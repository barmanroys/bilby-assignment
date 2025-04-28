#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the abstract interface to asynchronously process each document supplied by data loader."""

from data_loader import ABC, abstractmethod, CONCAT_TITLE_COL, UUID_COL
from db_interface import (
    AbstractPersistenceInterface,
    PersistenceClientFactory,
    logging,
    pl,
)
from matching_interface import AbstractEntityMatcher, EntityMatcherFactory
from ner_client import Dict, AbstractNERClient, NERClientFactory


class AbstractAsyncDocProcessor(ABC):
    """Abstract asynchronous document processor interface."""

    @abstractmethod
    async def process_doc(self, document: Dict[str, str]) -> int:
        """
        Asynchronously process the row including named entity extraction, SoT matching, and database persistence
        Example of a document is

        document={'title': 'Steve Jobs released the new iPhone on Apple Inc AGM in California',
                   'uuid': '550e8400-e29b-41d4-a716-446655440000'
        }

        Return the number of rows inserted.
        """
        raise NotImplementedError

    @abstractmethod
    async def insert_raw_data(self, df: pl.LazyFrame) -> None:
        """This function is for inserting the raw document data to the database."""
        raise NotImplementedError


class AsyncDocProcessor(AbstractAsyncDocProcessor):
    """Abstract asynchronous document processor interface."""

    def __init__(
        self,
        ner_client: AbstractNERClient,
        matcher: AbstractEntityMatcher,
        rdb_client: AbstractPersistenceInterface,
    ):
        """Initialise with appropriate components."""
        self._ner_client_: AbstractNERClient = ner_client
        self._matcher_: AbstractEntityMatcher = matcher
        self._rdb_client_: AbstractPersistenceInterface = rdb_client

    async def process_doc(self, document: Dict[str, str]) -> int:
        """
        Asynchronously process the row including named entity extraction, SoT matching, and database persistence
        Example of a document is

        document={'title': 'Steve Jobs released the new iPhone on Apple Inc AGM in California',
                   'uuid': '550e8400-e29b-41d4-a716-446655440000'
        }
        """
        # Steps to perform
        # Call to ner
        # Match extracted entities with SoT entities
        # Add the UUID as a column
        # Persist in the database

        text: str = document[CONCAT_TITLE_COL]
        document_id: str = document[UUID_COL]
        logging.debug(
            msg=f"Starting to process document {document_id} having {len(text)} characters."
        )
        try:
            result: pl.LazyFrame = await self._ner_client_.get_entities_from_body(
                text=text
            )
            matched_entity_results: pl.DataFrame = (
                self._matcher_.match_entities_with_sot(
                    result=await result.collect_async()
                ).with_columns(pl.lit(value=document_id).alias(name=UUID_COL))
            )
            row_count: int = self._rdb_client_.persist_ner_results(
                results=matched_entity_results
            )
            logging.info(
                msg=f"Finished processing {document_id} having {len(text)} characters."
            )
            return row_count
        except Exception as e:
            logging.error(
                msg=f"Document id {document_id} failed because of {e}",
                exc_info=True,
                stack_info=True,
                stacklevel=2,
            )
            return 0

    async def insert_raw_data(self, df: pl.LazyFrame) -> None:
        """This function is for inserting the raw document data to the database."""
        self._rdb_client_.persist_raw_data(data=await df.collect_async())
        logging.info(msg=f"Raw data persisted on the MySQL table.")


class DocumentProcessorFactory:
    """Factory class to get a document processor."""

    def __init__(
        self,
        ner_factory: NERClientFactory = NERClientFactory(),
        matcher_factory: EntityMatcherFactory = EntityMatcherFactory(),
        db_client_factory: PersistenceClientFactory = PersistenceClientFactory(),
    ):
        """Initialise the factory with the component factories."""
        self._ner_client_: AbstractNERClient = ner_factory.get_ner_client()
        self._matcher_: AbstractEntityMatcher = matcher_factory.get_entity_matcher()
        self._rdb_client_: AbstractPersistenceInterface = db_client_factory.get_client()

    def get_document_processor(self) -> AbstractAsyncDocProcessor:
        """Get the document processor based on the components."""
        return AsyncDocProcessor(
            ner_client=self._ner_client_,
            matcher=self._matcher_,
            rdb_client=self._rdb_client_,
        )
