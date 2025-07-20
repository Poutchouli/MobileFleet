"""Add language preference to users table

Revision ID: add_language_preference
Revises: e4822e57f6da
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_language_preference'
down_revision = 'e4822e57f6da'
branch_labels = None
depends_on = None

def upgrade():
    """Add language_preference column to users table"""
    op.add_column('users', sa.Column('language_preference', sa.String(5), nullable=True, default='en'))
    
    # Set default language preference for existing users
    op.execute("UPDATE users SET language_preference = 'en' WHERE language_preference IS NULL")

def downgrade():
    """Remove language_preference column from users table"""
    op.drop_column('users', 'language_preference')
