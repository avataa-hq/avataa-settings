"""Update operators data in filterset

Revision ID: 909a5bdc5b16
Revises: 3d75a4ecab7c
Create Date: 2024-01-23 10:01:00.254408

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '909a5bdc5b16'
down_revision = '3d75a4ecab7c'
branch_labels = None
depends_on = None

symbol_mapping = {
    '!=': 'notEquals',
    '>=': 'moreOrEq',
    '<=': 'lessOrEq',
    '=': 'equals',
    '>': 'more',
    '<': 'less'
}


def get_update_query(value, filter_id):
    return text(f"""UPDATE filter_set SET filters = '{value}' WHERE id = {filter_id};""")


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if inspector.has_table('filter_set'):
        rows = connection.execute(text("SELECT id, filters FROM filter_set")).fetchall()
        for row in rows:
            if row is not None:
                filter_id, json_value = row
                if json_value is not None:
                    for symbol, word in symbol_mapping.items():
                        json_value = (str(json_value).replace("'", '"').
                                      replace(f'"operator": "{symbol}"', f'"operator": "{word}"'))
                        connection.execute(get_update_query(value=json_value, filter_id=filter_id))


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if inspector.has_table('filter_set'):
        rows = connection.execute(text("SELECT id, filters FROM filter_set")).fetchall()
        for row in rows:
            if row is not None:
                filter_id, json_value = row
                if json_value is not None:
                    for symbol, word in symbol_mapping.items():
                        json_value = (str(json_value).replace("'", '"').
                                      replace(f'"operator": "{word}"', f'"operator": "{symbol}"'))
                        connection.execute(get_update_query(value=json_value, filter_id=filter_id))
