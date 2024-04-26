"""empty message

Revision ID: d76e56b9a0cf
Revises: c6d030ecc243
Create Date: 2024-04-26 13:34:03.126341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd76e56b9a0cf'
down_revision = 'c6d030ecc243'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('servings',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe', schema=None) as batch_op:
        batch_op.alter_column('servings',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('description',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###
