import mysql.connector
import logging
#Script to update IMAGE_PATHS in SQL DB based on GCS bucket
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to the MySQL database
def connect_to_mysql():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='',  # Replace with your host
            user='',  # Replace with your username
            password='',  # Replace with your password
            database=''  # Replace with your database name
        )
        if connection.is_connected():
            logging.info("Successfully connected to MySQL database.")
            return connection
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to MySQL database: {err}")
    return None

# Function to update image paths in the database in batches
def update_image_paths_in_batches(batch_size=100):  # Adjust batch_size as needed
    """Update the image paths in the flickr_metadata table in batches."""
    conn = connect_to_mysql()
    if conn:
        try:
            cursor = conn.cursor()

            # Fetch all filenames from the flickr_metadata table
            cursor.execute("SELECT filename FROM flickr_metadata")
            filenames = cursor.fetchall()

            total_rows = len(filenames)
            processed_rows = 0

            # Process filenames in batches
            for i in range(0, total_rows, batch_size):
                batch_filenames = filenames[i:i + batch_size]

                for filename in batch_filenames:
                    file_name_str = filename[0]  # Extract the filename from tuple
                    image_path = f"YOUR_BUCKET_NAME/{file_name_str}"  # Updated bucket name

                    # Prepare the SQL update statement
                    update_query = "UPDATE flickr_metadata SET image_path = %s WHERE filename = %s"
                    cursor.execute(update_query, (image_path, file_name_str))

                    processed_rows += 1
                    if processed_rows % 100 == 0:  # Log progress every 100 rows
                        logging.info(f"Processed {processed_rows} out of {total_rows} rows.")

                # Commit changes for the current batch
                conn.commit()

            logging.info("Image paths updated successfully.")
        except mysql.connector.Error as err:
            logging.error(f"Error updating image paths: {err}")
        finally:
            cursor.close()
            conn.close()

# Run the update function with batch processing
if __name__ == "__main__":
    update_image_paths_in_batches()  # You can adjust the batch_size here if needed
