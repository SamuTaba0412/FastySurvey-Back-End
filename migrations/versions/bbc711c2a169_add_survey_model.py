"""add survey model

Revision ID: bbc711c2a169
Revises: dfbaa5314224
Create Date: 2025-10-12 16:41:10.474283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbc711c2a169'
down_revision: Union[str, Sequence[str], None] = 'dfbaa5314224'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
