"""split salary_range into salary_min/salary_max; make status required

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-13

Expand → backfill → contract, all in one migration because the table is small.
For a huge production table you'd split this into several deploys (see the lesson).
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Expand: add new nullable columns (safe, no table rewrite)
    op.add_column("applications", sa.Column("salary_min", sa.BigInteger(), nullable=True))
    op.add_column("applications", sa.Column("salary_max", sa.BigInteger(), nullable=True))

    # 2. Backfill with plain SQL (never import app models in migrations — they change over time)
    op.execute(
        r"""
        UPDATE applications
        SET salary_min = split_part(salary_range, '-', 1)::bigint,
            salary_max = split_part(salary_range, '-', 2)::bigint
        WHERE salary_range ~ '^\d+-\d+$'
        """
    )
    op.execute("UPDATE applications SET status = 'applied' WHERE status IS NULL")

    # 3. Tighten rules now that the data is valid
    op.alter_column("applications", "status", existing_type=sa.String(30), nullable=False, server_default="applied")
    # The metadata's naming convention ("ck_%(table_name)s_%(constraint_name)s") adds the prefix,
    # so pass the SHORT name here → final name: ck_applications_salary_range_valid
    op.create_check_constraint("salary_range_valid", "applications", "salary_min <= salary_max")

    # 4. Contract: remove the old column
    op.drop_column("applications", "salary_range")


def downgrade():
    op.add_column("applications", sa.Column("salary_range", sa.String(50), nullable=True))
    op.execute(
        """
        UPDATE applications
        SET salary_range = salary_min::text || '-' || salary_max::text
        WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL
        """
    )
    # op.f() marks the name as final, so the naming convention isn't applied a second time
    op.drop_constraint(op.f("ck_applications_salary_range_valid"), "applications", type_="check")
    op.alter_column("applications", "status", existing_type=sa.String(30), nullable=True, server_default=None)
    op.drop_column("applications", "salary_max")
    op.drop_column("applications", "salary_min")
