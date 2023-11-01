"""empty message

Revision ID: e30e569886f7
Revises: 
Create Date: 2023-11-01 15:48:30.134196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e30e569886f7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medicine',
    sa.Column('MED_ID', sa.Text(), nullable=False),
    sa.Column('Name', sa.Text(), nullable=False),
    sa.Column('ThubLink', sa.Text(), nullable=False),
    sa.Column('Effect_Type', sa.Text(), nullable=False),
    sa.Column('Effect', sa.Text(), nullable=False),
    sa.Column('Usage_Type', sa.Text(), nullable=False),
    sa.Column('Usage', sa.Text(), nullable=False),
    sa.Column('Caution_Type', sa.Text(), nullable=False),
    sa.Column('Caution', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('MED_ID')
    )
    op.create_table('user',
    sa.Column('USR_ID', sa.Text(), nullable=False),
    sa.Column('Password', sa.Text(), nullable=False),
    sa.Column('Name', sa.Text(), nullable=False),
    sa.Column('Birthday', sa.DateTime(), nullable=False),
    sa.Column('Gender', sa.Text(), nullable=False),
    sa.Column('Phone', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('USR_ID')
    )
    op.drop_table('MEDICINE')
    op.drop_table('USER')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('USER',
    sa.Column('ID', sa.TEXT(), nullable=True),
    sa.Column('Password', sa.TEXT(), nullable=True),
    sa.Column('Name', sa.TEXT(), nullable=True),
    sa.Column('Birthday', sa.DATE(), nullable=True),
    sa.Column('Gender', sa.VARCHAR(length=2), nullable=True),
    sa.Column('Phone', sa.VARCHAR(length=11), nullable=True)
    )
    op.create_table('MEDICINE',
    sa.Column('ID', sa.INTEGER(), nullable=True),
    sa.Column('Name', sa.TEXT(), nullable=True),
    sa.Column('ThubLink', sa.TEXT(), nullable=True),
    sa.Column('Effect_Type', sa.TEXT(), nullable=True),
    sa.Column('Effect', sa.TEXT(), nullable=True),
    sa.Column('Usage_Type', sa.TEXT(), nullable=True),
    sa.Column('Usage', sa.TEXT(), nullable=True),
    sa.Column('Caution_Type', sa.TEXT(), nullable=True),
    sa.Column('Caution', sa.TEXT(), nullable=True)
    )
    op.drop_table('user')
    op.drop_table('medicine')
    # ### end Alembic commands ###
