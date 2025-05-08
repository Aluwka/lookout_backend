"""Make file_name not null

Revision ID: 7d6d9ebd06a1
Revises: f7e37931c1e7
Create Date: 2025-05-08 01:25:21.246211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d6d9ebd06a1'
down_revision: Union[str, None] = 'f7e37931c1e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
