"""Add file upload functionality

Revision ID: 17ba1b91c5ae
Revises: 2b1000ad2835
Create Date: 2025-07-30 04:06:21.722803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17ba1b91c5ae'
down_revision: Union[str, None] = '2b1000ad2835'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
