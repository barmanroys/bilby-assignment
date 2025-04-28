## Goal

The project reads the raw document data (containing title, unique document id and several other attributes)
to recognise the named entities and inserts the recognised entities into a MySQL database.
The named entity recognition task is isolated from the main pipeline by a containerised service interface.

#### Infra Setup

It is recommended to run the server inside a docker container to facilitate the dependency set-up.
Make sure you have recent versions
of <a href="https://docs.docker.com/get-started/overview/" target="_top">docker daemon and CLI</a> installed. The
current repository was tested on Docker version 28.1.1 running on Ubuntu 24.04. It is recommended to use a POSIX
compatible shell and have the following environment variables set up.

| Environment <br/> Variable | Value                                                   
|----------------------------|---------------------------------------------------------|
| MYSQL_DATABASE             | `db`                                                    | 
| USER                       | Usual POSIX user name, will be used for database access | 
| MYSQL_PASSWORD             | Any value you want                                      | 

With this setup, run the following from the Git root repository.

```shell
docker compose up
```

This should fire up a

* Local MySQL service with the above username and password
* Initialise the database with appropriate table definitions to accept data from the pipeline
* The named entity recogniser as a containerised service

#### Effect of Running the Task

* Copy the raw document data to the MySQL database (this is intended to make the fields available in the same database)
* Run the named entity recogniser pipeline to insert the named entities (together with SoT matched entities) into the
  database in a separate table

A user can verify the results by logging into the database (exposed at port 3306 of the host) and checking the table.

#### Database Schema

In the database, two tables are created

* `documents`: Contains the raw documents data, without any change. (Recommended to convert the UUID to Binary and
  certain data cleanups)
* `extracted_entities`: Results of the NER pipeline with one row for each entity from each document.

Instead of merging them into the same table, the schema is partially normalised to avoid storing the long document
bodies multiple times for each entity.
