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

from typing import Sequence
import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from model_interface import FrozenSet, NERResult, AbstractNERInterface, ModelFactory, Iterator, config, logging

DESCRIPTION: str = """
A named entity recogniser application 

# Clients

You will be able to POST 
* text body (mandatory)
* labels (optional)
* threshold confidence (optional)


and get a collection of named entities with metadata (position, label, confidence). 
"""

app: FastAPI = FastAPI(title='Named Entity Recogniser',
                       description=DESCRIPTION,
                       contact=dict(name='Barman Roy, Swagato',
                                    email='swagatopablo@aol.com'))
origins = ['*']
# noinspection PyTypeChecker
app.add_middleware(middleware_class=CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=origins,
                   allow_headers=origins)





@app.post(path='/extract_entities/')
async def extract(
    text: str = Query(default='', description='Text body to extract entities from'),
    labels: FrozenSet[str] = Query(default=frozenset(('Person', 'Company', 'Location')), description='Relevant labels for the application'),
    threshold: float = Query(default=.5, ge=0, le=1, description='Confidence threshold to detect named entities')) -> Sequence[NERResult]:
    """Get the recognised entities with metadata."""
    logging.info(msg=f'Got text of length {len(text)} with labels {labels} and confidence {threshold} on the ASGI')
    model_wrapper:AbstractNERInterface=ModelFactory().get_model_wrapper()
    result:Iterator[NERResult]=model_wrapper.extract(text=text, labels=labels, threshold=threshold)
    return tuple(result)



if __name__ == '__main__':
    file: str = os.path.basename(p=__file__).split(sep='.')[0]
    appname: str = f'{file}:app'
    host:str=config.get(section='asgi', option='HOST') # Expose the service to the network via 0.0.0.0
    port:int=int(config.get(section='asgi', option='PORT'))
    run(app=appname, host=host, port=port, workers=os.cpu_count())