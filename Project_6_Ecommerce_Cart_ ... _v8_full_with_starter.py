# ============================================
# E-Commerce Cart System
# Demonstrates OOP concepts:
# Abstraction, Polymorphism, Composition,
# Encapsulation, Strategy Pattern
# ============================================

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict


# ============================================
# Pricing Strategy (Abstract Base Class)
# ============================================
class PricingStrategy(ABC):

    # calculate final price after discount
    @abstractmethod
    def calculate(self, subtotal: float) -> float:
        pass


# ============================================
# No Discount Strategy
# ============================================
class NoDiscount(PricingStrategy):

    def calculate(self, subtotal: float) -> float:
        return subtotal


# ============================================
# Percentage Discount Strategy
# ============================================
class PercentageDiscount(PricingStrategy):

    def __init__(self, percent: float):

        # validate percent
        if percent < 0 or percent > 100:
            raise ValueError("Percent must be between 0 and 100")

        self.percent = percent

    def calculate(self, subtotal: float) -> float:

        discount = subtotal * (self.percent / 100)
        return subtotal - discount


# ============================================
# Product Data Class
# ============================================
@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: float

    def __post_init__(self):

        # validate product price
        if self.price <= 0:
            raise ValueError("Price must be greater than 0")


# ============================================
# Cart Item
# ============================================
@dataclass
class CartItem:
    product: Product
    qty: int = 1

    # calculate subtotal for item
    def subtotal(self) -> float:

        if self.qty < 1:
            raise ValueError("Quantity must be at least 1")

        return self.product.price * self.qty


# ============================================
# Shopping Cart
# ============================================
class ShoppingCart:

    def __init__(self, strategy: PricingStrategy):
        self._items: Dict[str, CartItem] = {}   # sku -> CartItem
        self.strategy = strategy

    # add product to cart
    def add(self, product: Product, qty: int = 1) -> None:

        if qty < 1:
            raise ValueError("Quantity must be at least 1")

        if product.sku in self._items:
            # increase quantity
            self._items[product.sku].qty += qty
        else:
            self._items[product.sku] = CartItem(product, qty)

    # remove product from cart
    def remove(self, sku: str) -> None:

        if sku not in self._items:
            raise KeyError("Item not found in cart")

        del self._items[sku]

    # calculate subtotal of cart
    def subtotal(self) -> float:

        total = 0.0
        for item in self._items.values():
            total += item.subtotal()

        return total

    # calculate total after applying pricing strategy
    def total(self) -> float:

        subtotal = self.subtotal()
        return self.strategy.calculate(subtotal)

    # generate receipt lines
    def receipt(self):

        lines = []
        for item in self._items.values():
            line = f"{item.product.name} x{item.qty} = {item.subtotal():.2f}"
            lines.append(line)

        subtotal = self.subtotal()
        total = self.total()
        discount = subtotal - total

        lines.append(f"Subtotal: {subtotal:.2f}")
        lines.append(f"Discount: {discount:.2f}")
        lines.append(f"Total: {total:.2f}")

        return lines


# ============================================
# Example Usage
# ============================================
if __name__ == "__main__":

    # create products
    p1 = Product("P101", "Laptop", 1000)
    p2 = Product("P102", "Mouse", 50)
    p3 = Product("P103", "Keyboard", 80)

    # choose pricing strategy
    strategy = PercentageDiscount(10)

    # create cart
    cart = ShoppingCart(strategy)

    # add products
    cart.add(p1, 1)
    cart.add(p2, 2)
    cart.add(p3, 1)

    # print receipt
    print("Receipt")
    print("-------")

    for line in cart.receipt():
        print(line)