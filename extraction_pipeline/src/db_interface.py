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
    def persist_ner_results(self, results: pl.DataFrame) -> None:
        """Persist the results in the database."""
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

    def persist_ner_results(self, results: pl.DataFrame) -> None:
        """Persist the result containing the document UUID, extracted entities and matched entities with SoT"""

        document_id: str = next(iter(results.select(pl.col(name=UUID_COL)).to_series()))
        # Cast the UUID column as binary data to match the database schema
        results = results.with_columns(
            pl.col(name=UUID_COL).map_elements(
                function=lambda doc_id: uuid.UUID(hex=doc_id).bytes,
                return_dtype=pl.Binary,
            )
        )
        try:
            with self._engine_ as engine:
                row_count: int = results.write_database(
                    table_name=self._table_name_,
                    connection=engine,
                    if_table_exists="append",
                )
            logging.info(
                msg=f"{row_count} rows inserted into {self._table_name_} for document {document_id}."
            )
        except Exception as e:
            # Catch a broad exception for external dependencies
            logging.error(
                msg=f"Document {document_id} encountered error {e}.",
                exc_info=True,
                stack_info=True,
                stacklevel=2,
            )


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
