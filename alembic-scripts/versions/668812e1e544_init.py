"""init

Revision ID: 668812e1e544
Revises: 
Create Date: 2022-01-25 10:12:37.093816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '668812e1e544'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'metric_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__metric_users')),
        sa.UniqueConstraint('id', name=op.f('uq__metric_users__id')),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(length=40), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__users')),
        sa.UniqueConstraint('email', name=op.f('uq__users__email')),
        sa.UniqueConstraint('id', name=op.f('uq__users__id')),
        sa.UniqueConstraint('login', name=op.f('uq__users__login')),
    )
    op.create_table(
        'jwt',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk__jwt__user_id__users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__jwt')),
        sa.UniqueConstraint('id', name=op.f('uq__jwt__id')),
    )
    op.create_table(
        'logins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('info', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk__logins__user_id__users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__logins')),
        sa.UniqueConstraint('id', name=op.f('uq__logins__id')),
    )
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['metric_users.id'], name=op.f('fk__metrics__user_id__metric_users'), ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__metrics')),
        sa.UniqueConstraint('id', name=op.f('uq__metrics__id')),
        sa.UniqueConstraint('metric_name', name=op.f('uq__metrics__metric_name')),
        sa.UniqueConstraint('user_id', 'metric_name', name='metric_pk'),
    )
    op.create_table(
        'metric_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_id', sa.Integer(), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ['metric_id'], ['metrics.id'], name=op.f('fk__metric_data__metric_id__metrics'), ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__metric_data')),
        sa.UniqueConstraint('id', name=op.f('uq__metric_data__id')),
        sa.UniqueConstraint('metric_id', 'metric_date', name='metric_data_pk'),
    )
    op.create_table(
        'metric_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('metric_first', sa.Integer(), nullable=False),
        sa.Column('metric_second', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ['metric_first'], ['metrics.id'], name=op.f('fk__metric_results__metric_first__metrics'), ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['metric_second'],
            ['metrics.id'],
            name=op.f('fk__metric_results__metric_second__metrics'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['metric_users.id'], name=op.f('fk__metric_results__user_id__metric_users'), ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__metric_results')),
        sa.UniqueConstraint('id', name=op.f('uq__metric_results__id')),
        sa.UniqueConstraint('user_id', 'metric_first', 'metric_second', name='metric_result_pk'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('metric_results')
    op.drop_table('metric_data')
    op.drop_table('metrics')
    op.drop_table('logins')
    op.drop_table('jwt')
    op.drop_table('users')
    op.drop_table('metric_users')
    # ### end Alembic commands ###
