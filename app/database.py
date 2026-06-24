import logging
import asyncpg
from app.config import DATABASE_URL

pool: asyncpg.Pool | None = None

async def init_db():
    global pool
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
        
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    fullname VARCHAR(255),
                    phone VARCHAR(50),
                    region VARCHAR(255),
                    district VARCHAR(255),
                    district_detailed VARCHAR(255),
                    loc_a_lat DOUBLE PRECISION,
                    loc_a_lon DOUBLE PRECISION,
                    loc_b_lat DOUBLE PRECISION,
                    loc_b_lon DOUBLE PRECISION,
                    truck_type VARCHAR(255),
                    movers VARCHAR(255),
                    chosen_lang VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        logging.info("Database connection and tables initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")

async def close_db():
    global pool
    if pool:
        await pool.close()
        logging.info("Database connection closed.")
