import pandas as pd
from sqlalchemy.orm import Session
from database.models.consumer_log_model import ConsumerLogModel
from database.models.producer_log_model import ProducerLogModel
from database.models.kafka_batch_stats_model import KafkaBatchStatsModel
from datetime import datetime
import uuid
import threading
import docker


class AnalyticsBuffer:
    def __init__(self, db: Session, length: int = 100, consumer_configs: list = {}):
        self.length = length
        self.db = db
        self.buffer = []
        self.lock = threading.Lock()
        self.docker_client = docker.from_env()
        self.consumer_configs = consumer_configs

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
        # Get stats for Kafka containers asynchronously
        cpu_usages = []
        mem_usages = []

        def fetch_container_stats(container_name):
            try:
                container = self.docker_client.containers.get(container_name)
                stats = container.stats(stream=False)

                cpu_delta = (
                    stats["cpu_stats"]["cpu_usage"]["total_usage"]
                    - stats["precpu_stats"]["cpu_usage"]["total_usage"]
                )
                system_delta = (
                    stats["cpu_stats"]["system_cpu_usage"]
                    - stats["precpu_stats"]["system_cpu_usage"]
                )
                num_cpus = (
                    len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [])) or 1
                )

                cpu_percent = (
                    (cpu_delta / system_delta) * num_cpus * 100.0
                    if system_delta > 0
                    else 0.0
                )

                mem_usage = stats["memory_stats"].get("usage", 0)
                cache = stats["memory_stats"].get("stats", {}).get("cache", 0)
                actual_usage = mem_usage - cache
                mem_limit = stats["memory_stats"].get("limit", 1)

                mem_percent = (
                    (actual_usage / mem_limit) * 100.0 if mem_limit > 0 else 0.0
                )

                cpu_usages.append(cpu_percent)
                mem_usages.append(mem_percent)

            except Exception as e:
                print(f"[ERROR] Failed to get stats for {container_name}: {e}")

        # Run the stats fetching in parallel for each container
        threads = []
        for container_name in ["kafka1", "kafka2", "kafka3"]:
            thread = threading.Thread(
                target=fetch_container_stats, args=(container_name,)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to finish
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
        print(message_ids)

        producer_logs = (
            self.db.query(ProducerLogModel)
            .filter(
                ProducerLogModel.message_id.in_(message_ids),
                ProducerLogModel.is_analytics_processed.is_(False),
            )
            .all()
        )

        p_ids = [log.message_id for log in producer_logs]
        print(p_ids)

        if not producer_logs or not consumer_logs:
            print("[DEBUG] No new producer or consumer logs found.")
            for log in consumer_logs:
                print(log.message_id)
                log.is_analytics_processed = True

            self.db.commit()
            return None

        producer_df = pd.DataFrame([p.__dict__ for p in producer_logs])
        consumer_df = pd.DataFrame([c.__dict__ for c in consumer_logs])

        for df in [producer_df, consumer_df]:
            df.drop(columns=["_sa_instance_state"], errors="ignore", inplace=True)

        producer_df.sort_values("timestamp", ascending=False, inplace=True)
        producer_df = producer_df.drop_duplicates(subset=["message_id"])

        consumer_df.sort_values("timestamp", ascending=False, inplace=True)
        consumer_df = consumer_df.drop_duplicates(subset=["message_id"])

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
            return None

        merged_df["latency_ms"] = (
            merged_df["consumer_timestamp"] - merged_df["producer_timestamp"]
        ).dt.total_seconds() * 1000

        total_messages = len(merged_df)
        avg_latency = merged_df["latency_ms"].mean()
        start_time = merged_df["producer_timestamp"].min()
        end_time = merged_df["consumer_timestamp"].max()
        time_window_sec = (end_time - start_time).total_seconds() or 1
        throughput_mps = total_messages / time_window_sec

        uptime_cost_usd = 0.21 / 3600 * time_window_sec
        per_message_cost_usd = 0.01 / 1_000_000
        total_cost_usd = uptime_cost_usd + (total_messages * per_message_cost_usd)
        
        print("here")
        print(self.consumer_configs)

        stats_model = KafkaBatchStatsModel(
            id=uuid.uuid4(),
            batch_size=total_messages,
            average_latency_ms=round(avg_latency, 2),
            average_throughput_mps=round(throughput_mps, 4),
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
            cost_per_message_usd=round(per_message_cost_usd, 8),
            msk_uptime_cost_usd=round(uptime_cost_usd, 5),
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
            return stats_model
        except Exception as e:
            self.db.rollback()
            print(f"[ERROR] Failed to commit analytics: {e}")
            return None
