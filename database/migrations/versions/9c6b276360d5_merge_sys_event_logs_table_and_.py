"""merge sys_event_logs_table and 7c5beec44136

Revision ID: 9c6b276360d5
Revises: sys_event_logs_table, 7c5beec44136
Create Date: 2025-04-18 03:11:55.410700
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c6b276360d5'
down_revision: Union[str, None] = ('sys_event_logs_table', '7c5beec44136')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('consumer_logs', sa.Column('message_id', sa.String(length=255), nullable=True))
    op.add_column('producer_logs', sa.Column('message_id', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('consumer_logs', 'message_id')
    op.drop_column('producer_logs', 'message_id')
