"""Add cost_price to product_units

Revision ID: e4c79bc471b0
Revises: 20c0ded2b729
Create Date: 2025-12-22 10:51:51.989493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4c79bc471b0'
down_revision: Union[str, Sequence[str], None] = '20c0ded2b729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cost_price column to product_units table."""
    # Safe add column
    op.execute("ALTER TABLE product_units ADD COLUMN IF NOT EXISTS cost_price NUMERIC(14, 4)")


def downgrade() -> None:
    """Remove cost_price column from product_units table."""
    op.drop_column('product_units', 'cost_price')
