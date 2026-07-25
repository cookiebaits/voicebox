import asyncio
import logging
from datetime import datetime, timedelta
from ..database import get_db, Generation
from ..services import history

logger = logging.getLogger(__name__)

async def cleanup_stale_audio():
    while True:
        await asyncio.sleep(60)
        db = next(get_db())
        try:
            cutoff = datetime.utcnow() - timedelta(minutes=1)
            stale_gens = db.query(Generation).filter(Generation.created_at < cutoff).all()
            for gen in stale_gens:
                try:
                    await history.delete_generation(gen.id, db)
                    logger.info(f"Deleted stale unplayed generation: {gen.id}")
                except Exception as e:
                    logger.error(f"Failed to delete stale generation {gen.id}: {e}")
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
        finally:
            db.close()
