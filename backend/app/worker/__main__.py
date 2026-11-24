import logging
import socket
import threading
import time
from typing import Optional

from app.core.config import settings
from app.db.session import SessionLocal
from app.services import ingestion, queue

logger = logging.getLogger(__name__)


def run_worker_once(worker_id: str) -> bool:
    """Claim and process a single pending ingestion job. Returns True if a job was processed."""
    if SessionLocal is None:
        return False

    db = SessionLocal()
    try:
        job = queue.claim_next_job(db, worker_id=worker_id)
        if not job:
            return False
        logger.info("Worker %s claimed job %s for document %s", worker_id, job.id, job.document_id)
        ingestion.process_ingestion_job(db, job)
        return True
    except Exception as exc:
        logger.warning("Worker %s encountered error: %s", worker_id, type(exc).__name__)
        return False
    finally:
        db.close()


def run_worker_loop(stop_event: Optional[threading.Event] = None, worker_id: Optional[str] = None) -> None:
    """Continuously poll the ingestion queue until stopped."""
    resolved_id = worker_id or f"worker-{socket.gethostname()}"
    poll_interval = max(1, settings.WORKER_POLL_INTERVAL_SECONDS)
    logger.info("Starting ingestion worker %s (poll=%ss)", resolved_id, poll_interval)

    while not (stop_event and stop_event.is_set()):
        processed = run_worker_once(resolved_id)
        if not processed:
            if stop_event:
                stop_event.wait(poll_interval)
            else:
                time.sleep(poll_interval)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_worker_loop()
