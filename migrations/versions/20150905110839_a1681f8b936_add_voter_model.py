"""Add Voter model.

Revision ID: a1681f8b936
Revises: 5ab6b37da4d1
Create Date: 2015-09-05 11:08:39.879641

"""

# revision identifiers, used by Alembic.
revision = 'a1681f8b936'
down_revision = '5ab6b37da4d1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('voter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('voter_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['voter_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'user', sa.Column('voters_count', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'user', 'voters_count')
    op.drop_table('voter')
    ### end Alembic commands ###