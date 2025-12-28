"""fix missing columns

Revision ID: f152d00b510a
Revises: e1b4c19ddaac
Create Date: 2025-12-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = 'f152d00b510a'
down_revision: Union[str, Sequence[str], None] = 'e1b4c19ddaac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    # Suppliers
    conn.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS current_balance NUMERIC(12, 2) DEFAULT 0.00"))
    conn.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(12, 2)"))
    conn.execute(text("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS payment_terms INTEGER DEFAULT 30"))
    
    # Returns
    conn.execute(text("ALTER TABLE return_details ADD COLUMN IF NOT EXISTS unit_price NUMERIC(12, 2) DEFAULT 0.00"))
    
    # Sale Payments
    conn.execute(text("ALTER TABLE sale_payments ADD COLUMN IF NOT EXISTS exchange_rate NUMERIC(14, 4) DEFAULT 1.0000"))

def downgrade() -> None:
    pass
