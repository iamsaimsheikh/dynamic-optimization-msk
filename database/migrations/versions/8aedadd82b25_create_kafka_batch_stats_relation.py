"""create-kafka-batch-stats-relation

Revision ID: 8aedadd82b25
Revises: 4123971cb947
Create Date: 2025-04-19 22:22:57.814749
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision: str = '8aedadd82b25'
down_revision: Union[str, None] = '4123971cb947'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'kafka_batch_stats',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('batch_size', sa.Integer(), nullable=True),
        sa.Column('average_latency_ms', sa.Float(), nullable=True),
        sa.Column('average_throughput_mps', sa.Float(), nullable=True),

        sa.Column('average_linger_ms', sa.Float(), nullable=True),
        sa.Column('average_max_request_size', sa.Float(), nullable=True),
        sa.Column('average_acks', sa.Float(), nullable=True),
        sa.Column('average_producer_batch_size', sa.Float(), nullable=True),

        sa.Column('total_messages', sa.Integer(), nullable=True),
        sa.Column('total_cost_usd', sa.Float(), nullable=True),
        sa.Column('cost_per_message_usd', sa.Float(), nullable=True),
        sa.Column('msk_uptime_cost_usd', sa.Float(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('kafka_batch_stats')
