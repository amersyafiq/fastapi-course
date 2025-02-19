"""add content column to posts table

Revision ID: 1a4ab9d7dd5f
Revises: fa2c7192a669
Create Date: 2025-02-18 21:27:47.378103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a4ab9d7dd5f'
down_revision: Union[str, None] = 'fa2c7192a669'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
