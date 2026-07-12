"""Entity Model V2: display_name, rarity, and payload columns on entities.

Revision ID: b7c2d4e6f8a1
Revises: e41196798f3f
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b7c2d4e6f8a1"
down_revision: str | None = "e41196798f3f"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Add the Entity Model V2 columns."""
    op.add_column("entities", sa.Column("display_name", sa.String(length=200), nullable=True))
    op.add_column("entities", sa.Column("rarity", sa.String(length=20), nullable=True))
    op.add_column(
        "entities",
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql"),
            nullable=True,
        ),
    )
    op.create_index("ix_entities_display_name", "entities", ["display_name"])
    op.create_index("ix_entities_rarity", "entities", ["rarity"])


def downgrade() -> None:
    """Remove the Entity Model V2 columns."""
    op.drop_index("ix_entities_rarity", table_name="entities")
    op.drop_index("ix_entities_display_name", table_name="entities")
    op.drop_column("entities", "payload")
    op.drop_column("entities", "rarity")
    op.drop_column("entities", "display_name")
