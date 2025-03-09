from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'sys_event_logs_table'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'sys_event_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('level', sa.String(length=10), nullable=False),  # e.g., DEBUG, INFO
        sa.Column('thread_id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('entity_name', sa.String(), nullable=False),  # e.g., kafka.conn
        sa.Column('action', sa.String(), nullable=False)  # Log message
    )

def downgrade() -> None:
    """Drop sys_event_logs table."""
    op.drop_table('sys_event_logs')
