import pandas as pd
from sqlalchemy.orm import Session
from database.models.consumer_log_model import ConsumerLogModel
from database.models.producer_log_model import ProducerLogModel
from database.models.kafka_batch_stats_model import KafkaBatchStatsModel
from datetime import datetime
import uuid
import threading
import docker
import json
import time


class AnalyticsBuffer:
    def __init__(self, db: Session, length: int = 100, consumer_configs: dict = {}, consumer_stop_event: threading.Event = None):
        self.length = length
        self.db = db
        self.buffer = []
        self.lock = threading.Lock()
        self.docker_client = docker.from_env()
        self.consumer_configs = consumer_configs
        self.consumer_stop_event = consumer_stop_event  # Event to signal consumer finished

    def appendId(self, log_id: str):
        with self.lock:
            print(f"[DEBUG] Appending ID: {log_id}")
            self.buffer.append(log_id)
            if len(self.buffer) >= self.length:
                print(f"[DEBUG] Buffer reached {self.length}, triggering analytics")
                result = self.calculate_analytics()
                self.buffer = []
                return result

    def get_system_stats(self):
        # This method uses streaming stats like the original KafkaMonitor code.
        cpu_usages, mem_usages = [], []

        def fetch_container_stats(container_name):
            try:
                container = self.docker_client.containers.get(container_name)
                stats = container.stats(stream=False)

                cpu_stats = stats.get("cpu_stats", {})
                precpu_stats = stats.get("precpu_stats", {})

                cpu_usage = cpu_stats.get("cpu_usage", {})
                precpu_usage = precpu_stats.get("cpu_usage", {})

                total_usage = cpu_usage.get("total_usage")
                precpu_total_usage = precpu_usage.get("total_usage")

                system_cpu = cpu_stats.get("system_cpu_usage")
                precpu_system_cpu = precpu_stats.get("system_cpu_usage")

                if None in (total_usage, precpu_total_usage, system_cpu, precpu_system_cpu):
                    print(f"[WARN] Missing CPU usage data for {container_name}, skipping stats calculation")
                    return  # skip this container for now

                cpu_delta = total_usage - precpu_total_usage
                system_delta = system_cpu - precpu_system_cpu

                num_cpus = len(cpu_usage.get("percpu_usage", [])) or 1

                cpu_percent = ((cpu_delta / system_delta) * num_cpus * 100.0) if system_delta > 0 else 0.0

                mem_usage = stats.get("memory_stats", {}).get("usage", 0)
                cache = stats.get("memory_stats", {}).get("stats", {}).get("cache", 0)
                actual_usage = mem_usage - cache
                mem_limit = stats.get("memory_stats", {}).get("limit", 1)

                mem_percent = ((actual_usage / mem_limit) * 100.0) if mem_limit > 0 else 0.0

                cpu_usages.append(cpu_percent)
                mem_usages.append(mem_percent)

            except Exception as e:
                print(f"[ERROR] Failed to get stats for {container_name}: {e}")


        threads = []
        for name in ["kafka1", "kafka2", "kafka3"]:
            thread = threading.Thread(target=fetch_container_stats, args=(name,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        avg_cpu = round(sum(cpu_usages) / len(cpu_usages), 2) if cpu_usages else 0.0
        avg_ram = round(sum(mem_usages) / len(mem_usages), 2) if mem_usages else 0.0

        return avg_cpu, avg_ram

    def calculate_analytics(self):
        print("[DEBUG] Starting analytics calculation...")
        avg_cpu, avg_ram = self.get_system_stats()

        consumer_logs = (
            self.db.query(ConsumerLogModel)
            .filter(
                ConsumerLogModel.is_analytics_processed.is_(False),
                ConsumerLogModel.message_id.isnot(None),
                ConsumerLogModel.message_id != "None",
            )
            .order_by(ConsumerLogModel.timestamp.asc())
            .limit(self.length)
            .all()
        )

        message_ids = [log.message_id for log in consumer_logs]
        print(f"Consumer Message Ids: {message_ids}")

        producer_logs = (
            self.db.query(ProducerLogModel)
            .filter(
                ProducerLogModel.message_id.in_(message_ids),
                ProducerLogModel.is_analytics_processed.is_(False),
            )
            .all()
        )

        p_ids = [log.message_id for log in producer_logs]
        print(f"Producer Message Ids: {p_ids}")

        if not producer_logs or not consumer_logs:
            print("[DEBUG] No new producer or consumer logs found.")
            for log in consumer_logs:
                print(log.message_id)
                log.is_analytics_processed = True

            self.db.commit()
            
            # Signal consumer stop event if set, since no more data to process
            if self.consumer_stop_event:
                print("[DEBUG] Setting consumer_stop_event - no new logs.")
                self.consumer_stop_event.set()

            return None

        producer_df = pd.DataFrame([p.__dict__ for p in producer_logs])
        consumer_df = pd.DataFrame([c.__dict__ for c in consumer_logs])

        # Drop internal SQLAlchemy state
        for df in [producer_df, consumer_df]:
            df.drop(columns=["_sa_instance_state"], errors="ignore", inplace=True)

        # Remove duplicate message IDs and sort by timestamp
        producer_df.sort_values("timestamp", ascending=False, inplace=True)
        producer_df.drop_duplicates(subset=["message_id"], inplace=True)

        consumer_df.sort_values("timestamp", ascending=False, inplace=True)
        consumer_df.drop_duplicates(subset=["message_id"], inplace=True)

        # Merge by message_id to calculate latency
        merged_df = pd.merge(
            producer_df,
            consumer_df,
            on="message_id",
            how="inner",
            suffixes=("_producer", "_consumer"),
        )

        merged_df.rename(
            columns={
                "timestamp_producer": "producer_timestamp",
                "timestamp_consumer": "consumer_timestamp",
            },
            inplace=True,
        )

        if merged_df.empty:
            print("[DEBUG] Merged DataFrame is empty. No matching message_id found.")
            if self.consumer_stop_event:
                print("[DEBUG] Setting consumer_stop_event - empty merged dataframe.")
                self.consumer_stop_event.set()
            return None

        # ✅ Latency in milliseconds
        # Adjust latency: subtract 1s (1000ms) from each message's latency
        merged_df["latency_ms"] = (
            (merged_df["consumer_timestamp"] - merged_df["producer_timestamp"])
            .dt.total_seconds() * 1000
        ) - 1000  # Adjust for consumer 1s sleep

        # Total messages
        total_messages = len(merged_df)

        # Average latency (ms)
        average_latency_ms = merged_df["latency_ms"].mean()

        # Adjusted time window: subtract 2s per message (1s from producer + 1s from consumer)
        raw_time_window = (merged_df["consumer_timestamp"].max() - merged_df["producer_timestamp"].min()).total_seconds()
        adjusted_time_window_sec = max(raw_time_window, 0.1)  # Avoid divide-by-zero

        # Average throughput (messages per second)
        average_throughput_mps = total_messages / adjusted_time_window_sec

        # Cost calculations
        msk_uptime_cost_usd = 0.21 / 3600 * raw_time_window  # Billing is based on real elapsed time
        cost_per_message_usd = 0.01 / 1_000_000
        total_cost_usd = msk_uptime_cost_usd + (total_messages * cost_per_message_usd)

        print("Adjusted metrics calculated")
        print(self.consumer_configs)


        stats_model = KafkaBatchStatsModel(
            id=uuid.uuid4(),
            batch_size=total_messages,
            average_latency_ms=round(average_latency_ms, 2),
            average_throughput_mps=round(average_throughput_mps, 4),
            conf_linger_ms=round(merged_df["linger_ms_producer"].mean(), 2),
            conf_max_request_size=round(
                merged_df["max_request_size_producer"].mean(), 2
            ),
            conf_acks=merged_df["acks_producer"].mode().iloc[0],
            conf_batch_size=round(
                merged_df["batch_size_producer"].mean(), 2
            ),
            total_messages=total_messages,
            total_cost_usd=round(total_cost_usd, 5),
            cost_per_message_usd=round(cost_per_message_usd, 8),
            msk_uptime_cost_usd=round(msk_uptime_cost_usd, 5),
            avg_cpu_usage=avg_cpu,
            avg_ram_usage=avg_ram,
            conf_fetch_max_bytes= self.consumer_configs['fetch_max_bytes'],
            conf_max_poll_records = self.consumer_configs['max_poll_records'],
            conf_session_timeout_ms = self.consumer_configs['session_timeout_ms'],
            conf_heartbeat_interval_ms = self.consumer_configs['heartbeat_interval_ms'],
            created_at=datetime.utcnow(),
        )
        
        print(stats_model)

        try:
            self.db.add(stats_model)

            for log in producer_logs:
                log.is_analytics_processed = True
            for log in consumer_logs:
                log.is_analytics_processed = True

            self.db.commit()
            print("[DEBUG] KafkaBatchStatsModel committed successfully.")
            
            # Signal consumer_stop_event after successful commit
            if self.consumer_stop_event:
                print("[DEBUG] Setting consumer_stop_event - analytics complete.")
                self.consumer_stop_event.set()
            
            return stats_model
        except Exception as e:
            self.db.rollback()
            print(f"[ERROR] Failed to commit analytics: {e}")
            
            # You may want to decide whether to set or clear the event here
            return None
