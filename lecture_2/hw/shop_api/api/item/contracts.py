from pydantic import BaseModel, ConfigDict, NonNegativeFloat
from ...store.models import *


class ItemRequest(BaseModel):
    name: str
    price: NonNegativeFloat
    deleted: bool = False

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(
            name=self.name,
            price=self.price,
            deleted=self.deleted,
        )


class PatchItemRequest(BaseModel):
    name: str | None = None
    price: NonNegativeFloat | None = None

    model_config = ConfigDict(extra="forbid")

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)


class ItemResponse(BaseModel):
    id: int
    name: str
    price: NonNegativeFloat
    deleted: bool

    @staticmethod
    def from_entity(entity: ItemEntity) -> "ItemResponse":
        return ItemResponse(
            id=entity.id,
            name=entity.info.name,
            price=entity.info.price,
            deleted=entity.info.deleted,
        )
