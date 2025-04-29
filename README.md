## Goal

The project reads the raw document data (containing title, unique document id and several other attributes)
to recognise the named entities and inserts the recognised entities into a MySQL database.
The named entity recognition task is isolated from the main pipeline by a containerised service interface.

##### Infrastructure Requirements

Make sure you got

* recent versions
  of [Docker daemon, compose and CLI](https://docs.docker.com/get-started/overview/) installed.
  The development version is Docker 28.1.1.
* [UV package manager](https://github.com/astral-sh/uv)
* a POSIX environment (I tested on Ubuntu 24.04) with the following variables set appropriately for your
  scripts/container to access them

| Environment <br/> Variable | Value
|----------------------------|---------------------------------------------------------|
| MYSQL_DATABASE             | `db`                                                    |
| USER                       | Usual POSIX user name, will be used for database access |
| MYSQL_PASSWORD             | Any value you want                                      |
| NER_HOST                   | `ner`                                                   |
| MYSQL_HOST                 | `database`

With this setup, if you run the following from the Git root repository.

```shell
docker compose up
```

This should

* fire up the local MySQL service with the above username and password
* initialise the database with appropriate table definitions to accept data from the pipeline
* start the named entity recogniser as a containerised service

#### Effects of Running the Task

* Copy the raw document data to the MySQL database (this is intended to make the fields available in the same database). If the raw documents (identified by UUID) already exist, this phase is skipped.
* Run the named entity recogniser pipeline to insert the named entities (together with SoT matched entities) into the
  database in a separate table

A user can verify the results by logging into the database (exposed at port 3306 of the host) and checking the table.
You can use tools like DBeaver to access the database or go to the MySQL console by

```shell
mysql -h 127.0.0.1 -p
```

and keying in the password (set by the environment variable) when prompted.

#### Database Schema

The schema can be seen from the database initialisation script. Basically, two tables are created

* `documents`: Contains the raw documents data after converting the UUID to binary format.
* `extracted_entities`: Results of the NER pipeline with one row for each entity from each document.

Instead of merging them into the same table, the schema is partially normalised to avoid storing the long document
bodies multiple times for each entity. The unified view (combining document details and named entities) can be obtained
by

```sql
SELECT * FROM extracted_entities JOIN documents ON extracted_entities.uuid=documents.uuid;
```

#### Airflow Dag
The task is made available as an Airflow DAG in the `airflow_manager/dags` directory. The whole DAG has only one step, as the intermediate results are kept in process, which meets the requirement specified in the instruction.
