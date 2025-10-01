from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision: str = 'dfbaa5314224'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'fs_permissions',
        sa.Column('id_permission', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('permission_name', sa.String(), nullable=False)
    )
    op.create_table(
        'fs_roles',
        sa.Column('id_role', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('role_name', sa.String(length=50), nullable=False),
        sa.Column('creation_date', sa.Date(), nullable=False),
        sa.Column('role_state', sa.Integer(), nullable=False),
        sa.Column('update_date', sa.Date(), nullable=True)
    )
    op.create_table(
        'fs_roles_permissions',
        sa.Column('id_roles_permissions', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_role', sa.Integer(), sa.ForeignKey('fs_roles.id_role', name='fk_role', ondelete='CASCADE')),
        sa.Column('id_permission', sa.Integer(), sa.ForeignKey('fs_permissions.id_permission', name='fk_permission', ondelete='CASCADE'))
    )

    permissions_table = sa.table(
        "fs_permissions",
        sa.column("permission_name", sa.String)
    )

    roles_table = sa.table(
        "fs_roles",
        sa.column("role_name", sa.String),
        sa.column("creation_date", sa.Date),
        sa.column("role_state", sa.Integer),
    )

    op.bulk_insert(
        permissions_table,
        [
            {"permission_name": "Inicio"},
            {"permission_name": "Creación de Encuestas"},
            {"permission_name": "Administrar Encuestas"},
            {"permission_name": "Administrar Usuarios"},
            {"permission_name": "Administrar Roles"},
        ]
    )

    op.bulk_insert(
        roles_table,
        [
            {
                "role_name": "Administrador",
                "creation_date": datetime.date.today(),
                "role_state": 1
            }
        ]
    )

    op.execute("""
        INSERT INTO fs_roles_permissions (id_role, id_permission)
        SELECT r.id_role, p.id_permission
        FROM fs_roles r, fs_permissions p
        WHERE r.role_name = 'Administrador';
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('fs_roles_permissions')
    op.drop_table('fs_roles')
    op.drop_table('fs_permissions')