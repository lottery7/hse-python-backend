from os import name
from typing import Callable, Iterator

from pydantic import NonNegativeInt, PositiveInt
from .models import *


def _create_id_gen() -> Iterator[int]:
    _id = 0
    while True:
        yield _id
        _id += 1


_carts = dict[int, CartInfo]()
_cart_id_gen = _create_id_gen()


_items = dict[int, ItemInfo]()
_items_id_gen = _create_id_gen()


def add_cart(info: CartInfo) -> CartEntity:
    id = next(_cart_id_gen)
    assert id not in _carts
    _carts[id] = info
    return CartEntity(id, _carts[id])


def new_cart() -> CartEntity:
    return add_cart(CartInfo([], 0))


def get_cart(id: int) -> CartEntity | None:
    if id not in _carts:
        return None
    return CartEntity(id, _carts[id])


def get_many_carts(
    offset: NonNegativeInt,
    limit: PositiveInt,
    _filter: Callable[[CartInfo], bool] | None = None,
) -> Iterator[CartEntity]:

    if _filter is None:
        _filter = lambda x: True

    entities = filter(
        lambda e: _filter(e.info), (CartEntity(id, info) for id, info in _carts.items())
    )

    curr = 0
    for e in entities:
        if curr >= offset + limit:
            break
        if curr >= offset:
            yield e
        curr += 1


def add_cart_item(cart_id: int, item_id: int) -> CartItemInfo | None:
    if cart_id not in _carts:
        return None

    cart_info = _carts[cart_id]

    for cart_item_info in cart_info.items:
        if cart_item_info.id == item_id:
            cart_item_info.quantity += 1
            return cart_item_info

    item_info = _items[item_id]
    cart_item_info = CartItemInfo(item_id, item_info.name, 1, not item_info.deleted)
    cart_info.items.append(cart_item_info)

    return cart_item_info


def add_item(info: ItemInfo) -> ItemEntity:
    id = next(_items_id_gen)
    _items[id] = info
    return ItemEntity(id, info)


def get_item(id: int) -> ItemEntity | None:
    if id not in _items:
        return None
    return ItemEntity(id, _items[id])


def get_many_items(
    offset: NonNegativeInt,
    limit: PositiveInt,
    _filter: Callable[[ItemInfo], bool] | None = None,
) -> Iterator[ItemEntity]:

    if _filter is None:
        _filter = lambda x: True

    entities = filter(
        lambda e: _filter(e.info), (ItemEntity(id, info) for id, info in _items.items())
    )

    curr = 0
    for e in entities:
        if curr >= offset + limit:
            break
        if curr >= offset:
            yield e
        curr += 1


def replace_item(id: int, info: ItemInfo) -> ItemEntity | None:
    if id not in _items:
        return None
    _items[id] = info
    return ItemEntity(id, info)


def update_item(id: int, info: PatchItemInfo) -> ItemEntity | None:
    if id not in _items:
        return None

    if not _items[id].deleted:
        if info.name is not None:
            _items[id].name = info.name

        if info.price is not None:
            _items[id].price = info.price

    return ItemEntity(id, _items[id])


def delete_item(id: int) -> bool:
    if id not in _items:
        return False
    _items[id].deleted = True
    for cart in _carts.values():
        for item in cart.items:
            if item.id == id:
                item.available = False
    return True
