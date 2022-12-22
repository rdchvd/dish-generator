from copy import copy
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException
from sqlalchemy import and_, func, or_
from sqlalchemy.engine import Inspector
from sqlalchemy.sql.elements import BooleanClauseList
from sqlmodel import Session, select
from sqlmodel.main import SQLModel, SQLModelMetaclass
from sqlmodel.sql.expression import SelectOfScalar

from core.db import get_inspector, get_session


class ModelManager:
    def __init__(
        self,
        session: Session = next(get_session()),
        inspector: Inspector = get_inspector(),
        model: Optional[SQLModelMetaclass] = None,
    ):
        self.db = session
        self.model = model
        self.inspector = inspector
        self.custom_fields = False
        self.fields = self.__all_field()

    # TODO write method to check foreign key

    def __all_field(self) -> tuple:
        """
        Generate default fields

        Parameters
        ----------
        Returns
        -------
        Tuple model
        """
        return (self.model,)

    def __process_query(self, query) -> List[Any]:

        """
        Execute query

        Parameters
        ----------
        query
        Returns
        -------
        List values
        """
        result = self.db.execute(query)
        if not self.custom_fields:
            result = result.scalars()
        return result.all()

    @staticmethod
    def __get_class_by_tablename(table_fullname: str) -> Optional[object]:
        """Returns the class model object using table name.
        Parameters
        ----------
        table_fullname: str
            The full name of the table
        Returns
        -------
        The class object of the table or None.
        """
        BaseModel = SQLModel.__subclasses__()[0]
        for _class in BaseModel.__subclasses__():
            if (
                hasattr(_class, "__table__")
                and _class.__table__.fullname == table_fullname
            ):
                return _class
        return

    def __filter_by_kwargs(self, **kwargs) -> BooleanClauseList:
        """Makes filter_by functionality but filters the base model instead of the joined ones."""

        filtering_queries = []
        for field_name, value in kwargs.items():
            field = getattr(self.model, field_name)
            filtering_queries.append(field.__eq__(value))
        return and_(*filtering_queries)

    def values(self, *args) -> object:

        """
        Generate special fields

        Parameters
        ----------
        Returns
        -------
        Tuple special fields
        """

        self.fields = args
        self.custom_fields = True
        return self

    def all(self) -> List[Optional[SQLModelMetaclass]]:
        """Returns a list of all the rows in the table

        Parameters
        ----------
        Returns
        -------
        A list of all the rows in the table.
        """
        return self.db.execute(select(self.model)).scalars().all()

    def filter_in(
        self, field_name: str, list_values: list[str]
    ) -> list[Optional[SQLModelMetaclass]]:
        """
        Filter instances by given list. If instance.field_name in list_values

        :param field_name: name for filtering
        :param list_values: values
        :return: list
        """
        query = select(self.fields).where(
            getattr(self.fields[0], field_name).in_(list_values)
        )
        return self.__process_query(query)

    def sort(self, query: SelectOfScalar, ordering_values: str) -> SelectOfScalar:
        """Takes a query and a string of field names, and returns a query that is sorted by those fields.

        Parameters
        ----------
        query: SelectOfScalar
            The query to sort
        ordering_values: str
            The value of the ordering query parameter
        Returns
        -------
        A query object.
        """
        direction = "desc" if ordering_values.startswith("-") else "asc"
        order_by_queries = []
        for field_name in ordering_values.split(","):
            field_name = field_name.replace("-", "").replace("+", "")
            order_by_field = getattr(self.model, field_name, None)
            if not order_by_field:
                raise HTTPException(
                    status_code=400,
                    detail=f"{self.model.__name__} has no `{field_name}` field.",
                )
            # add direction and field to query
            order_by_queries.append(getattr(order_by_field, direction)())
        # order by all fields in direction
        return query.order_by(*order_by_queries)

    def partial_match_filter(
        self, query: SelectOfScalar, search_term: str, searching_fields: List[str]
    ) -> SelectOfScalar:
        """Returns a query that filters the results to only those that contain the search term in any of the searching_fields

        Parameters
        ----------
        query: SelectOfScalar
            The query object that's being filtered
        search_term: str
            The string that the user is searching for
        searching_fields: List[str]
            A list of fields to search
        Returns
        -------
        A query object
        """
        searching_and_queries = []
        for bit in search_term.lower().split():
            searching_or_queries = []
            for field_name in searching_fields:
                field = getattr(self.model, field_name)
                # func.lower() makes search case-insensitive
                searching_or_queries.append(func.lower(field).contains(bit))
            # add to list queries like `field_1 like '%bit_1%' or field_2 like '%bit_1%' or ...`
            searching_and_queries.append(or_(*searching_or_queries))
        # filter using queries like `(field_1 like '%bit_1%' or ...) and (field_1 like '%bit_2%' or ...) ...`
        return query.filter(and_(*searching_and_queries))

    def filter(
        self,
        query: Optional[SelectOfScalar] = None,
        group_by: Optional[str] = None,
        should_be_executed: Optional[bool] = True,
        searching_fields: Optional[List[Optional[str]]] = None,
        **kwargs,
    ) -> Union[List[Any], SelectOfScalar]:
        """Filters the query by the keyword arguments passed in.

        Parameters
        ----------
        query: Optional[SelectOfScalar]
            The query object that's being filtered
        group_by: Optional[str]
            If given, query will be grouped by given value
        should_be_executed: Optional[bool]
            If False, query wouldn't be executed
        searching_fields: Optional[List[Optional[str]]]
            Set of fields could be filtered by partial match
        Returns
        -------
        List or SelectOfScalar
        """
        search_term = kwargs.pop("search", None)
        ordering_values = kwargs.pop("order_by", None)

        # get query from queryset or if no one given, select all model rows
        if query is None:
            query = select(self.fields)
        query = query.filter(self.__filter_by_kwargs(**kwargs))

        # if search in request and viewset contains `searching_fields`, filter by partial match
        if search_term and searching_fields:
            query = self.partial_match_filter(query, search_term, searching_fields)
        # group query by field if needed
        if group_by:
            query = query.group_by(group_by)

        # if order_by in request, sort query using it
        if ordering_values:
            query = self.sort(query, ordering_values)

        if not should_be_executed:
            return query
        return self.__process_query(query)

    def create(self, **kwargs) -> SQLModelMetaclass:
        """Creates a new instance.

        Parameters
        ----------

        Returns
        -------
        A SQLModel object
        """
        query = self.model(**kwargs)
        self.check_unique(query)
        self.check_values_fk(**kwargs)
        return self.save_model(query)

    def update(self, data_update: dict, **kwargs) -> SQLModelMetaclass:
        """Updates the model with the new values.

        Parameters
        ----------
        Returns
        -------
        The updated model
        """

        query = self.model.objects.filter(**kwargs)
        self.check_values_fk(**data_update)
        for row in query:
            # set values for unique checking
            for key, value in data_update.items():
                setattr(row, key, value)
            self.check_unique(row, is_update=True)
            # set values for db update
            for key, value in data_update.items():
                setattr(row, key, value)
            self.save_model(row)
        return query

    def delete(self, **kwargs) -> None:
        """Deletes object from the database.

        Parameters
        ----------
        """
        obj = self.get_or_404(**kwargs)
        self.db.delete(obj)
        self.db.commit()

    def delete_all(self, query: SelectOfScalar):
        """Deletes all the objects that match the given criteria.

        Parameters
        ----------
        query: SelectOfScalar
            Query to be deleted.
        """
        for obj in self.db.execute(query).scalars().all():
            self.db.delete(obj)
        self.db.commit()

    def save_model(self, query: SQLModelMetaclass) -> SQLModelMetaclass:
        """Saves the model to the database, commits the changes, and refreshes the model

        Parameters
        ----------
        query : SQLModel
           The query object to be saved
        Returns
        -------
        query: SQLModel
            The query is being returned.
        """
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)
        return query

    def exists(self, query: Optional[SelectOfScalar] = None, **kwargs) -> bool:
        """Returns True if the model exists in the database else False

         Parameters
        ----------
        model: Optional[SQLModel]
            The model to query. If not provided, the default model is used
        Returns
        -------
        A boolean value.
        """
        if query is None:
            query = select(self.fields)
        return bool(
            self.db.execute(query.filter(self.__filter_by_kwargs(**kwargs))).first()
        )

    def get_or_none(
        self, query: Optional[SelectOfScalar] = None, **kwargs
    ) -> Union[SQLModelMetaclass, None]:
        """Returns the row that matches the given criteria or None.

        Parameters
        ----------
        Returns
        -------
        A single row from the database.
        """
        if query is None:
            query = select(self.fields)
        return (
            self.db.execute(query.filter(self.__filter_by_kwargs(**kwargs)))
            .scalars()
            .one_or_none()
        )

    def get_or_404(
        self, error_message: Optional[str] = None, **kwargs
    ) -> Optional[SQLModelMetaclass]:
        """Returns the row  that matches the given criteria or raises 404.

        Parameters
        ----------
        error_message: Optional[str]
            Error message shown if 404 raised.
        Returns
        -------
        A single row from the database.
        """
        result = self.get_or_none(**kwargs)
        if not result:
            if not error_message:
                error_message = f"{self.model.__name__} not found."
            raise HTTPException(status_code=404, detail=error_message)
        return result

    def check_unique(
        self, query: SQLModelMetaclass, is_update: Optional[bool] = False
    ) -> None:
        """Checks if the query with unique constraints already exists in the database.

        Parameters
        ----------
        query: SQLModel
            The model instance to check for uniqueness
        is_update: Optional[bool]
            A boolean value that tells if the query is an update or not, defaults to False
        """

        # list of unique constraints of the model.
        unique_constraints = self.inspector.get_unique_constraints(
            self.model.__tablename__
        )
        if not unique_constraints:
            return
        query_dict = copy(query.dict())
        # refresh query to skip new model values while checking
        if is_update:
            self.db.refresh(query)
        for constraint in unique_constraints:
            columns = constraint.get("column_names")
            # dict with unique columns and values
            column_dict = {
                key: value
                for key, value in query_dict.items()
                if key in columns and value
            }
            if column_dict:
                existing_model = self.get_or_none(**column_dict)
            # check if the other model with same values exists
            if (
                column_dict
                and existing_model
                and existing_model.id != query_dict.get("id")
            ):
                raise HTTPException(
                    status_code=400, detail=f"{self.model.__name__} already exists."
                )
        return

    def check_values_fk(self, **kwargs: Dict[str, Any]) -> None:
        """Checks if the foreign key value exists in the database.
        Parameters
        ----------
        kwargs: Dict[str, Any]
            Object values dict
        Returns
        -------
        """
        foreign_keys = self.inspector.get_foreign_keys(self.model.__tablename__)
        for fk in foreign_keys:
            constrained_column = fk["constrained_columns"][0]
            referred_column = fk["referred_columns"][0]
            if constrained_column not in kwargs:
                continue

            FKClass = self.__get_class_by_tablename(fk["referred_table"])
            FKClass.objects.get_or_404(**{referred_column: kwargs[constrained_column]})
        return

    def get_or_create(self, **kwargs) -> SQLModelMetaclass:
        """If the model exists, returns it else creates one

        Parameters
        ----------
        Returns
        -------
        SQLModel
        """
        obj = self.get_or_none(**kwargs)
        return obj if obj else self.create(**kwargs)

    def update_or_create(self, data_update: dict, **kwargs) -> SQLModelMetaclass:
        """If the query exists, updates it, otherwise creates it.

        Parameters
        ----------
        data_update: dict
            Data that the object must have.
        Returns
        -------
        A SQLModel object
        """
        query = self.update(data_update, **kwargs)
        if not query:
            query = self.create(**dict(kwargs, **data_update))
        return query

    def exists_all(self, field_name: str, values_to_check: List[Any], **kwargs) -> bool:
        """Checks if db has all models with fields that were passed.
           So doing exists_all(field_name='id', [1, 2]) will check are
           there models in database with ids 1 and 2.

        Parameters
        ----------
        ids_to_check: list
            ids that we want to check.
        Returns
        -------
        bollean
        """
        query = self.db.exec(
            select(func.count(self.model.id)).where(
                getattr(self.model, field_name).in_(values_to_check)
            )
        ).one()

        return len(values_to_check) == query
