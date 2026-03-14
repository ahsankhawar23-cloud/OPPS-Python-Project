from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from abc import ABC, abstractmethod
from datetime import date
import unittest


# ==========================
# Fine Policy (Abstraction)
# ==========================

class FinePolicy(ABC):

    @abstractmethod
    def calculate(self, days_late: int) -> float:
        pass


class SimpleFinePolicy(FinePolicy):

    def __init__(self, per_day: float = 5.0):
        self.per_day = per_day

    def calculate(self, days_late: int) -> float:
        if days_late <= 0:
            return 0.0
        return days_late * self.per_day


# ==========================
# Book Model
# ==========================

@dataclass
class Book:

    book_id: str
    title: str
    author: str
    __available: bool = field(default=True, repr=False)

    def borrow(self) -> None:

        if not self.__available:
            raise ValueError("Book is not available")

        self.__available = False

    def return_book(self) -> None:

        self.__available = True

    def is_available(self) -> bool:
        return self.__available


# ==========================
# Member Model
# ==========================

@dataclass
class Member:

    member_id: str
    name: str
    __borrowed_books: Set[str] = field(default_factory=set, repr=False)

    def borrow_book(self, book_id: str, limit: int = 3) -> None:

        if len(self.__borrowed_books) >= limit:
            raise ValueError("Borrow limit reached")

        self.__borrowed_books.add(book_id)

    def return_book(self, book_id: str) -> None:

        if book_id not in self.__borrowed_books:
            raise ValueError("Member did not borrow this book")

        self.__borrowed_books.remove(book_id)

    @property
    def borrowed_books(self) -> Set[str]:
        return set(self.__borrowed_books)


# ==========================
# Borrow Record
# ==========================

@dataclass
class BorrowRecord:

    member_id: str
    book_id: str
    borrow_date: date
    return_date: Optional[date] = None


# ==========================
# Library Business Logic
# ==========================

class Library:

    def __init__(self, fine_policy: FinePolicy):

        self.fine_policy = fine_policy
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.records: List[BorrowRecord] = []

    # Add book

    def add_book(self, book_id: str, title: str, author: str) -> None:

        if book_id in self.books:
            raise ValueError("Book ID already exists")

        self.books[book_id] = Book(book_id, title, author)

    # Add member

    def add_member(self, member_id: str, name: str) -> None:

        if member_id in self.members:
            raise ValueError("Member ID already exists")

        self.members[member_id] = Member(member_id, name)

    # Borrow book

    def borrow_book(self, member_id: str, book_id: str, borrow_date: date) -> None:

        if member_id not in self.members:
            raise KeyError("Member does not exist")

        if book_id not in self.books:
            raise KeyError("Book does not exist")

        member = self.members[member_id]
        book = self.books[book_id]

        book.borrow()
        member.borrow_book(book_id)

        record = BorrowRecord(member_id, book_id, borrow_date)

        self.records.append(record)

    # Return book

    def return_book(self, member_id: str, book_id: str, return_date: date) -> float:

        if member_id not in self.members:
            raise KeyError("Member does not exist")

        if book_id not in self.books:
            raise KeyError("Book does not exist")

        member = self.members[member_id]
        book = self.books[book_id]

        member.return_book(book_id)
        book.return_book()

        record = None

        for r in self.records:
            if r.member_id == member_id and r.book_id == book_id and r.return_date is None:
                record = r
                break

        if record is None:
            raise ValueError("Borrow record not found")

        record.return_date = return_date

        days_borrowed = (return_date - record.borrow_date).days

        grace_period = 7
        days_late = max(0, days_borrowed - grace_period)

        fine = self.fine_policy.calculate(days_late)

        return fine


# ==========================
# CLI (User Interface)
# ==========================

def run_cli():

    library = Library(SimpleFinePolicy())

    while True:

        print("\n===== Library Menu =====")
        print("1 Add Book")
        print("2 Add Member")
        print("3 Borrow Book")
        print("4 Return Book")
        print("5 Exit")

        choice = input("Choose option: ")

        try:

            if choice == "1":

                book_id = input("Book ID: ")
                title = input("Title: ")
                author = input("Author: ")

                library.add_book(book_id, title, author)

                print("Book added successfully")

            elif choice == "2":

                member_id = input("Member ID: ")
                name = input("Name: ")

                library.add_member(member_id, name)

                print("Member added successfully")

            elif choice == "3":

                member_id = input("Member ID: ")
                book_id = input("Book ID: ")

                library.borrow_book(member_id, book_id, date.today())

                print("Book borrowed")

            elif choice == "4":

                member_id = input("Member ID: ")
                book_id = input("Book ID: ")

                fine = library.return_book(member_id, book_id, date.today())

                print("Book returned")
                print("Fine:", fine)

            elif choice == "5":

                break

        except Exception as e:

            print("Error:", e)


# ==========================
# Unit Tests
# ==========================

class TestLibrary(unittest.TestCase):

    def setUp(self):

        self.library = Library(SimpleFinePolicy())

        self.library.add_book("b1", "Python", "Guido")
        self.library.add_member("m1", "Ali")

    def test_add_book(self):

        self.library.add_book("b2", "AI", "John")

        self.assertIn("b2", self.library.books)

    def test_add_member(self):

        self.library.add_member("m2", "Sara")

        self.assertIn("m2", self.library.members)

    def test_borrow_book(self):

        self.library.borrow_book("m1", "b1", date(2024,1,1))

        self.assertFalse(self.library.books["b1"].is_available())

    def test_return_book(self):

        self.library.borrow_book("m1","b1",date(2024,1,1))

        fine = self.library.return_book("m1","b1",date(2024,1,5))

        self.assertEqual(fine,0)

    def test_fine_calculation(self):

        self.library.borrow_book("m1","b1",date(2024,1,1))

        fine = self.library.return_book("m1","b1",date(2024,1,20))

        self.assertTrue(fine > 0)

    def test_borrow_unavailable(self):

        self.library.borrow_book("m1","b1",date(2024,1,1))

        with self.assertRaises(ValueError):

            self.library.borrow_book("m1","b1",date(2024,1,2))

    def test_invalid_member(self):

        with self.assertRaises(KeyError):

            self.library.borrow_book("x","b1",date(2024,1,1))

    def test_invalid_book(self):

        with self.assertRaises(KeyError):

            self.library.borrow_book("m1","x",date(2024,1,1))


# ==========================
# Run Program
# ==========================

if __name__ == "__main__":

    print("1 Run Library CLI")
    print("2 Run Tests")

    mode = input("Select mode: ")

    if mode == "1":
        run_cli()

    elif mode == "2":
        unittest.main()
