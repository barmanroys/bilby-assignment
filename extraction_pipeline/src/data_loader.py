#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the abstract interface and implementation of a data loader."""

from abc import ABC, abstractmethod
import logging, os
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
    def fetch_latest_data(self) -> pl.LazyFrame:
        """Fetch the latest data in the form of a dataframe."""
        raise NotImplementedError


class DiskDataLoader(AbstractDataLoader):
    """
    Mock the data source with a parquet file.
    A production data loader will be more involved, scraping data from cloud bucket/database if necessary, but it should
    follow the same method signature. Following the clean architecture principle, the data source is a detail.
    """

    def __init__(self, path: str = os.path.join(DATA_DIR, DOC_SOURCE)):
        """Supply the data path."""
        self._data_file_: str = path

    def fetch_latest_data(self) -> pl.LazyFrame:
        """
        Fetch the latest data by reading the parquet file.
        The downstream process needs only the UUID and the body. To form the body, we have concatenated the title and
        body in both languages (English and Chinese). The rest of the columns
        are discarded from any downstream processing.
        """
        result: pl.LazyFrame = pl.scan_parquet(source=self._data_file_).select(
            pl.col(
                UUID_COL, EN_TITLE_COL, SOURCE_TITLE_COL, EN_BODY_COL, SOURCE_BODY_COL
            )
        )
        return result.with_columns(
            pl.concat_str(
                exprs=pl.col(
                    EN_TITLE_COL, EN_BODY_COL, SOURCE_TITLE_COL, SOURCE_BODY_COL
                )
            ).alias(name=CONCAT_TITLE_COL)
        ).select(pl.col(UUID_COL, CONCAT_TITLE_COL))
