"""Add JIRA ticket fields

Revision ID: a7a27f6e3190
Revises: 032678519d9d
Create Date: 2024-11-11 10:49:41.282116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a7a27f6e3190'
down_revision: Union[str, None] = '032678519d9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticket', sa.Column('summary', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('ticket', sa.Column('order_reference', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('ticket', sa.Column('platforms', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('ticket', sa.Column('i_need_a_voucher', sa.Boolean(), nullable=False))
    op.add_column('ticket', sa.Column('voucher_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('ticket', sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('ticket', sa.Column('service', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('ticket', sa.Column('offer', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('ticket', sa.Column('offer_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.drop_column('ticket', 'description')
    op.drop_column('ticket', 'title')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ticket', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('ticket', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('ticket', 'offer_type')
    op.drop_column('ticket', 'offer')
    op.drop_column('ticket', 'service')
    op.drop_column('ticket', 'category')
    op.drop_column('ticket', 'voucher_id')
    op.drop_column('ticket', 'i_need_a_voucher')
    op.drop_column('ticket', 'platforms')
    op.drop_column('ticket', 'order_reference')
    op.drop_column('ticket', 'summary')
    # ### end Alembic commands ###