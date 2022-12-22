from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List, Optional, Type, Union
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.ext.sqlmodel import paginate as sqlmodel_paginate
from pydantic.dataclasses import dataclass
from sqlmodel import Session
from sqlmodel.main import SQLModelMetaclass
from sqlmodel.sql.expression import SelectOfScalar

from core.db import get_session
from utils.base_serailizer import BaseResponseSerializer


class BaseModelMixin(ABC):
    """
    model: SQLModel
        Model to work with data
    serializer_class: SQLModel
        Model to serialize data
    base_url: str
        Url for work with list and create methods
    detail_url: str
        Url for work with detail, update, delete methods
    response_class: dataclass
        Serializer for response view
    """

    request: Request

    def __init__(self, session: Session = Depends(get_session)):
        self.db = session

    @property
    @abstractmethod
    def model(self) -> Type[SQLModelMetaclass]:
        pass

    @property
    def searching_fields(self):
        return

    def get_queryset(self) -> Optional[SelectOfScalar]:
        """By default returns original queryset."""
        return getattr(self, "queryset", None)

    @property
    @abstractmethod
    def serializer_class(self) -> Type[dataclass]:
        pass

    @property
    @abstractmethod
    def response_class(self) -> Type[BaseResponseSerializer]:
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @property
    @abstractmethod
    def detail_url(self) -> str:
        pass

    @staticmethod
    def dc2dict(dc: dataclass) -> dict:
        """
        Convert Dataclass to dict

        :param dc: dataclass
        :return: dict
        """

        return {
            n: getattr(dc, n)
            for n in dc.__dataclass_fields__
            if getattr(dc, n) is not None
        }

    @staticmethod
    def valid_response(data: SQLModelMetaclass) -> Optional[SQLModelMetaclass]:
        """
        Validate data for Not found
        Parameters
        ----------
        data : SQLModel
            id for special row
        Returns
        -------
        results : Object or 404

        """
        if data is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return data

    def get(
        self,
        params: dataclass,
        page_params: Optional[AbstractParams] = None,
        queryset: Optional[SelectOfScalar] = None,
    ) -> Union[List[Optional[SQLModelMetaclass]], AbstractPage]:
        """
        Get all object from db

        Parameters
        ----------
        params: dataclass
            Parameters model will be filtered by.
        page_params: Optional[AbstractParams]
            If given, model will be paginated using them
        queryset: Optional[SelectOfScalar]
            If given, response returned using custom queryset

        Returns
        -------
        List of objects or page

        """
        dict_params = self.dc2dict(params)
        queryset = queryset if queryset is not None else self.get_queryset()
        # NOTE: this if is redundant, page_params have defaults so it's always True
        # in future when front needs add unpaginated responses
        if page_params:
            query = self.model.objects.filter(
                query=queryset,
                should_be_executed=False,
                searching_fields=self.searching_fields,
                **dict_params,
            )
            return sqlmodel_paginate(session=self.db, query=query, params=page_params)
        query = self.model.objects.filter(
            query=queryset, searching_fields=self.searching_fields, **dict_params
        )
        return query

    def detail(self, id_: UUID) -> Union[None, SQLModelMetaclass]:
        """
        Get all object from db

        Parameters
        ----------
        id_ : UUID
            id for special row

        Returns
        -------
        results : None or SQLModel object
        """
        queryset = self.get_queryset()
        return self.model.objects.get_or_404(query=queryset, id=id_)

    def post(self, params: dataclass) -> SQLModelMetaclass:
        """
        Save a new object to database
        Parameters
        ----------
        params : dataclass
            Dataclass which contain valid data for save

        Returns
        -------
        results : SQLModel object
        """

        return self.model.objects.create(**self.dc2dict(params))

    def bulk_post(self, save_list: List[dataclass]) -> List[SQLModelMetaclass]:
        """
        Validate and save multiple objects to database
        ----------
        save_list : list
            list which contains multiple objects to save

        Returns
        -------
        results : List of SQLModel objects
        """
        objects = [self.model(**self.dc2dict(params)) for params in save_list]
        # after committing it clears all the data from model so we pass a deep copy
        # because of this we severed model <-> db connection, but we don't need it anyway
        self.db.add_all(deepcopy(objects))
        self.db.commit()
        return objects

    def delete(self, id_: UUID) -> dict:
        """
        Delete the object from database
        Parameters
        ----------
        id_ : UUID
            id for special row

        Returns
        -------
        results : dict
        """
        queryset = self.get_queryset()
        return self.model.objects.delete(id=id_, query=queryset)

    def put(self, id_: UUID, params: dataclass) -> SQLModelMetaclass:
        """
        Update the object in database
        Parameters
        ----------
        id_ : UUID
            id for special row
        params : dataclass
            which contain valid data for update

        Returns
        -------
        results : SQLModel
        """
        queryset = self.get_queryset()
        model_exists = self.model.objects.exists(query=queryset, id=id_)
        if not model_exists:
            raise HTTPException(404, f"{self.model.__name__} with id={id_} not found.")
        return self.model.objects.update(id=id_, data_update=self.dc2dict(params))

    def bulk_put(self, save_list: List[dataclass]) -> List[SQLModelMetaclass]:
        """
        Update multiple objects in database
        Parameters
        ----------
        save_list : list of dataclasses
            which contain valid data for update
            *must contain and id for the entity to update
            in each object

        Returns
        -------
        results : list of updated SQLModels
        """
        mappings = [self.dc2dict(params) for params in save_list]
        self.db.bulk_update_mappings(self.model, mappings)
        self.db.commit()
        models_to_return = [self.model(**params) for params in mappings]
        return models_to_return
