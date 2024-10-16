from dataclasses import dataclass

from pydantic import NonNegativeFloat, NonNegativeInt


@dataclass(slots=True)
class ItemInfo:
    name: str
    price: NonNegativeFloat
    deleted: bool = False

@dataclass(slots=True)
class PatchItemInfo:
    name: str | None = None
    price: NonNegativeFloat | None = None


@dataclass(slots=True)
class ItemEntity:
    id: int
    info: ItemInfo


@dataclass(slots=True)
class CartItemInfo:
    id: int
    name: str
    quantity: NonNegativeInt
    available: bool


@dataclass(slots=True)
class CartInfo:
    items: list[CartItemInfo]
    price: NonNegativeFloat


@dataclass(slots=True)
class CartEntity:
    id: int
    info: CartInfo
