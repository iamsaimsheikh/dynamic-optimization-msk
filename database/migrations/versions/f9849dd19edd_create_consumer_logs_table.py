"""Create consumer_logs table

Revision ID: 4fa9cef20b33
Revises: b0a71a231f90
Create Date: 2025-02-19 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4fa9cef20b33'
down_revision: Union[str, None] = 'b0a71a231f90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'consumer_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', postgresql.TIMESTAMP(), nullable=False),
        sa.Column('case_id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('consumer_id', sa.BigInteger(), nullable=False),
        sa.Column('batch_size', sa.Integer(), nullable=False),
        sa.Column('linger_ms', sa.Integer(), nullable=False),
        sa.Column('compression_type', sa.String(), nullable=False),
        sa.Column('max_request_size', sa.Integer(), nullable=False),
        sa.Column('acks', sa.String(), nullable=False),
        sa.Column('message_details', sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('consumer_logs')
