from fastapi import APIRouter, HTTPException, Response, status
from pydantic import NonNegativeInt, PositiveInt
from .contracts import *
from ...store import queries as store

router = APIRouter(prefix="/item")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_item(request: ItemRequest, response: Response) -> ItemResponse:
    item = store.add_item(request.as_item_info())
    return ItemResponse.from_entity(item)


@router.get("/{item_id}")
async def get_item(item_id: int) -> ItemResponse:
    item = store.get_item(item_id)
    if item is None or item.info.deleted:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found",
        )
    return ItemResponse.from_entity(item)


@router.get("/")
async def get_items(
    offset: NonNegativeInt = 0,
    limit: PositiveInt = 10,
    min_price: NonNegativeFloat | None = None,
    max_price: NonNegativeFloat | None = None,
    show_deleted: bool = False,
) -> list[ItemResponse]:

    filter = lambda info: all(
        [
            min_price is None or info.price >= min_price,
            max_price is None or info.price <= max_price,
            show_deleted or not info.deleted,
        ]
    )

    response = [
        ItemResponse.from_entity(entity)
        for entity in store.get_many_items(offset, limit, filter)
    ]

    return response


@router.put("/{id}")
async def put_item(id: int, request: ItemRequest) -> ItemResponse:
    info = request.as_item_info()
    item = store.replace_item(id, info)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {id} not found",
        )
    return ItemResponse.from_entity(item)


@router.patch("/{id}")
async def patch_item(id: int, request: PatchItemRequest) -> ItemResponse:
    patch_info = request.as_patch_item_info()
    item = store.update_item(id, patch_info)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {id} not found"
        )

    if item.info.deleted:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED, detail=f"Item {id} is deleted"
        )

    return ItemResponse.from_entity(item)


@router.delete("/{id}")
async def delete_item(id: int) -> Response:
    deleted = store.delete_item(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {id} not found",
        )

    return Response("")
