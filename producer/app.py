import mysql.connector
from kafka import KafkaProducer, KafkaAdminClient
from kafka.errors import KafkaError
import random
import time

# Connect to MySQL
def connect_to_mysql(user, password, host, database):
    return mysql.connector.connect(user=user, password=password, host=host, database=database)

# Check if the table exists and create it if not
def ensure_table_exists(cnx):
    print("Creating my_table...")
    cursor = cnx.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS my_table ("
                   "id INT AUTO_INCREMENT PRIMARY KEY,"
                   "data TEXT NOT NULL,"
                   "status ENUM('unprocessed', 'processed', 'completed') NOT NULL DEFAULT 'unprocessed',"
                   "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                   "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                   ");")
    cnx.commit()
    cursor.close()

# Generate and insert sample rows
def insert_sample_rows(cnx, num_rows):
    print("Inserting sample rows to the my_table...")
    cursor = cnx.cursor()
    for _ in range(num_rows):
        random_data = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=100))
        insert_query = "INSERT INTO my_table (data) VALUES (%s);"
        cursor.execute(insert_query, (random_data,))
    cnx.commit()
    cursor.close()

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

# Fetch unprocessed rows and enqueue them in Kafka
def produce_and_enqueue_data(cnx, producer):

    print("Fetching data to enqueue...")
    cursor = cnx.cursor()
    query = "SELECT * FROM my_table WHERE status='unprocessed' LIMIT 100;"
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        print("Enqueuing to the Kafka ...")
        task = str(row).encode('utf-8')
        producer.send('my_tasks_topic', task)

        update_query = "UPDATE my_table SET status='processed' WHERE id=%s;"
        cursor.execute(update_query, (row[0],))
        cnx.commit()

        wait_time = random.uniform(0.3, 3)
        time.sleep(wait_time)

    cursor.close()

if __name__ == "__main__":

    producer = None
    bootstrap_servers=['kafka:9092']
    # Wait for Kafka broker to be ready before proceeding
    if check_kafka_connection(bootstrap_servers):
        print("Kafka broker is available, connecting...")
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        pass
    else:
        raise Exception("Sorry, Kafka is not available...")

    print("Connecting to the MySQL database server...")
    cnx = connect_to_mysql(user='myuser', password='myuserpassword', host='mysql', database='mydb')

    ensure_table_exists(cnx)
    insert_sample_rows(cnx, 10000)

    while True:
        produce_and_enqueue_data(cnx, producer)
        time.sleep(0.1)  # 100ms

    print("Producer terminating...")
    cnx.close()