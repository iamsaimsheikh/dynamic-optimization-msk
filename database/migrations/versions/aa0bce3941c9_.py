"""

Revision ID: aa0bce3941c9
Revises: 9c6b276360d5
Create Date: 2025-04-18 03:12:11.231944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa0bce3941c9'
down_revision: Union[str, None] = '9c6b276360d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('checkpoint',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('last_checkpoint_timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkpoint_id'), 'checkpoint', ['id'], unique=False)
    op.add_column('consumer_logs', sa.Column('message_id', sa.String(), nullable=False))
    op.add_column('producer_logs', sa.Column('message_id', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('producer_logs', 'message_id')
    op.drop_column('consumer_logs', 'message_id')
    op.drop_index(op.f('ix_checkpoint_id'), table_name='checkpoint')
    op.drop_table('checkpoint')
    # ### end Alembic commands ###
