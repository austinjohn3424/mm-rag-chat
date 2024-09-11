from datasets import load_dataset
from google.cloud import storage
from tqdm import tqdm
import io

# Function to upload a file to GCS
def upload_to_gcs(bucket, image, destination_blob_name):
    blob = bucket.blob(destination_blob_name)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    blob.upload_from_string(img_byte_arr, content_type='image/jpeg')

# Set up GCS client
storage_client = storage.Client()
bucket = storage_client.bucket('flikr30k')

# Load the Flickr30k dataset
print("Loading Flickr30k dataset...")
ds = load_dataset("nlphuji/flickr30k", split="test")  # or "train" if you want the full dataset

# Process each image
for item in tqdm(ds, desc="Uploading images"):
    image = item['image']
    filename = item['filename']  # Use the filename directly from the dataset

    # Upload to GCS
    upload_to_gcs(bucket, image, filename)

print("Upload completed!")
