"""add display_name to users

Revision ID: f3a4b5c6d7e8
Revises: 60f62404aa55
Create Date: 2026-03-08 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('display_name', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'display_name')
