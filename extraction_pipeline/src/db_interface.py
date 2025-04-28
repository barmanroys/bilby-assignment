#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the abstract interface and implementation of a database interface for NER result persistence."""

import uuid
from contextlib import AbstractContextManager
from typing import Optional, cast, Any

from sqlalchemy import Engine, create_engine

from data_loader import ABC, abstractmethod, pl, logging, UUID_COL, config, os


class AbstractPersistenceInterface(ABC):
    """Define the interface to persist data."""

    @abstractmethod
    def persist_raw_data(
        self, data: pl.DataFrame, table_name: str = "documents"
    ) -> None:
        """Persist raw data on a given table."""
        raise NotImplementedError

    @abstractmethod
    def persist_ner_results(self, results: pl.DataFrame) -> int:
        """Persist the results in the database and return the number of rows inserted"""
        raise NotImplementedError


class EngineContext(AbstractContextManager):
    """Wrap the connectivity engine inside a context to prevent leakage."""

    def __init__(self, uri: str):
        """
        Initialise the class with the connection string.
        Do not start the engine. Leave it to the context manager to acquire
        a connection.
        """
        self.uri: str = uri
        self.engine: Optional[Engine] = None

    def __enter__(self) -> Engine:
        """Create an engine and acquire the connection."""
        self.engine = create_engine(url=self.uri)
        logging.debug(msg=f"Engine created.")
        return cast(Engine, self.engine)

    def __exit__(
        self, exception_type: Any, exception_value: Any, traceback: Any
    ) -> None:
        """Release the connection."""
        cast(Engine, self.engine).dispose()
        logging.debug(msg="Engine disposed.")


class MySQLPersistenceClient(AbstractPersistenceInterface):
    """Implement the client to persist the results into MySQL"""

    def __init__(
        self,
        engine: EngineContext,
        table_name: str = config.get(section="db", option="TABLE"),
    ):
        """Initialise the client with an asynchronous engine."""
        self._engine_: EngineContext = engine
        self._table_name_: str = table_name
        # This expression is used to convert the UUID column to Binary for efficient storage.
        # It is kept as a variable here to avoid duplication inside the methods.
        self._converter_: pl.Expr = pl.col(name=UUID_COL).map_elements(
            function=lambda doc_id: uuid.UUID(hex=doc_id).bytes,
            return_dtype=pl.Binary,
        )

    def persist_raw_data(
        self, data: pl.DataFrame, table_name: str = "documents"
    ) -> None:
        """Use this method to persist the document data with full texts in the MySQL table."""
        with self._engine_ as engine:
            row_count: int = data.write_database(
                table_name=table_name,
                connection=engine,
                if_table_exists="append",
            )
            logging.debug(
                msg=f"{row_count} rows of raw data inserted into {table_name}"
            )

    def persist_ner_results(self, results: pl.DataFrame) -> int:
        """Persist the result containing the document UUID, extracted entities and matched entities with SoT"""

        document_id: str = next(iter(results.select(pl.col(name=UUID_COL)).to_series()))
        # Cast the UUID column as binary data to match the database schema
        results = results.with_columns(self._converter_)
        with self._engine_ as engine:
            row_count: int = results.write_database(
                table_name=self._table_name_,
                connection=engine,
                if_table_exists="append",
            )
            logging.debug(
                msg=f"{row_count} rows inserted into {self._table_name_} for document {document_id}."
            )
        return row_count


class PersistenceClientFactory:
    """Factory class to get a persistence client."""

    def __init__(
        self,
        host: str = os.environ["MYSQL_HOST"],
        dialect: str = config.get(section="db", option="DIALECT"),
        driver: str = config.get(section="db", option="DRIVER"),
        port: int = int(config.get(section="db", option="PORT")),
        user: str = os.environ["MYSQL_USER"],
        password: str = os.environ["MYSQL_PASSWORD"],
        db: str = os.environ["MYSQL_DATABASE"],
    ):
        """Initialise the database url with the supplied parameters."""
        connector = f"{dialect}+{driver}://{user}:{password}@{host}:{port}"
        self.uri: str = os.path.join(connector, db)
        logging.debug(msg=f"Factory initialised with database access details")

    def get_client(self) -> AbstractPersistenceInterface:
        """Get the MySQL client."""
        return MySQLPersistenceClient(engine=EngineContext(uri=self.uri))
