#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the abstract interface and implementation of a database interface for NER result persistence."""

from data_loader import ABC, abstractmethod, pl


class AbstractPersistenceInterface(ABC):
    """Define the interface to persist data."""

    @abstractmethod
    def persist_ner_results(self, results: pl.DataFrame) -> None:
        """Persist the results in the database."""
        raise NotImplementedError
