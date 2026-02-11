"""add_readability_to_page_results

Revision ID: da1c2b4bbc34
Revises: 822401c8462f
Create Date: 2026-02-10 19:15:54.961553+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da1c2b4bbc34'
down_revision: Union[str, None] = '822401c8462f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add readability_score column
    op.add_column('page_results', sa.Column('readability_score', sa.Float(), nullable=True))
    # Add readability_grade column
    op.add_column('page_results', sa.Column('readability_grade', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove readability columns
    op.drop_column('page_results', 'readability_grade')
    op.drop_column('page_results', 'readability_score')
