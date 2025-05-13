## Goal

The project reads the raw document data (containing title, unique document id and several other attributes)
to recognise the named entities and inserts the recognised entities into a MySQL database.
The named entity recognition task is isolated from the main pipeline by a containerised service interface.

##### Infrastructure Requirements

Make sure you got a POSIX environment (tested on Debian Bookworm) with recent versions of the following components

* [Docker daemon and CLI](https://docs.docker.com/get-started/overview/) for containerisation
* [Minikube](https://minikube.sigs.k8s.io/docs/start/) as a local Kubernetes cluster manager
* [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to control the cluster resources

Further, make sure your minikube cluster can pull the public images `barmanroys/ent-extraction` and `barmanroys/ner-service` from Dockerhub.


#### Effects of Running the Task

* Copy the raw document data to the MySQL database (this is intended to make the fields available in the same database). If the raw documents (identified by UUID) already exist, this phase is skipped.
* Run the named entity recogniser pipeline to insert the named entities (together with SoT matched entities) into the
  database in a separate table

A user can verify the results by logging in to the database (exposed at port 3306 of the database pod, which can be tunnelled to the localhost) and checking the table.
You can use tools like DBeaver to access the database or go to the MySQL console by

```shell
mysql -h 127.0.0.1 -p
```

and keying in the password (set by the environment variable) when prompted. The sample output data can be found in the `extraction_pipeline/sample_out_dump` directory.

#### Database Schema

The schema can be seen from the database initialisation script. Basically, two tables are created

* `documents`: Contains the raw documents data after converting the UUID to binary format.
* `extracted_entities`: Results of the NER pipeline with one row for each entity from each document.

Instead of merging them into the same table, the schema is partially normalised to avoid storing the long document
bodies multiple times for each entity. But I also created a unified view (combining document details and named entities) that you can query by

```sql
SELECT * FROM db.extracted_entities_documents;
```

#### Kubernetes Set up
The `kubeops-manifests` directory contains the Kubernetes manifests for deploying the application. You can deploy the application by running the following command:

```shell
time ./end-to-end-test.sh
```
Running this has the following effects
* Build the images
* Push the images to the dockerhub registry (needs access to dockerhub)
* Deploy the services (Database and the NER) on the local minikube cluster
* Schedule the ETL pipeline as a Kubernetes cron job
* Start a minikube dashboard to monitor the service health
