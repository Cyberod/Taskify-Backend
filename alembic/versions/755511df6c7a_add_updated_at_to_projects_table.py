"""Add updated_at to projects table

Revision ID: 755511df6c7a
Revises: daa8d849222c
Create Date: 2025-06-07 04:28:48.053602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '755511df6c7a'
down_revision: Union[str, None] = 'daa8d849222c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


    # Set the updated_at column to the current time for existing records
    op.execute(text("UPDATE projects SET updated_at = created_at WHERE updated_at IS NULL"))

    # Alter the updated_at column to be non-nullable
    op.alter_column('projects', 'updated_at', nullable=False)

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('projects', 'updated_at')
    # ### end Alembic commands ###
