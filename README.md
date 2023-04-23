# Basic Producer Consumer using Kafka and MySQL Produced by GPT-4
This is my attempt to use GPT-4 to generate a basic producer-consumer app that is using docker-compose.

```
+-------------+      +-------------+      +------------+      +-------------+
|             |      |             |      |            |      |             |
|  MySQL DB   +----->+  Producer   +----->+   Kafka    +----->+  Consumer   |
|             |      |  (Python)   |      |   Broker   |      |  (Python)   |
+------+------+      +------+------+      +------+-----+      +------^------+
       |                    |                    |                   |
       |                    |                    |                   |
+------+------+      +------+------+      +------+-----+      +------v------+
|             |      |             |      |            |      |             |
|  Database   |      | Dockerized  |      | Dockerized |      | Dockerized  |
|  (Docker)   |      |  Producer   |      |   Kafka    |      |  Consumer   |
|             |      |  (Docker)   |      |  (Docker)  |      |  (Docker)   |
+-------------+      +-------------+      +------------+      +-------------+
```
In this architecture, the following components are involved:

MySQL Database: The MySQL database stores the my_table with the rows to be processed. The database runs inside a Docker container.

Producer (Python): The producer Python script reads unprocessed rows from the MySQL database, and sends them as messages to the Kafka topic my_tasks_topic. The producer runs inside a Docker container.

Kafka Broker: The Kafka broker receives messages from the producer and stores them in the my_tasks_topic topic. The broker runs inside a Docker container.

Consumer (Python): The consumer Python script subscribes to the Kafka topic my_tasks_topic and processes messages sent by the producer. The consumer runs inside a Docker container.