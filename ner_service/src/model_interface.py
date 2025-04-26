#!/usr/bin/env python3
# encoding: utf-8

"""This file presents the abstract interface and implementation of an NER Model."""

from configparser import ConfigParser
from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Iterator, FrozenSet
from gliner import GLiNER
import logging
from huggingface_hub.errors import LocalEntryNotFoundError

logging.basicConfig(
    format="%(asctime)s|%(levelname)s: %(message)s",
    datefmt="%H:%M:%S, %d-%b-%Y",
    level=logging.INFO,
)


# Load basic configurations and the default hugging face path
config: ConfigParser = ConfigParser()
assert config.read(filenames="config.ini")
HF_PATH: str = config.get(section="model", option="HF_PATH")
CACHE_DIR: str = config.get(
    section="model", option="LOCAL_PATH"
)  # Cache here to avoid repeated download

DEFAULT_LABELS: FrozenSet[str] = frozenset(("Person", "Company", "Location"))


class NERResult(BaseModel):
    """
    The result class from named entity recogniser.
    Attributes:
        start: Starting index of the recognised entity in the text.
        end: Ending index of the recognised entity in the text.
        text: Actual text of the recognised entity.
        label: Deduplicated labels indicating the type of entity (e.g. PERSON, ORGANIZATION).
        score: Threshold confidence score of the recognition, ranging from 0.0 to 1.0.
    """

    start: int
    end: int
    text: str
    label: str
    score: float


class AbstractNERInterface(ABC):
    """Abstract interface for the NER Model."""

    @abstractmethod
    def extract(
        self, text: str, labels: FrozenSet[str], threshold: float
    ) -> Iterator[NERResult]:
        """
        Extract the named entities
        Parameters:
            text: The text body to extract named entities from
            labels: The labels to extract, example, a collection of entities like person, companies etc.
            threshold: Minimal confidence score to identify an entity.
        """
        raise NotImplementedError


class GlinerClient(AbstractNERInterface):
    """Gliner implementation of the named entity recogniser."""

    def __init__(self, model: GLiNER):
        """Initialise the client with a raw model."""
        self._model_: GLiNER = model

    def extract(
        self, text: str, labels: FrozenSet[str] = DEFAULT_LABELS, threshold: float = 0.5
    ) -> Iterator[NERResult]:
        """Extract the named entities."""
        logging.debug(
            msg=f"Extracting entities from {text} for {labels} and threshold {threshold}."
        )
        return map(
            lambda entity: NERResult(**entity),
            self._model_.predict_entities(
                text=text, labels=labels, threshold=threshold
            ),
        )


class ModelFactory:
    """Model factory class for the downstream modules to get the model wrapper."""

    def __init__(self, hf_path: str = HF_PATH):
        """Initialise the model for caching."""
        try:
            # Look for a local model
            self._model_: GLiNER = GLiNER.from_pretrained(
                pretrained_model_name_or_path=hf_path,
                cache_dir=CACHE_DIR,
                local_files_only=True,
            )
            logging.debug(msg=f"Loaded model from {CACHE_DIR}")
        except LocalEntryNotFoundError:
            # Failing to find a local model, fetch from hugging face hub and cache locally
            self._model_: GLiNER = GLiNER.from_pretrained(
                pretrained_model_name_or_path=hf_path, cache_dir=CACHE_DIR
            )
            logging.debug(msg=f"Downloaded model from {hf_path}")

    def get_model_wrapper(self) -> AbstractNERInterface:
        """Get the NER Model client as a wrapper on the Gliner Model."""
        return GlinerClient(model=self._model_)
