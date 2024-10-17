from fastapi import APIRouter, HTTPException, Response, status
from pydantic import NonNegativeFloat, NonNegativeInt, PositiveInt

from ...store import queries as store
from ...store.models import *
from .contracts import *


router = APIRouter(prefix="/cart")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_cart(response: Response) -> PostCartResponse:
    cart = store.new_cart()
    response.headers["location"] = f"{router.prefix}/{cart.id}"
    return PostCartResponse.from_entity(cart)


@router.get("/{id}")
async def get_cart(id: int) -> CartResponse:
    cart = store.get_cart(id)
    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart {id} not found",
        )
    return CartResponse.from_entity(cart)


@router.get("/")
async def get_carts(
    offset: NonNegativeInt = 0,
    limit: PositiveInt = 10,
    min_price: NonNegativeFloat | None = None,
    max_price: NonNegativeFloat | None = None,
    min_quantity: NonNegativeInt | None = None,
    max_quantity: NonNegativeInt | None = None,
) -> list[CartResponse]:

    def _filter(info: CartInfo):
        quantity = sum(item.quantity for item in info.items)
        return all(
            (
                min_price is None or info.price >= min_price,
                max_price is None or info.price <= max_price,
                min_quantity is None or quantity >= min_quantity,
                max_quantity is None or quantity <= max_quantity,
            )
        )

    carts = [
        CartResponse.from_entity(entity)
        for entity in store.get_many_carts(offset, limit, _filter)
    ]

    return carts


@router.post("/{cart_id}/add/{item_id}")
async def post_cart_item(cart_id: int, item_id: int):
    cart_item = store.add_cart_item(cart_id, item_id)
    if cart_item is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Cart with ID {cart_id} or item with ID {item_id} not found",
        )
    return PostCartItemResponse.from_info(cart_item)
