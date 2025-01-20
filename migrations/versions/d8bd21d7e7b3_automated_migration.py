"""Automated migration

Revision ID: d8bd21d7e7b3
Revises: 2b22697ae11b
Create Date: 2025-01-20 15:16:08.447412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8bd21d7e7b3'
down_revision = '2b22697ae11b'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.LargeBinary(),
               type_=sa.TEXT(),
               existing_nullable=False,
               postgresql_using="password::text")  # Reverte para texto


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.TEXT(),
               type_=sa.LargeBinary(),
               existing_nullable=False,
               postgresql_using="password::bytea")  # Reverte para binário

    # ### end Alembic commands ###
