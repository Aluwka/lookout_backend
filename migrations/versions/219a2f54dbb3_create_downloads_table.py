"""Create downloads table

Revision ID: 219a2f54dbb3
Revises: 7d6d9ebd06a1
Create Date: 2025-05-08 02:02:26.256797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '219a2f54dbb3'
down_revision: Union[str, None] = '7d6d9ebd06a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
