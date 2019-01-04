hasurino
^^^^^^^^

Forward HFP MQTT messages into transitlog GraphQL API.

Usage
*****

An example usage:

.. code:: sh

   cp config.yaml my_config.yaml

   # Modify the configuration to match your needs. The suggested values in
   # config.yaml are quite sensible for HFP messages.
   vim my_config.yaml

   docker run \
     -v ./my_config.yaml:/my_config.yaml \
     hsldevcom/hasurino:latest \
     /my_config.yaml

A configuration file is necessary.
There are no other ways to configure hasurino.
As the configuration file contains secrets, the recommendation for Docker usage is to make the whole configuration a Docker secret.

Structure
*********

hasurino consists of a pipeline of three parts: MQTT subscribing, message processing and posting to the GraphQL endpoint.
Each part is handled by a separate thread.
The threads communicate using one-way queues.
There is also a queue for exceptions that will end the program.

Message processing is divided into message deduplication (for MQTT QoS 1), parsing, bundling and serializing.
