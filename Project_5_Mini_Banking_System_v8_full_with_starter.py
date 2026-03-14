# ============================================
# Mini Banking System
# Demonstrates OOP concepts:
# Encapsulation, Inheritance, Polymorphism
# ============================================

from __future__ import annotations
from datetime import date
from typing import Dict, List, Tuple

# Transaction format:
# (date, type, amount, balance_after)
Txn = Tuple[str, str, float, float]


# ============================================
# Base Account Class
# ============================================
class Account:

    def __init__(self, account_id: str, owner: str):
        self.account_id = account_id
        self.owner = owner
        self.__balance: float = 0.0          # private balance
        self._history: List[Txn] = []        # transaction history

    # record transaction in history
    def _record(self, typ: str, amount: float) -> None:
        txn = (date.today().isoformat(), typ, amount, self.__balance)
        self._history.append(txn)

    # deposit money
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        new_balance = self.__balance + amount
        self._set_balance(new_balance)
        self._record("DEPOSIT", amount)

    # return balance
    def get_balance(self) -> float:
        return self.__balance

    # internal method to update balance
    def _set_balance(self, new_balance: float) -> None:
        self.__balance = new_balance

    # withdraw (to be overridden)
    def withdraw(self, amount: float) -> None:
        raise NotImplementedError("Withdraw must be implemented in subclass")

    # transfer money between accounts
    def transfer(self, to: "Account", amount: float) -> None:

        if self is to:
            raise ValueError("Cannot transfer to same account")

        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        # withdraw first (atomic operation)
        self.withdraw(amount)

        # deposit if withdraw succeeded
        to.deposit(amount)

        self._record("TRANSFER_OUT", amount)
        to._record("TRANSFER_IN", amount)

    # show transaction history
    def statement(self) -> List[Txn]:
        return list(self._history)


# ============================================
# Savings Account
# Cannot go below 0 balance
# ============================================
class SavingsAccount(Account):

    def withdraw(self, amount: float) -> None:

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if self.get_balance() - amount < 0:
            raise ValueError("Savings account cannot overdraft")

        new_balance = self.get_balance() - amount
        self._set_balance(new_balance)
        self._record("WITHDRAW", amount)


# ============================================
# Current Account
# Allows overdraft up to limit
# ============================================
class CurrentAccount(Account):

    def __init__(self, account_id: str, owner: str, overdraft_limit: float = 5000.0):
        super().__init__(account_id, owner)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float) -> None:

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        new_balance = self.get_balance() - amount

        if new_balance < -self.overdraft_limit:
            raise ValueError("Overdraft limit exceeded")

        self._set_balance(new_balance)
        self._record("WITHDRAW", amount)


# ============================================
# Bank class manages accounts
# ============================================
class Bank:

    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    # open new account
    def open_account(self, account: Account) -> None:

        if account.account_id in self.accounts:
            raise ValueError("Account ID already exists")

        self.accounts[account.account_id] = account

    # get account by ID
    def get_account(self, account_id: str) -> Account:

        if account_id not in self.accounts:
            raise KeyError("Account not found")

        return self.accounts[account_id]

    # transfer between two accounts
    def transfer(self, from_id: str, to_id: str, amount: float) -> None:

        from_acc = self.get_account(from_id)
        to_acc = self.get_account(to_id)

        from_acc.transfer(to_acc, amount)


# ============================================
# Example Usage (for testing)
# ============================================
if __name__ == "__main__":

    bank = Bank()

    acc1 = SavingsAccount("A101", "Ali")
    acc2 = CurrentAccount("A102", "Ahmed", overdraft_limit=2000)

    bank.open_account(acc1)
    bank.open_account(acc2)

    acc1.deposit(1000)
    acc1.transfer(acc2, 200)
    acc2.withdraw(500)

    print("Ali Balance:", acc1.get_balance())
    print("Ahmed Balance:", acc2.get_balance())

    print("\nAli Statement:")
    for txn in acc1.statement():
        print(txn)

    print("\nAhmed Statement:")
    for txn in acc2.statement():
        print(txn)