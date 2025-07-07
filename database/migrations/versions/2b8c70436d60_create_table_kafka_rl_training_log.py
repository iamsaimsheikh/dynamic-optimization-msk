"""create table kafka_rl_training_log

Revision ID: 2b8c70436d60
Revises: a9831fb150e9
Create Date: 2025-05-24 15:56:25.578289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2b8c70436d60'
down_revision: Union[str, None] = 'a9831fb150e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create extension pgcrypto for gen_random_uuid() if not exists
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    
    # Create kafka_rl_training_log table
    op.create_table(
        'kafka_rl_training_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('episode', sa.Integer, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        
        # Config parameters
        sa.Column('conf_linger_ms', sa.Integer, nullable=False),
        sa.Column('conf_max_request_size', sa.Integer, nullable=False),
        sa.Column('conf_fetch_max_bytes', sa.Integer, nullable=False),
        sa.Column('conf_max_poll_records', sa.Integer, nullable=False),
        sa.Column('conf_session_timeout_ms', sa.Integer, nullable=False),
        sa.Column('conf_heartbeat_interval_ms', sa.Integer, nullable=False),

        # Performance metrics
        sa.Column('average_throughput_mps', sa.Float, nullable=False),
        sa.Column('average_latency_ms', sa.Float, nullable=False),
        sa.Column('total_cost_usd', sa.Float, nullable=False),
        sa.Column('batch_size', sa.Integer, nullable=False),

        # RL info
        sa.Column('reward', sa.Float, nullable=False),
        sa.Column('action_taken', sa.Integer, nullable=False),

        # Next config after action
        sa.Column('next_conf_linger_ms', sa.Integer, nullable=False),
        sa.Column('next_conf_max_request_size', sa.Integer, nullable=False),
        sa.Column('next_conf_fetch_max_bytes', sa.Integer, nullable=False),
        sa.Column('next_conf_max_poll_records', sa.Integer, nullable=False),
        sa.Column('next_conf_session_timeout_ms', sa.Integer, nullable=False),
        sa.Column('next_conf_heartbeat_interval_ms', sa.Integer, nullable=False),

        sa.Column('loss', sa.Float, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('kafka_rl_training_log')
