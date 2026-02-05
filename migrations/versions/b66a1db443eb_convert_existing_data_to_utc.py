"""convert_existing_data_to_utc

Revision ID: b66a1db443eb
Revises: 37ea7e8810b5
Create Date: 2026-02-05 16:38:52.284902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b66a1db443eb'
down_revision: Union[str, Sequence[str], None] = '37ea7e8810b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PyCharm будет подсвечивать это желтым, пока не привяжешь БД — это ок!
    tables = ['users', 'attempts', 'audit_logs', 'elo_history', 'pvp_matches']
    for table in tables:
        op.execute(
            f"UPDATE {table} SET created_at = created_at AT TIME ZONE 'Europe/Moscow' AT TIME ZONE 'UTC'"
        )

def downgrade() -> None:
    tables = ['users', 'attempts', 'audit_logs', 'elo_history', 'pvp_matches']
    for table in tables:
        op.execute(
            f"UPDATE {table} SET created_at = created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Moscow'"
        )
