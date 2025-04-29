## Goal

One run of the pipeline performs the named entity recognition together with Database insertion.

#### Code Walkthrough

Following Bob Martin's Clean Architecture, the pipeline is designed to be modular and adheres to the SOLID principles. Each component has an abstract interface, which is implemented by concrete classes. Interfacing with other components must be done through the abstract interface, while the concrete objects are built with the `Factory` classes. The major components are

- **Data Loader**: This is responsible for loading data. In real production system, it can load data from a database or Kafka stream, in the present context, it is mocked by a concrete class that loads data from a file.
- **Named Entity Recogniser**: Abstract interface offered by an NER model, which is implemented by a class that makes use of a remote API. The implementation can also get the entities locally using a pre-trained model.
- **Entity Matcher**: This component is responsible for comparing the extracted entities with SoT entities. The mock version loads them from a static file, but in production setting, this warrants a database of its own.
- **Persistence Module**: Responsible for persisting the extracted and matched entities. The implementation uses a MySQL relational database, but, again, depending on the specific requirement, it can be designed to interface with a data lake/warehouse or cloud storage media, while maintaining the abstract interface.
- **Document Processor**: Asynchronously processes each document after data loading till persistence. The lazy nature of the implementation allows for better I/O performance.
- **Main**: Integrate the above components to create a pipeline that processes documents.
