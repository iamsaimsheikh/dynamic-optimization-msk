from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bcf423436a9'
down_revision = 'd928433e857c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('producer_logs', 'producer_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(),
                    existing_nullable=False)
                    
    op.alter_column('consumer_logs', 'consumer_id',
                    existing_type=sa.Integer(),
                    type_=sa.String(),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('producer_logs', 'producer_id',
                    existing_type=sa.String(),
                    type_=sa.Integer(),
                    existing_nullable=False)
                    
    op.alter_column('consumer_logs', 'consumer_id',
                    existing_type=sa.String(),
                    type_=sa.Integer(),
                    existing_nullable=False)
