"""Add subscription tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add subscription fields to users table
    op.add_column('users', sa.Column('subscription_status', sa.String(20), nullable=False, server_default='trial'))
    op.add_column('users', sa.Column('subscription_plan', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('trial_ends_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('subscription_ends_at', sa.DateTime(), nullable=True))
    
    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(100), nullable=False),
        sa.Column('stripe_price_id', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('plan_type', sa.String(20), nullable=False),
        sa.Column('current_period_start', sa.DateTime(), nullable=False),
        sa.Column('current_period_end', sa.DateTime(), nullable=False),
        sa.Column('trial_start', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('idx_subscriptions_stripe_id', 'subscriptions', ['stripe_subscription_id'], unique=True)
    
    # Create payment_events table for audit trail
    op.create_table('payment_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('stripe_event_id', sa.String(100), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_payment_events_stripe_id', 'payment_events', ['stripe_event_id'], unique=True)
    op.create_index('idx_payment_events_user_id', 'payment_events', ['user_id'])
    op.create_index('idx_payment_events_created_at', 'payment_events', ['created_at'])


def downgrade():
    # Drop tables
    op.drop_table('payment_events')
    op.drop_table('subscriptions')
    
    # Remove columns from users table
    op.drop_column('users', 'subscription_ends_at')
    op.drop_column('users', 'trial_ends_at')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_plan')
    op.drop_column('users', 'subscription_status')