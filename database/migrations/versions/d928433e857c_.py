"""empty message

Revision ID: d928433e857c
Revises: d07d6a21143c, 4fa9cef20b33
Create Date: 2025-02-20 00:32:58.341025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd928433e857c'
down_revision: Union[str, None] = ('d07d6a21143c', '4fa9cef20b33')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
