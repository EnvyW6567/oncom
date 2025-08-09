from abc import abstractmethod

from app.entity.transaction import Transaction


class TransactionRepository:
    @abstractmethod
    def save(self, transaction: Transaction):
        pass
