from datasets import load_dataset
import mysql.connector
from mysql.connector import Error

# Database connection details
DB_HOST = 'YOUR_SQL_DB_HOST' 
DB_USER = 'YOUR_SQL_DB_USER'
DB_PASSWORD = 'YOUR_SQL_DB_PASS'
DB_NAME = 'YOUR_SQL_DB_NAME'

def connect_to_database():
    """Establish a connection to the MySQL database and create the table if it doesn't exist."""
    try:
        # Connect to the MySQL server
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if connection.is_connected():
            cursor = connection.cursor()

            # Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
            cursor.execute(f"USE {DB_NAME};")

            # Create the table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS flickr_metadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                image_path VARCHAR(255),
                caption TEXT,
                sentids TEXT,
                split VARCHAR(50),
                img_id VARCHAR(50),
                filename VARCHAR(255)
            );
            """)

            print("Connected to the database and ensured the table exists.")
            return connection, cursor
    except Error as err:
        print(f"Error: {err}")
        return None, None

def insert_data_if_not_exists(cursor, image_path, caption, sentids, split, img_id, filename):
    """Insert data into the flickr_metadata table if it does not already exist."""
    # Check if the img_id already exists
    cursor.execute("SELECT COUNT(*) FROM flickr_metadata WHERE img_id = %s", (img_id,))
    result = cursor.fetchone()
    if result[0] == 0:
        # If no record exists, insert the new data
        cursor.execute("""
            INSERT INTO flickr_metadata (image_path, caption, sentids, split, img_id, filename)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (image_path, caption, sentids, split, img_id, filename))
    else:
        print(f"Record with img_id {img_id} already exists. Skipping insertion.")

def load_and_process_dataset(cursor):
    """Load and process the Flickr30k dataset using the datasets library."""
    # Load the Flickr30k dataset
    dataset = load_dataset('nlphuji/flickr30k')

    # Process the 'test' split
    data = dataset['test']
        
    # Iterate through each example in the dataset split
    for example in data:
        image_path = example['image'].filename  # Get the filename of the image
        caption_list = example.get('caption', [])
        sentids_list = example.get('sentids', [])
        split = example.get('split', '')
        img_id = example.get('img_id', '')
        filename = example.get('filename', '')

        # Convert lists to strings
        caption = "; ".join(caption_list)  # Join captions with a semicolon
        sentids = ",".join(sentids_list)  # Join sentids with a comma
        
        # Insert the data into the MySQL table
        insert_data_if_not_exists(cursor, image_path, caption, sentids, split, img_id, filename)
    print("Test data processed and inserted successfully.")

def main():
    """Main function to execute the script."""
    # Connect to the database
    connection, cursor = connect_to_database()
    if connection and cursor:
        # Load and process the dataset
        load_and_process_dataset(cursor)

        # Commit changes to the database
        connection.commit()
        print("All data inserted successfully.")

        # Close the connection
        cursor.close()
        connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
