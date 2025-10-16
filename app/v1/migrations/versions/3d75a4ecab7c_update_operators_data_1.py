"""Update operators data 1

Revision ID: 3d75a4ecab7c
Revises: cec336731b98
Create Date: 2024-01-22 19:37:04.619677

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '3d75a4ecab7c'
down_revision = '59fc2f621fba'
branch_labels = None
depends_on = None

symbol_mapping = {
    '>=': 'moreOrEq',
    '!=': 'notEquals',
    '<=': 'lessOrEq',
    '=': 'equals',
    '>': 'more',
    '<': 'less',
}


def get_update_query(value, filter_id):
    return text(f"""UPDATE table_filters SET value = '{value}' WHERE id = {filter_id};""")


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if inspector.has_table('filter_set'):
        rows = connection.execute(text("SELECT id, value FROM table_filters")).fetchall()
        for row in rows:
            if row is not None:
                filter_id, json_value = row
                if json_value is not None:
                    for symbol, word in symbol_mapping.items():
                        json_value = (str(json_value).replace("'", '"')
                                      .replace(f'"operator": "{symbol}"', f'"operator": "{word}"')
                                      .replace('False', 'false')
                                      .replace('True', 'true')
                                      .replace('None', 'null'))
                        connection.execute(get_update_query(value=json_value, filter_id=filter_id))


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if inspector.has_table('filter_set'):
        rows = connection.execute(text("SELECT id, value FROM table_filters")).fetchall()
        for row in rows:
            if row is not None:
                filter_id, json_value = row
                if json_value is not None:
                    for symbol, word in symbol_mapping.items():
                        json_value = (str(json_value).replace("'", '"')
                                      .replace(f'"operator": "{word}"', f'"operator": "{symbol}"')
                                      .replace('False', 'false')
                                      .replace('True', 'true')
                                      .replace('None', 'null'))
                        connection.execute(get_update_query(value=json_value, filter_id=filter_id))
