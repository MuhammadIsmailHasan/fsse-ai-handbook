"""create applications (the starting point, already in production)

Revision ID: 0001
Revises:
Create Date: 2026-09-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("role_title", sa.String(200), nullable=False),
        sa.Column("status", sa.String(30), nullable=True),          # oops: nullable, no default
        sa.Column("salary_range", sa.String(50), nullable=True),     # oops: "9000000-14000000" as text
    )


def downgrade():
    op.drop_table("applications")
