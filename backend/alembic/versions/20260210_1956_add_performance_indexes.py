"""add_performance_indexes

Revision ID: e84f3c1e7bed
Revises: da1c2b4bbc34
Create Date: 2026-02-10 19:56:57.718733+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e84f3c1e7bed'
down_revision: Union[str, None] = 'da1c2b4bbc34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes to improve query speed."""

    # Website indexes
    op.create_index(
        'ix_websites_domain',
        'websites',
        ['domain'],
        unique=False
    )
    op.create_index(
        'ix_websites_verified',
        'websites',
        ['verified'],
        unique=False
    )
    op.create_index(
        'ix_websites_created_at',
        'websites',
        ['created_at'],
        unique=False
    )

    # PageResult indexes
    op.create_index(
        'ix_page_results_url',
        'page_results',
        ['url'],
        unique=False,
        postgresql_ops={'url': 'text_pattern_ops'}  # For LIKE queries
    )
    op.create_index(
        'ix_page_results_seo_score',
        'page_results',
        ['seo_score'],
        unique=False
    )
    op.create_index(
        'ix_page_results_status_code',
        'page_results',
        ['status_code'],
        unique=False
    )
    # Composite index for efficient queries: "get all pages for crawl job, sorted by date"
    op.create_index(
        'ix_page_results_crawl_created',
        'page_results',
        ['crawl_job_id', 'created_at'],
        unique=False
    )

    # User indexes
    op.create_index(
        'ix_users_plan',
        'users',
        ['plan'],
        unique=False
    )

    # AIRecommendation indexes
    op.create_index(
        'ix_ai_recommendations_type',
        'ai_recommendations',
        ['recommendation_type'],
        unique=False
    )
    # Composite index for filtering: "get all recommendations for a crawl by status"
    op.create_index(
        'ix_ai_recommendations_crawl_status',
        'ai_recommendations',
        ['crawl_job_id', 'implementation_status'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""

    # AIRecommendation indexes
    op.drop_index('ix_ai_recommendations_crawl_status', table_name='ai_recommendations')
    op.drop_index('ix_ai_recommendations_type', table_name='ai_recommendations')

    # User indexes
    op.drop_index('ix_users_plan', table_name='users')

    # PageResult indexes
    op.drop_index('ix_page_results_crawl_created', table_name='page_results')
    op.drop_index('ix_page_results_status_code', table_name='page_results')
    op.drop_index('ix_page_results_seo_score', table_name='page_results')
    op.drop_index('ix_page_results_url', table_name='page_results')

    # Website indexes
    op.drop_index('ix_websites_created_at', table_name='websites')
    op.drop_index('ix_websites_verified', table_name='websites')
    op.drop_index('ix_websites_domain', table_name='websites')
