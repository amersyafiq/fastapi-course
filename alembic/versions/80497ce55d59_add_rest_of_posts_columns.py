"""add rest of posts columns

Revision ID: 80497ce55d59
Revises: 1341a72bb550
Create Date: 2025-02-19 08:42:01.410062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80497ce55d59'
down_revision: Union[str, None] = '1341a72bb550'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts',
                  sa.Column('published', sa.Boolean, nullable=False, server_default='TRUE'),)
    op.add_column('posts', 
                  sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),)
    pass


def downgrade() -> None:
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
    pass
