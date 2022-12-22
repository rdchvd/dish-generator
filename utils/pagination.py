from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from fastapi_pagination import Params, set_page
from fastapi_pagination.bases import AbstractPage, AbstractParams
from pydantic import conint

T = TypeVar("T")


class Page(AbstractPage[T], Generic[T]):
    """Pagination container class with enabled lazy relations lookups
    if you want that functionality: in your view just replace fastapi_pagination.Page with this Page"""

    # Just a copy of class 'fastapi_pagination.Page'
    # because just inheriting from it raises cryptic errors
    items: Sequence[T]
    total: conint(ge=0)
    page: conint(ge=1)
    size: conint(ge=1)

    __params_type__ = Params

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ) -> Page[T]:
        if not isinstance(params, Params):
            raise ValueError("Page should be used with Params")

        return cls(
            total=total,
            items=items,
            page=params.page,
            size=params.size,
        )

    class Config:
        # just a copied value from parent config
        arbitrary_types_allowed = True
        # on paginated responses enable lazy loading fk objects
        read_with_orm_mode = True
        orm_mode = True


# set custom Page class for pagination
set_page(Page)
