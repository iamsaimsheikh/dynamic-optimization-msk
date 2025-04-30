"""fix columns names for table kafka_batch_stats

Revision ID: 868fb5750e0e
Revises: 8547da822391
Create Date: 2025-04-30 22:49:37.177705
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '868fb5750e0e'
down_revision: Union[str, None] = '8547da822391'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('kafka_batch_stats', 'average_linger_ms', new_column_name='conf_linger_ms')
    op.alter_column('kafka_batch_stats', 'average_max_request_size', new_column_name='conf_max_request_size')
    op.alter_column('kafka_batch_stats', 'average_acks', new_column_name='conf_acks')
    op.alter_column('kafka_batch_stats', 'average_producer_batch_size', new_column_name='conf_batch_size')


def downgrade() -> None:
    op.alter_column('kafka_batch_stats', 'conf_linger_ms', new_column_name='average_linger_ms')
    op.alter_column('kafka_batch_stats', 'conf_max_request_size', new_column_name='average_max_request_size')
    op.alter_column('kafka_batch_stats', 'conf_acks', new_column_name='average_acks')
    op.alter_column('kafka_batch_stats', 'conf_batch_size', new_column_name='average_producer_batch_size')
