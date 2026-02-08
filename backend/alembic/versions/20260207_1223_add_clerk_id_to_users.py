"""add_clerk_id_to_users

Revision ID: 45b6d63030b6
Revises: 
Create Date: 2026-02-07 12:23:20.870805+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45b6d63030b6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add clerk_id column to users table
    op.add_column('users', sa.Column('clerk_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_users_clerk_id'), 'users', ['clerk_id'], unique=True)


def downgrade() -> None:
    # Remove clerk_id column from users table
    op.drop_index(op.f('ix_users_clerk_id'), table_name='users')
    op.drop_column('users', 'clerk_id')
