#!/usr/bin/env python3
# encoding: utf-8

"""
Asynchronous gateway interface to expose the named entity recogniser

For development, start it by
    $ uvicorn gateway:app --host=0.0.0.0 --port=8081 --reload

Skip the reload option above in containerised production environment to exploit
concurrent processing and withstand moderate user traffic.

Author: Barman Roy, Swagato
"""

import re
from typing import Sequence
from urllib.parse import unquote

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from model_interface import (
    FrozenSet,
    NERResult,
    AbstractNERInterface,
    ModelFactory,
    logging,
    DEFAULT_LABELS,
)

DESCRIPTION: str = """
A named entity recogniser application 

# Clients

You will be able to POST 
* text body (mandatory)
* labels (optional)
* threshold confidence (optional)


and get a collection of named entities with metadata (position, label, confidence). 
"""

app: FastAPI = FastAPI(
    title="Named Entity Recogniser",
    description=DESCRIPTION,
    contact=dict(name="Barman Roy, Swagato", email="swagatopablo@aol.com"),
)
origins = ["*"]
# noinspection PyTypeChecker
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=origins,
)
MODEL_WRAPPER: AbstractNERInterface = ModelFactory().get_model_wrapper()


@app.post(path="/extract_entities/")
async def extract(
    text: str = Query(default="", description="Text body to extract entities from"),
    labels: FrozenSet[str] = Query(
        default=DEFAULT_LABELS, description="Relevant labels for the application"
    ),
    threshold: float = Query(
        default=0.5,
        ge=0,
        le=1,
        description="Confidence threshold to detect named entities",
    ),
) -> Sequence[NERResult]:
    """
    Get the recognised entities with metadata. These are the parameters.
    Parameters:
            text: The text body to extract named entities from
            labels: The labels to extract, for example, a collection of entities like person, companies etc.
            threshold: Minimal confidence score to identify an entity. Higher value means you will get fewer results.
    """
    logging.info(
        msg=f"Got text of length {len(text)} with labels {labels} and confidence {threshold} on the ASGI"
    )

    # The text might be url encoded. Detect it with a regex and correct if so
    text = (
        unquote(string=text)
        if re.search(pattern=r"%[0-9A-Fa-f]{2}", string=text)
        else text
    )
    return tuple(MODEL_WRAPPER.extract(text=text, labels=labels, threshold=threshold))
