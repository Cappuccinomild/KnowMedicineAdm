"""empty message

Revision ID: ee0b3906f85a
Revises: 
Create Date: 2023-11-02 11:51:44.333315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee0b3906f85a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('check_log',
    sa.Column('check_log_id', sa.String(length=12), nullable=False),
    sa.Column('user_id', sa.String(length=12), nullable=False),
    sa.Column('med_id', sa.String(length=12), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('rate', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('check_log_id')
    )
    op.create_table('id_seq',
    sa.Column('ID', sa.String(length=3), nullable=False),
    sa.Column('seq', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('ID')
    )
    op.create_table('medicine',
    sa.Column('med_id', sa.String(length=12), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('thubLink', sa.String(length=255), nullable=False),
    sa.Column('effect_type', sa.String(length=2), nullable=False),
    sa.Column('effect', sa.Text(), nullable=False),
    sa.Column('usage_type', sa.String(length=2), nullable=False),
    sa.Column('usage', sa.Text(), nullable=False),
    sa.Column('caution_type', sa.String(length=2), nullable=False),
    sa.Column('caution', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('med_id')
    )
    op.create_table('user',
    sa.Column('user_id', sa.String(length=12), nullable=False),
    sa.Column('auth', sa.String(length=20), nullable=False),
    sa.Column('password', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('birthday', sa.DateTime(), nullable=False),
    sa.Column('gender', sa.String(length=2), nullable=False),
    sa.Column('phone', sa.String(length=17), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('user_log',
    sa.Column('user_log_id', sa.String(length=12), nullable=False),
    sa.Column('user_id', sa.String(length=12), nullable=False),
    sa.Column('med_id', sa.String(length=12), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('rate', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('user_log_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_log')
    op.drop_table('user')
    op.drop_table('medicine')
    op.drop_table('id_seq')
    op.drop_table('check_log')
    # ### end Alembic commands ###
