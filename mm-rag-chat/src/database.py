# database.py
import mysql.connector
from config import MYSQL_CONFIG, logging

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            logging.info("Successfully connected to MySQL database.")
            return connection
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to MySQL database: {err}")
    return None

def fetch_metadata(img_ids):
    conn = connect_to_mysql()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            placeholders = ', '.join(['%s'] * len(img_ids))
            query = f"SELECT * FROM flickr_metadata WHERE img_id IN ({placeholders})"
            cursor.execute(query, tuple(img_ids))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            ordered_results = {img_id: None for img_id in img_ids}
            for result in results:
                ordered_results[str(result['img_id'])] = result
            
            return [result for result in ordered_results.values() if result is not None]
        except mysql.connector.Error as err:
            logging.error(f"Error fetching metadata: {err}")
    return []
