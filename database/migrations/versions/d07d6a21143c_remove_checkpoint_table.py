"""remove checkpoint table

Revision ID: d07d6a21143c
Revises: b0a71a231f90
Create Date: 2025-02-19 13:52:35.801371

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd07d6a21143c'
down_revision: Union[str, None] = 'b0a71a231f90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('checkpoint')
    # ### end Alembic commands ###

