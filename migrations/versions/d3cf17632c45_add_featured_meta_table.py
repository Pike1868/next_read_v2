"""Add featured_meta table

Revision ID: d3cf17632c45
Revises: 1810f2fb5317
Create Date: 2025-01-04 16:38:03.501724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3cf17632c45'
down_revision = '1810f2fb5317'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('featured_meta',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('featured_meta')
    # ### end Alembic commands ###
