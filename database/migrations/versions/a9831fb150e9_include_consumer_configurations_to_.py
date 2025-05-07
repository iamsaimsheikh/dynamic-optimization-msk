"""include consumer configurations to kafka batch stats model

Revision ID: a9831fb150e9
Revises: 868fb5750e0e
Create Date: 2025-05-07 21:40:30.336561
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9831fb150e9'
down_revision: Union[str, None] = '868fb5750e0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add actual consumer configuration columns
    op.add_column('kafka_batch_stats', sa.Column('conf_fetch_max_bytes', sa.Integer(), nullable=True))
    op.add_column('kafka_batch_stats', sa.Column('conf_max_poll_records', sa.Integer(), nullable=True))
    op.add_column('kafka_batch_stats', sa.Column('conf_session_timeout_ms', sa.Integer(), nullable=True))
    op.add_column('kafka_batch_stats', sa.Column('conf_heartbeat_interval_ms', sa.Integer(), nullable=True))



def downgrade() -> None:
    # Remove consumer config columns
    op.drop_column('kafka_batch_stats', 'conf_heartbeat_interval_ms')
    op.drop_column('kafka_batch_stats', 'conf_session_timeout_ms')
    op.drop_column('kafka_batch_stats', 'conf_max_poll_records')
    op.drop_column('kafka_batch_stats', 'conf_fetch_max_bytes')

