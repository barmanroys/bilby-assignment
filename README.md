## Goal

This branch migrates the database schema to use PostgreSQL. But remember, it uses the same environment variables as `master` branch using MySQL, whose names can be a little misleading.
##### Infrastructure Requirements

Make sure you got

* recent versions
  of [Docker daemon, compose and CLI](https://docs.docker.com/get-started/overview/) installed.
  The development version is Docker 28.1.1.
* [UV package manager](https://github.com/astral-sh/uv)
* pull access to the dockerhub images `barmanroys/ent-extraction` and `barmanroys/ner-service`
* a POSIX environment (I tested on Ubuntu 24.04) with the following variables set appropriately for your
  scripts/container to access them

| Environment <br/> Variable | Value
|----------------------------|---------------------------------------------------------|
| MYSQL_DATABASE             | `db`, name of the database to be created.                                                    |
| MYSQL_USER                       | $USER, the usual POSIX user name, will be used for database access |
| MYSQL_PASSWORD             | Any value you want, but without space or special characters                                      |
| NER_HOST                   | `ner`, the service name for named entity recognition                                                    |
| MYSQL_HOST                 | `database`, the service name for the MySQL database

With this setup, if you run the following from the Git root repository.
