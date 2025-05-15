#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the entry point of the task."""

import asyncio
from typing import Iterator, Iterable

from data_loader import AbstractDataLoader, DataLoaderFactory, pl, logging
from doc_processor import AbstractAsyncDocProcessor, DocumentProcessorFactory


class Main:
    """Main job runner"""

    def __init__(
        self, doc_processor: AbstractAsyncDocProcessor, dl: AbstractDataLoader
    ):
        """Initialise the main with document processor."""
        self._dp_: AbstractAsyncDocProcessor = doc_processor
        self._dl_: AbstractDataLoader = dl
        logging.debug(msg="Document processor and data loader initialised at main.")

    async def run(self):
        """Run the job for all documents asynchronously."""
        # Insert the raw data first
        await self._dp_.insert_raw_data(df=self._dl_.fetch_raw_data())
        data: pl.DataFrame = await self._dl_.fetch_latest_data().collect_async()
        tasks: Iterator[asyncio.Task] = map(
            lambda doc: asyncio.create_task(coro=self._dp_.process_doc(document=doc)),
            data.iter_rows(named=True),
        )
        results: Iterable[int] = await asyncio.gather(*tasks)
        logging.info(msg=f"{sum(results)} named entities persisted on the database.")


if __name__ == "__main__":
    asyncio.run(
        main=Main(
            doc_processor=DocumentProcessorFactory().get_document_processor(),
            dl=DataLoaderFactory().get_data_loader(),
        ).run()
    )
