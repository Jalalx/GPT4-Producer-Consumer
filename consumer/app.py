import mysql.connector
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.errors import KafkaError
import random
import time
import datetime

# Connect to MySQL
def connect_to_mysql(user, password, host, database):
    return mysql.connector.connect(user=user, password=password, host=host, database=database)

# Check Kafka connection
def check_kafka_connection(bootstrap_servers, max_retries=10, retry_interval=5):
    retries = 0
    while retries < max_retries:
        try:
            # Check the connection using the KafkaAdminClient
            admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
            admin_client.close()
            print("Kafka broker is ready.")
            return True
        except KafkaError as e:
            print(f"Kafka connection failed (attempt {retries + 1}/{max_retries}): {e}")
            retries += 1
            time.sleep(retry_interval)
    
    print("Max retries reached. Exiting.")
    return False


def process_row(row):
    print("Processing row id #" + str(row[0]))
    wait_time = random.uniform(0.3, 3)
    time.sleep(wait_time)

    
# Fetch unprocessed rows and enqueue them in Kafka
def consume_data(cnx, consumer):

    print("Fetching data to consume...")
    cursor = cnx.cursor()
    
    for message in consumer:
        row = eval(message.value)
        process_row(row)

        # Update the row as 'completed'
        update_query = "UPDATE my_table SET status='completed' WHERE id=%s;"
        cursor.execute(update_query, (row[0],))
        cnx.commit()

    cursor.close()

if __name__ == "__main__":

    consumer = None
    bootstrap_servers=['kafka:9092']
    # Wait for Kafka broker to be ready before proceeding
    if check_kafka_connection(bootstrap_servers):
        print("Kafka broker is available, connecting...")
        consumer = KafkaConsumer(
            'my_tasks_topic',
            group_id='my_group',
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: m.decode('utf-8'),
            enable_auto_commit=True)
        pass
    else:
        raise Exception("Sorry, Kafka is not available...")

    print("Connecting to the MySQL database server...")
    cnx = connect_to_mysql(user='myuser', password='myuserpassword', host='mysql', database='mydb')

    while True:
        consume_data(cnx, consumer)
        time.sleep(0.1)  # 100ms

    print("Consumer terminating...")
    cnx.close()