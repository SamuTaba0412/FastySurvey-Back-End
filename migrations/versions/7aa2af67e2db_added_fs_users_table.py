"""added fs_users table with admin user and hashed fixed password

Revision ID: 7aa2af67e2db
Revises: dfbaa5314224
Create Date: 2025-10-07 09:57:56.328865
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import date
import bcrypt

revision: str = '7aa2af67e2db'
down_revision: Union[str, Sequence[str], None] = 'dfbaa5314224'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    fs_users = op.create_table(
        'fs_users',
        sa.Column('id_user', sa.Integer(), nullable=False),
        sa.Column('names', sa.String(length=60), nullable=False),
        sa.Column('last_names', sa.String(length=60), nullable=False),
        sa.Column('identification_type', sa.String(length=5), nullable=False),
        sa.Column('identification', sa.String(length=15), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('creation_date', sa.Date(), nullable=False),
        sa.Column('update_date', sa.Date(), nullable=True),
        sa.Column('user_state', sa.Integer(), nullable=False),
        sa.Column('id_role', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_role'], ['fs_roles.id_role'], name='fk_role', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_user'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('identification')
    )

    plain_password = "R7#pG9!t"

    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    op.bulk_insert(
        fs_users,
        [
            {
                "names": "Samuel",
                "last_names": "Tabares Patiño",
                "identification_type": "CC",
                "identification": "1017923676",
                "email": "samutabares09022005@gmail.com",
                "password": hashed_password,
                "creation_date": date.today(),
                "update_date": None,
                "user_state": 1,
                "id_role": 1,
            }
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('fs_users')