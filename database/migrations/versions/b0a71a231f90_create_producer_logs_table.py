from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b0a71a231f90'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.create_table(
        'producer_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),  
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('producer_id', sa.Integer(), nullable=False),
        sa.Column('batch_size', sa.Integer(), nullable=False),  
        sa.Column('linger_ms', sa.Integer(), nullable=False),  
        sa.Column('compression_type', sa.String(), nullable=False),  
        sa.Column('max_request_size', sa.Integer(), nullable=False),  
        sa.Column('acks', sa.String(), nullable=False),  
        sa.Column('message_details', sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('producer_logs')
