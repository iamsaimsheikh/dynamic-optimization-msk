"""alter producer and consumer table int datatype to bigint

Revision ID: 7c5beec44136
Revises: 1bcf423436a9
Create Date: 2025-02-20 00:39:36.110581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c5beec44136'
down_revision: Union[str, None] = '1bcf423436a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('producer_logs', 'case_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)
                    
    op.alter_column('consumer_logs', 'case_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)


def downgrade() -> None:
    pass
