"""Inline schema migrations that run automatically on startup.

Each migration is idempotent — it checks whether the change is needed before
applying it, so it is safe to run on every startup (including Docker).
"""

import logging

from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)


def run_migrations(db) -> None:
    """Apply any pending schema migrations.

    Called from create_app() after db.create_all(), inside an active
    app context.
    """
    _migrate_add_user_id_to_time_entries(db)


# ---------------------------------------------------------------------------
# Individual migrations
# ---------------------------------------------------------------------------


def _migrate_add_user_id_to_time_entries(db) -> None:
    """Add user_id column to time_entries and assign existing rows to the
    default admin user.

    Safe for SQLite and PostgreSQL.
    """
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('time_entries')]

    if 'user_id' in columns:
        return  # Already migrated

    logger.info('Migration: adding user_id column to time_entries')

    db_url = str(db.engine.url)
    is_sqlite = db_url.startswith('sqlite')

    with db.engine.begin() as conn:
        if is_sqlite:
            # SQLite does not support NOT NULL ADD COLUMN without a DEFAULT,
            # so we add it as nullable first, back-fill, then note the
            # constraint lives in SQLAlchemy only (SQLite doesn't enforce it).
            conn.execute(text('ALTER TABLE time_entries ADD COLUMN user_id INTEGER'))
        else:
            # PostgreSQL / other RDBMS — add as nullable, we'll fill it next
            conn.execute(text('ALTER TABLE time_entries ADD COLUMN user_id INTEGER REFERENCES users(id)'))

        # Assign all orphaned rows to the first admin user, falling back to
        # the first user of any kind if no admin exists yet.
        row = conn.execute(text('SELECT id FROM users WHERE is_admin = 1 ORDER BY id LIMIT 1')).fetchone()

        if row is None:
            row = conn.execute(text('SELECT id FROM users ORDER BY id LIMIT 1')).fetchone()

        if row is not None:
            admin_id = row[0]
            conn.execute(
                text('UPDATE time_entries SET user_id = :uid WHERE user_id IS NULL'),
                {'uid': admin_id},
            )
            logger.info('Migration: assigned %d rows to user id=%d', _count_updated(conn), admin_id)
        else:
            # No users exist yet — rows will be assigned when the default
            # admin is created and the user logs in for the first time.
            # Leave them NULL for now; they are invisible until claimed.
            logger.warning('Migration: no users found — existing time_entries left with NULL user_id')


def _count_updated(conn) -> int:
    """Return the number of time_entries that still have a non-NULL user_id."""
    result = conn.execute(text('SELECT COUNT(*) FROM time_entries WHERE user_id IS NOT NULL')).fetchone()
    return result[0] if result else 0
