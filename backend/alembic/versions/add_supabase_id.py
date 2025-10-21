"""Add supabase_id to users

Revision ID: add_supabase_id
Revises: 6a90c6e6ea03
Create Date: 2025-10-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_supabase_id"
down_revision = "6a90c6e6ea03"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Añadir columna supabase_id (texto nullable)
    op.add_column("users", sa.Column("supabase_id", sa.String(), nullable=True))
    # Crear índice único (si quieres que sea único; quita unique=True si no lo deseas)
    op.create_index(op.f("ix_users_supabase_id"), "users", ["supabase_id"], unique=True)

def downgrade() -> None:
    op.drop_index(op.f("ix_users_supabase_id"), table_name="users")
    op.drop_column("users", "supabase_id")