from datetime import datetime

from app.database.postgres_db import get_cursor
from app.entity.transaction import Transaction
from app.repository.transaction_repository import TransactionRepository


class PostgresTransactionRepository(TransactionRepository):

    def save(self, transaction: Transaction):
        with get_cursor() as cursor:
            cursor.execute("""
            INSERT INTO transactions (
                job_id, company_id, category_id,
                transaction_date, description,
                amount_in, amount_out, balance_after,
                transaction_location, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                transaction.job_id, transaction.company_id, transaction.category_id,
                transaction.transaction_date, transaction.description,
                transaction.amount_in, transaction.amount_out, transaction.balance_after,
                transaction.transaction_location, datetime.now()
            ))
