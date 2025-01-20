"""Revert password to TEXT

Revision ID: 30e810da3a5e
Revises: d8bd21d7e7b3
Create Date: 2025-01-20 15:55:20.427829

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '30e810da3a5e'
down_revision = 'd8bd21d7e7b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=postgresql.BYTEA(),
               type_=sa.Text(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.Text(),
               type_=postgresql.BYTEA(),
               existing_nullable=False)

    # ### end Alembic commands ###
