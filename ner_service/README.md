#### Goal

NER Service with Gliner model.

#### Application

Basically, an HTTP wrapper around Gliner.

#### Start Up

Make sure you have docker compose set-up and run the following from the Git project root (after exposing port 8081).
```Shell
docker compose up
```
The OpenAPI documentation should be available [on your browser](http://127.0.0.1:8081/docs) to interact.

##### Note
The default compose stack starts the service at port 8081 of the container, but does not expose it to the host machine/end user. In production set up, the service is meant only for the ETL pipeline, not the end user.
