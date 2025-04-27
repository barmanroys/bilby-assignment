#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the abstract interface and implementation of a data loader."""

from data_loader import config, ABC, abstractmethod, logging, pl
from contextlib import AbstractAsyncContextManager
import httpx
from urllib.parse import urlunparse, urlencode, quote
from typing import Dict

# Silence verbose logs from httpx
logging.getLogger(name="httpx").setLevel(level=logging.WARNING)

# Service details
DEFAULT_HOST: str = config.get(section="ner_service", option="HOST")
DEFAULT_PORT: int = int(config.get(section="ner_service", option="PORT"))
DEFAULT_ROUTE: str = config.get(section="ner_service", option="ROUTE")

# Database schema details
START_COL: str = config.get(section="columns", option="START")
END_COL: str = config.get(section="columns", option="END")
ENT_TEXT_COL: str = config.get(section="columns", option="ENT_TEXT")
ENT_TYPE_COL: str = config.get(section="columns", option="ENT_TYPE")
SCORE_COL: str = config.get(section="columns", option="SCORE")


class AbstractNERClient(ABC):
    """Abstract definition of an NER client."""

    @abstractmethod
    async def get_entities_from_body(self, text: str) -> pl.LazyFrame:
        """Get the entities from the body based on the NER model output"""
        raise NotImplementedError


class ResponseContext(AbstractAsyncContextManager):
    """Wraps the asynchronous response inside a client to respect RAII."""

    def __init__(self, r: httpx.Response):
        """Initialise with the raw response"""
        self.response: httpx.Response = r
        self.path: str = self.response.url.path
        logging.debug(msg=f"Response context initiated with {self.path}")

    async def __aenter__(self) -> httpx.Response:
        """Acquire the resource."""
        logging.debug(msg=f"Opened response context for {self.path}")
        return self.response

    async def __aexit__(self, exception_type, exception_value, traceback) -> None:
        """Release the resource"""
        await self.response.aclose()
        logging.debug(msg=f"Closed response context for {self.path}")


class RemoteNERClient(AbstractNERClient):
    """
    Implement the named entity recogniser via Remote NER call. This choice is made to avoid loading the Gliner
    model as part of the same process running the main pipeline.
    """

    def __init__(self, host: str, port: int, route: str):
        """Initialise to store the URL details to make API calls."""
        self._host_: str = host
        self._port_: int = port
        self._route_: str = route

    async def get_entities_from_body(self, text: str) -> pl.LazyFrame:
        """Get the extracted entities from a text in the form of a dataframe."""
        protocol: str = "http"
        url: str = urlunparse(
            components=(
                protocol,
                f"{self._host_}:{self._port_}",
                self._route_,
                "",
                "",
                "",
            )
        )
        param_key: str = "text"  # The NER service accepts this named parameter
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout=60, connect=60)
        ) as client:
            async with ResponseContext(
                r=await client.post(
                    url=url, params=urlencode(query={param_key: quote(string=text)})
                )
            ) as response:
                # The NER service has different field names from the MySQL database. Hence, the mapping
                column_mapping: Dict[str, str] = {
                    "start": START_COL,
                    "end": END_COL,
                    "text": ENT_TEXT_COL,
                    "label": ENT_TYPE_COL,
                    "score": SCORE_COL,
                }
                # Deduplicate the same entity if it appears multiple times
                return (
                    pl.LazyFrame(data=response.json())
                    .rename(mapping=column_mapping)
                    .unique(subset=ENT_TEXT_COL)
                )


class NERClientFactory:
    """Factory class to initialise the NER client."""

    def __init__(self):
        """Initialise with the defaults."""
        self._host_: str = DEFAULT_HOST
        self._port_: int = DEFAULT_PORT
        self._route_: str = DEFAULT_ROUTE

    def get_ner_client(self) -> AbstractNERClient:
        """Get the remote NER client based on default service configurations."""
        return RemoteNERClient(host=self._host_, port=self._port_, route=self._route_)
