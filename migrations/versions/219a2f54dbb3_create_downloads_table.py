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
    op.create_table(
        'downloads',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('video_id', sa.Integer, sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('result', sa.String(length=10), nullable=False, server_default='FAKE'),
        sa.Column('confidence', sa.Float, nullable=False, server_default='0')
    )

def downgrade() -> None:
    op.drop_table('downloads')
