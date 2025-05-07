from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '8547da822391'
down_revision: Union[str, None] = '7b10ffe458a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('kafka_batch_stats', sa.Column('avg_cpu_usage', sa.Float(), nullable=True))
    op.add_column('kafka_batch_stats', sa.Column('avg_ram_usage', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('kafka_batch_stats', 'avg_cpu_usage')
    op.drop_column('kafka_batch_stats', 'avg_ram_usage')