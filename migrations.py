from lnbits.db import Connection


async def m001_initial(db: Connection):
    """Initial roxy table."""
    await db.execute(f"""
        CREATE TABLE roxy.roxies (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            title TEXT NOT NULL,
            target_url TEXT NOT NULL,
            encoding TEXT NOT NULL DEFAULT 'url',
            is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            unique_hash TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT {db.timestamp_column_default},
            updated_at TIMESTAMP DEFAULT {db.timestamp_column_default}
        );
    """)
