#!/usr/bin/env python3
# encoding: utf-8

"""Implementation of the entity matcher between the extracted entity and source of truth entities."""

import ast
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from data_loader import os, DATA_DIR
from ner_client import config, ABC, abstractmethod, pl, logging, ENT_TEXT_COL

# Columns related to the matching process
SOT_ID_COL: str = config.get(section="columns", option="SOT_NAME")
SOT_ALIAS_COL: str = config.get(section="columns", option="SOT_ALIASES")
MATCHED_ENT_ID_COL: str = config.get(section="columns", option="MATCHED_ENT_ID")
MATCHED_ENT_NAME_COL: str = config.get(section="columns", option="MATCHED_ENT_NAME")
MATCHED_COL: str = config.get(section="columns", option="MATCHED")


ENTITY_FILE: str = config.get(section="local_resource", option="ENTITY_FILE")


class AbstractEntityMatcher(ABC):
    """Abstract interface for the entity matcher."""

    @abstractmethod
    def match_entities_with_sot(self, result: pl.DataFrame) -> pl.DataFrame:
        """
        Match the entities by comparing extracted results with the source of truth.
        Pass the results from NER client to this method, and you will get a matched set of results against
        SoT entities.
        """
        raise NotImplementedError


class EntityMatcher(AbstractEntityMatcher):
    """The concrete entity matcher based on the static file"""

    def __init__(self, sot: pl.DataFrame):
        """Initialise the entity matcher with the given SoT."""
        self._sot_: pl.Dataframe = sot
        logging.debug(
            msg=f"Constructed the raw source of truth with {len(self._sot_)} entities."
        )

    @staticmethod
    def _row_transform_(row: Dict[str, str]) -> pl.DataFrame:
        """Transform each row to a dataframe with the aliases"""
        name: str = row[SOT_ID_COL]
        aliases: List[str] = ast.literal_eval(node_or_string=row[SOT_ALIAS_COL]) + [
            name
        ]
        return pl.DataFrame(
            data={
                MATCHED_ENT_ID_COL: [name] * len(aliases),
                MATCHED_ENT_NAME_COL: aliases,
            }
        )

    def _transform_sot_(self) -> pl.DataFrame:
        """Transform the SoT schema for effective matching."""
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
            return pl.concat(
                items=ex.map(
                    EntityMatcher._row_transform_, self._sot_.iter_rows(named=True)
                )
            )

    def match_entities_with_sot(self, result: pl.DataFrame) -> pl.DataFrame:
        """Match the entities by comparing extracted results with the source of truth."""
        sot: pl.DataFrame = self._transform_sot_()
        result = result.join(
            other=sot, how="left", left_on=ENT_TEXT_COL, right_on=MATCHED_ENT_NAME_COL
        )
        logging.debug(
            msg=f"Generating matching results for {len(result)} extracted entities against {len(sot)} SOT entities"
        )
        return result.with_columns(
            pl.when(pl.col(name=MATCHED_ENT_ID_COL).is_null())
            .then(statement=None)
            .otherwise(statement=pl.col(name=ENT_TEXT_COL))
            .alias(name=MATCHED_ENT_NAME_COL),
            pl.when(pl.col(name=MATCHED_ENT_ID_COL).is_null())
            .then(statement=False)
            .otherwise(statement=True)
            .alias(name=MATCHED_COL),
        )


class EntityMatcherFactory:
    """Factory class to get an entity matcher with the default data file."""

    def __init__(self, entity_file: str = os.path.join(DATA_DIR, ENTITY_FILE)):
        """Read the SoT from the entity file."""
        self._sot_path_: str = entity_file

    def get_entity_matcher(self) -> AbstractEntityMatcher:
        """Generate the entity matcher."""
        logging.debug(msg=f"Generating entity matcher based on {self._sot_path_}.")
        return EntityMatcher(sot=pl.read_parquet(source=self._sot_path_))
