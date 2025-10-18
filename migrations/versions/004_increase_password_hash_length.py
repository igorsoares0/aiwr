"""Increase password_hash length to 256

Revision ID: 004
Revises: 003
Create Date: 2025-10-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Increase password_hash column length from 128 to 256
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(128),
                    type_=sa.String(256),
                    existing_nullable=True)


def downgrade():
    # Revert password_hash column length back to 128
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(256),
                    type_=sa.String(128),
                    existing_nullable=True)
