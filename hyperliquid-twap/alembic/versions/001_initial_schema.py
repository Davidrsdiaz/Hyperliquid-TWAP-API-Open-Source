"""Initial schema for TWAP tracking

Revision ID: 001
Revises: 
Create Date: 2025-11-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create twap_status and etl_s3_ingest_log tables with indexes."""
    
    # Create twap_status table
    op.create_table(
        'twap_status',
        sa.Column('twap_id', sa.Text(), nullable=False),
        sa.Column('wallet', sa.Text(), nullable=False),
        sa.Column('ts', postgresql.TIMESTAMPTZ(), nullable=False),
        sa.Column('asset', sa.Text(), nullable=True),
        sa.Column('side', sa.Text(), nullable=True),
        sa.Column('size_requested', sa.Numeric(), nullable=True),
        sa.Column('size_executed', sa.Numeric(), nullable=True),
        sa.Column('notional_executed', sa.Numeric(), nullable=True),
        sa.Column('status', sa.Text(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('s3_object_key', sa.Text(), nullable=False),
        sa.Column('raw_payload', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('inserted_at', postgresql.TIMESTAMPTZ(), nullable=False),
        sa.PrimaryKeyConstraint('twap_id', 'wallet', 'ts')
    )
    
    # Create indexes on twap_status
    op.create_index('twap_status_wallet_ts_idx', 'twap_status', ['wallet', 'ts'])
    op.create_index('twap_status_twap_id_idx', 'twap_status', ['twap_id'])
    op.create_index('twap_status_asset_idx', 'twap_status', ['asset'])
    
    # Create etl_s3_ingest_log table
    op.create_table(
        'etl_s3_ingest_log',
        sa.Column('s3_object_key', sa.Text(), nullable=False),
        sa.Column('last_modified', postgresql.TIMESTAMPTZ(), nullable=False),
        sa.Column('rows_ingested', sa.Integer(), nullable=True),
        sa.Column('error_text', sa.Text(), nullable=True),
        sa.Column('ingested_at', postgresql.TIMESTAMPTZ(), nullable=False),
        sa.PrimaryKeyConstraint('s3_object_key')
    )


def downgrade() -> None:
    """Drop all tables and indexes."""
    op.drop_table('etl_s3_ingest_log')
    op.drop_index('twap_status_asset_idx', table_name='twap_status')
    op.drop_index('twap_status_twap_id_idx', table_name='twap_status')
    op.drop_index('twap_status_wallet_ts_idx', table_name='twap_status')
    op.drop_table('twap_status')
