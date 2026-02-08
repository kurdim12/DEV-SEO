"""add_ai_recommendations_table

Revision ID: ceedc4c3fc00
Revises: 45b6d63030b6
Create Date: 2026-02-07 16:03:55.988288+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ceedc4c3fc00'
down_revision: Union[str, None] = '45b6d63030b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ai_recommendations table
    op.create_table(
        'ai_recommendations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('crawl_job_id', sa.UUID(), nullable=False),
        sa.Column('page_result_id', sa.UUID(), nullable=True),
        sa.Column('recommendation_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('ai_generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('implementation_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['crawl_job_id'], ['crawl_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['page_result_id'], ['page_results.id'], ondelete='CASCADE'),
    )

    # Create indexes for better query performance
    op.create_index('ix_ai_recommendations_crawl_job_id', 'ai_recommendations', ['crawl_job_id'])
    op.create_index('ix_ai_recommendations_page_result_id', 'ai_recommendations', ['page_result_id'])
    op.create_index('ix_ai_recommendations_priority', 'ai_recommendations', ['priority'])
    op.create_index('ix_ai_recommendations_implementation_status', 'ai_recommendations', ['implementation_status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_ai_recommendations_implementation_status', table_name='ai_recommendations')
    op.drop_index('ix_ai_recommendations_priority', table_name='ai_recommendations')
    op.drop_index('ix_ai_recommendations_page_result_id', table_name='ai_recommendations')
    op.drop_index('ix_ai_recommendations_crawl_job_id', table_name='ai_recommendations')

    # Drop table
    op.drop_table('ai_recommendations')
