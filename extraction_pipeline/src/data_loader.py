#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the abstract interface and implementation of a data loader."""

import logging
import os
from abc import ABC, abstractmethod
from configparser import ConfigParser

import polars as pl

logging.basicConfig(
    format="%(asctime)s|%(levelname)s: %(message)s",
    datefmt="%H:%M:%S, %d-%b-%Y",
    level=logging.INFO,
)

# Load basic configurations and the default hugging face path
config: ConfigParser = ConfigParser()
assert config.read(filenames="config.ini")

# Input columns
UUID_COL: str = config.get(section="columns", option="ID_COL")
EN_TITLE_COL: str = config.get(section="columns", option="EN_TITLE")
SOURCE_TITLE_COL: str = config.get(section="columns", option="SOURCE_TITLE")
EN_BODY_COL: str = config.get(section="columns", option="EN_BODY")
SOURCE_BODY_COL: str = config.get(section="columns", option="SOURCE_BODY")
CONCAT_TITLE_COL: str = config.get(section="columns", option="CONCAT_TITLE")

DATA_DIR: str = config.get(section="local_resource", option="DATA_DIR")
DOC_SOURCE: str = config.get(section="local_resource", option="DOC_SOURCE")


class AbstractDataLoader(ABC):
    """Load the latest data."""

    @abstractmethod
    def fetch_raw_data(self) -> pl.LazyFrame:
        """Fetch the raw data in the form of a dataframe to persist in the same database as NER result."""
        raise NotImplementedError

    @abstractmethod
    def fetch_latest_data(self) -> pl.LazyFrame:
        """Fetch the latest data in the form of a dataframe."""
        raise NotImplementedError


class DiskDataLoader(AbstractDataLoader):
    """
    Mock the data source with a parquet file.
    A production data loader will be more involved, scraping data from cloud bucket/database if necessary, but it should
    follow the same method signature. Following the clean architecture principle, the data source is a detail.
    """

    def __init__(self, path: str):
        """Supply the data path."""
        self._data_file_: str = path

    def fetch_latest_data(self) -> pl.LazyFrame:
        """
        Fetch the latest data by reading the parquet file.
        The downstream process needs only the UUID and the body. To form the body, we have concatenated the title and
        body in both languages (English and Chinese). The other columns are discarded from any downstream processing.
        """
        # Concatenate the four relevant columns to form a unified title column
        concatenator: pl.Expr = pl.concat_str(
            exprs=pl.col(EN_TITLE_COL, EN_BODY_COL, SOURCE_TITLE_COL, SOURCE_BODY_COL)
        ).alias(name=CONCAT_TITLE_COL)
        logging.debug(msg=f"Lazily scanning the data file from {self._data_file_}.")
        return self.fetch_raw_data().select(concatenator, pl.col(name=UUID_COL))

    def fetch_raw_data(self) -> pl.LazyFrame:
        """Fetch the raw data in the form of a dataframe to persist in the same database as NER result."""
        return pl.scan_parquet(source=self._data_file_)


class DataLoaderFactory:
    """Factory class to get a data loader."""

    def __init__(self, directory: str = DATA_DIR, file: str = DOC_SOURCE):
        """Initialise with the default values."""
        self._dir_: str = directory
        self._file_: str = file
        logging.debug(msg=f"Data loader factory initialised with {self._dir_}.")

    def get_data_loader(self) -> AbstractDataLoader:
        """Return the data loader."""
        return DiskDataLoader(path=os.path.join(self._dir_, self._file_))
