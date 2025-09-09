"""add users table and user_id columns"""


from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.add_column("claims", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_claims_user_id", "claims", ["user_id"])
    op.create_foreign_key(None, "claims", "users", ["user_id"], ["id"])

    op.add_column("drift_history", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_drift_history_user_id", "drift_history", ["user_id"])
    op.create_foreign_key(None, "drift_history", "users", ["user_id"], ["id"])

    op.add_column("artifacts", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index("ix_artifacts_user_id", "artifacts", ["user_id"])
    op.create_foreign_key(None, "artifacts", "users", ["user_id"], ["id"])

    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "INSERT INTO users (email, password_hash, created_at) VALUES (:email, :pw, :created_at)"
        ),
        {
            "email": "public-demo@rve.local",
            "pw": generate_password_hash("demo"),
            "created_at": datetime.utcnow(),
        },
    )
    demo_id = result.inserted_primary_key[0]
    for table in ("claims", "drift_history", "artifacts"):
        conn.execute(sa.text(f"UPDATE {table} SET user_id = :uid"), {"uid": demo_id})
    op.alter_column("claims", "user_id", nullable=False)
    op.alter_column("drift_history", "user_id", nullable=False)
    op.alter_column("artifacts", "user_id", nullable=False)


def downgrade():
    op.drop_constraint(None, "artifacts", type_="foreignkey")
    op.drop_constraint(None, "drift_history", type_="foreignkey")
    op.drop_constraint(None, "claims", type_="foreignkey")
    op.drop_index("ix_artifacts_user_id", table_name="artifacts")
    op.drop_index("ix_drift_history_user_id", table_name="drift_history")
    op.drop_index("ix_claims_user_id", table_name="claims")
    op.drop_column("artifacts", "user_id")
    op.drop_column("drift_history", "user_id")
    op.drop_column("claims", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
