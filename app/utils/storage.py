import logging
from app import database

async def save_order(data: dict, user_id: int):
    if not database.pool:
        logging.error("Database pool is not initialized.")
        return

    loc_a = data.get("loc_a", {})
    loc_b = data.get("loc_b", {})
    
    query = """
        INSERT INTO orders (
            user_id, fullname, phone, region, district, district_detailed,
            loc_a_lat, loc_a_lon, loc_b_lat, loc_b_lon,
            truck_type, movers, chosen_lang
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
        )
    """
    
    try:
        async with database.pool.acquire() as conn:
            await conn.execute(
                query,
                user_id,
                data.get("fullname"),
                data.get("phone"),
                data.get("region"),
                data.get("district"),
                data.get("district_detailed"),
                loc_a.get("lat"),
                loc_a.get("lon"),
                loc_b.get("lat"),
                loc_b.get("lon"),
                data.get("truck_type"),
                data.get("movers"),
                data.get("chosen_lang")
            )
    except Exception as e:
        logging.error(f"Failed to save order to db: {e}")
