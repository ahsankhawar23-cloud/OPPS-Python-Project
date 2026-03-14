# ============================================================
# WHAT I LEARNED FROM THIS INVENTORY + SALES (MINI POS) SYSTEM
# ============================================================
# 1. I learned how inheritance works using a base Discount class.
# 2. I understood how polymorphism works with different discount types.
# 3. I learned how to use @dataclass for Product and Receipt.
# 4. I learned how to manage stock properly.
# 5. I understood how to validate user input.
# 6. I learned how to calculate subtotal and total.
# 7. I learned how to build a sales history system.
# 8. I improved my OOP skills in Python.
# 9. I learned how to design a small POS (Point of Sale) system.
# ============================================================


from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


# -----------------------
# Discount System
# -----------------------

class Discount:
    def apply(self, subtotal: float) -> float:
        return subtotal


class PercentDiscount(Discount):
    def __init__(self, percent: float):
        if not (0 <= percent <= 100):
            raise ValueError("Percent must be 0-100.")
        self.percent = percent

    def apply(self, subtotal: float) -> float:
        return subtotal * (1 - self.percent / 100)


class FixedDiscount(Discount):
    def __init__(self, amount: float):
        if amount < 0:
            raise ValueError("Amount must be >= 0.")
        self.amount = amount

    def apply(self, subtotal: float) -> float:
        return max(0.0, subtotal - self.amount)


# -----------------------
# Product
# -----------------------

@dataclass
class Product:
    product_id: str
    name: str
    price: float
    stock: int

    def restock(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Qty must be > 0.")
        self.stock += qty

    def reduce_stock(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Qty must be > 0.")
        if qty > self.stock:
            raise ValueError("Not enough stock.")
        self.stock -= qty


# -----------------------
# Receipt
# -----------------------

@dataclass
class Receipt:
    receipt_id: int
    items: List[Tuple[str, int, float, float]]  # (pid, qty, unit_price, line_total)

    def subtotal(self) -> float:
        return sum(line_total for *_rest, line_total in self.items)

    def total(self, discount: Optional[Discount] = None) -> float:
        sub = self.subtotal()
        return discount.apply(sub) if discount else sub

    @classmethod
    def from_cart(cls, receipt_id: int, cart: Dict[str, int], products: Dict[str, Product]) -> "Receipt":
        items: List[Tuple[str, int, float, float]] = []
        for pid, qty in cart.items():
            p = products[pid]
            items.append((pid, qty, p.price, p.price * qty))
        return cls(receipt_id, items)

    def print_receipt(self, products: Dict[str, Product], discount: Optional[Discount] = None) -> None:
        print(f"\nReceipt #{self.receipt_id}")
        print("----------------------")
        for pid, qty, unit, line_total in self.items:
            print(f"{products[pid].name} ({pid}) x{qty} @ {unit:.2f} = {line_total:.2f}")
        print("----------------------")
        print(f"Subtotal: {self.subtotal():.2f}")
        if discount:
            print(f"Total after discount: {self.total(discount):.2f}")
        else:
            print(f"Total: {self.subtotal():.2f}")


# -----------------------
# Store
# -----------------------

class Store:
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.sales: List[Receipt] = []
        self._next_receipt_id = 1

    def add_product(self, product_id: str, name: str, price: float, stock: int) -> None:
        product_id = product_id.strip()
        name = name.strip()

        if not product_id or not name:
            raise ValueError("Product ID and name required.")
        if product_id in self.products:
            raise ValueError("Product ID already exists.")
        if price < 0:
            raise ValueError("Price must be >= 0.")
        if stock < 0:
            raise ValueError("Stock must be >= 0.")

        self.products[product_id] = Product(product_id, name, price, stock)

    def restock(self, product_id: str, qty: int) -> None:
        if product_id not in self.products:
            raise KeyError("Product not found.")
        self.products[product_id].restock(qty)

    def low_stock(self, threshold: int = 5) -> List[Product]:
        return [p for p in self.products.values() if p.stock <= threshold]

    def create_sale(self, cart: Dict[str, int], discount: Optional[Discount] = None) -> Receipt:
        if not cart:
            raise ValueError("Cart is empty.")

        # Validate cart
        for pid, qty in cart.items():
            if pid not in self.products:
                raise KeyError(f"Product not found: {pid}")
            if qty <= 0:
                raise ValueError("Qty must be > 0.")
            if qty > self.products[pid].stock:
                raise ValueError(f"Not enough stock for {pid}.")

        # Reduce stock
        for pid, qty in cart.items():
            self.products[pid].reduce_stock(qty)

        # Create receipt
        rid = self._next_receipt_id
        self._next_receipt_id += 1

        receipt = Receipt.from_cart(rid, cart, self.products)
        self.sales.append(receipt)

        return receipt


# -----------------------
# CLI Helpers
# -----------------------

def read_discount() -> Optional[Discount]:
    ans = input("Discount? (none/percent/fixed): ").strip().lower()
    if ans in ("", "none"):
        return None
    if ans == "percent":
        return PercentDiscount(float(input("Percent (0-100): ")))
    if ans == "fixed":
        return FixedDiscount(float(input("Amount: ")))
    raise ValueError("Invalid discount type.")


# -----------------------
# Main Menu
# -----------------------

def main():
    store = Store()

    while True:
        print("\n--- Store Menu ---")
        print("1) Add product")
        print("2) Restock product")
        print("3) List products")
        print("4) Create sale")
        print("5) Low stock list")
        print("6) Exit")

        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                pid = input("Product ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                stock = int(input("Stock qty: "))
                store.add_product(pid, name, price, stock)
                print("Product added.")

            elif choice == "2":
                pid = input("Product ID: ")
                qty = int(input("Restock qty: "))
                store.restock(pid, qty)
                print("Restocked.")

            elif choice == "3":
                if not store.products:
                    print("No products.")
                else:
                    for p in store.products.values():
                        print(f"{p.product_id}: {p.name} price={p.price:.2f} stock={p.stock}")

            elif choice == "4":
                cart: Dict[str, int] = {}
                print("Enter items. Type 'done' when finished.")
                while True:
                    pid = input("Product ID: ").strip()
                    if pid.lower() == "done":
                        break
                    qty = int(input("Qty: "))
                    cart[pid] = cart.get(pid, 0) + qty

                discount = read_discount()
                receipt = store.create_sale(cart, discount)
                receipt.print_receipt(store.products, discount)

            elif choice == "5":
                t = int(input("Threshold (default 5): ") or "5")
                low = store.low_stock(t)
                if not low:
                    print("No low-stock products.")
                else:
                    for p in low:
                        print(f"{p.product_id}: {p.name} stock={p.stock}")

            elif choice == "6":
                print("Goodbye.")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()