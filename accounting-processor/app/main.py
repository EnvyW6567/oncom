import asyncio
import json
import logging
import signal
import sys

import redis
from dotenv import load_dotenv

from app.database.redis_db import get_redis
from app.processor import TransactionProcessor
from app.repository.impl.postgres_processing_job_repository import PostgresProcessingJobRepository
from app.repository.impl.postgres_transaction_repository import PostgresTransactionRepository

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Worker:
    def __main__(self):
        pass

    def __init__(self):
        self.redis_client = get_redis()
        self.processor = TransactionProcessor(
            PostgresProcessingJobRepository(),
            PostgresTransactionRepository()
        )
        self.running = True

    def signal_handler(self, signum, frame):
        logger.info("종료 시그널 받음. 워커를 중지합니다...")

        self.running = False
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        logger.info("워커 시작. 작업 대기 중...")

        while self.running:
            try:
                result = self.redis_client.brpop('accounting_tasks', timeout=5)

                if result:
                    _, task_data = result
                    task = json.loads(task_data)

                    logger.info(f"작업 시작: {task['job_id']}")

                    try:
                        self.processor.process_job(task['job_id'])
                        logger.info(f"작업 완료: {task['job_id']}")

                    except Exception as e:
                        logger.error(f"작업 실패: {task['job_id']}, 오류: {str(e)}")

            except redis.ConnectionError:
                logger.error("Redis 연결 실패. 5초 후 재시도...")
                asyncio.sleep(5)
            except Exception as e:
                logger.error(f"예상치 못한 오류: {str(e)}")
                asyncio.sleep(1)

        logger.info("워커 종료")


if __name__ == "__main__":
    worker = Worker()
    worker.run()
