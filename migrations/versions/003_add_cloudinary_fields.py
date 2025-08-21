"""Add Cloudinary fields to Document model

Revision ID: 003
Revises: 002
Create Date: 2025-08-20 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add Cloudinary fields to documents table
    op.add_column('documents', sa.Column('cloudinary_public_id', sa.String(length=255), nullable=True))
    op.add_column('documents', sa.Column('cloudinary_url', sa.String(length=500), nullable=True))
    op.add_column('documents', sa.Column('cloudinary_secure_url', sa.String(length=500), nullable=True))
    
    # Make upload_path nullable for Cloudinary compatibility
    op.alter_column('documents', 'upload_path', nullable=True)


def downgrade():
    # Make upload_path not nullable again
    op.alter_column('documents', 'upload_path', nullable=False)
    
    # Remove Cloudinary fields from documents table
    op.drop_column('documents', 'cloudinary_secure_url')
    op.drop_column('documents', 'cloudinary_url')
    op.drop_column('documents', 'cloudinary_public_id')