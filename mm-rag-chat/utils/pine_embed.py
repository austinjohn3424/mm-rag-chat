import os
from datasets import load_dataset
from pinecone import Pinecone, ServerlessSpec
from transformers import CLIPProcessor, CLIPModel
import torch
import numpy as np
from tqdm import tqdm

# Initialize Pinecone client
api_key = os.environ.get("PINECONE_API_KEY", "YOUR_API_KEY")  # Replace with your Pinecone API key
pc = Pinecone(api_key=api_key)

index_name = "flickr30k-embeddings"

# Check if the index exists; create it if it doesn't
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=512,  # CLIP embedding dimension
        metric='cosine',
        spec=ServerlessSpec(
            cloud='gcp',    # Adjust based on your requirements
            region='us-central1'
        )
    )
print(f"Using Pinecone index: {index_name}")

# Connect to the index
index = pc.Index(index_name)

# Initialize CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
print("CLIP model and processor loaded.")

def normalize_embedding(embedding):
    """Normalize the embedding to unit length."""
    embedding = np.array(embedding)
    embedding = np.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0)
    norm = np.linalg.norm(embedding)
    if norm > 1e-10:
        return (embedding / norm).tolist()
    return np.zeros_like(embedding).tolist()

def generate_embeddings_and_store(dataset, start_batch=0):
    """Generate vector embeddings for images and text, and store them in Pinecone."""
    batch_size = 32  # Adjust based on your GPU memory

    # Process batches
    for i in tqdm(range(start_batch, len(dataset['test']), batch_size)):
        # Select a batch from the dataset
        batch = dataset['test'].select(range(i, min(i + batch_size, len(dataset['test']))))

        # Extract images and captions from the dataset
        images = [example['image'] for example in batch if example['image'] is not None]  # Ensure images are not None
        all_captions = [str(example['caption']) for example in batch if example['caption'] is not None]  # Ensure captions are strings

        # Ensure both inputs are not empty
        if not images or not all_captions:
            print(f"Skipping batch {i} due to missing data.")
            continue

        # Generate embeddings for images and captions
        inputs = processor(text=all_captions, images=images, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            outputs = model(**inputs)
            image_embeddings = outputs.image_embeds.cpu().numpy()
            text_embeddings = outputs.text_embeds.cpu().numpy()

        # Prepare vectors for upsert
        vectors = []
        for j, img_emb, caption in zip(range(len(images)), image_embeddings, all_captions):
            # Use img_id directly from the dataset for consistency
            img_id = batch['img_id'][j]
            vectors.append((str(img_id), img_emb.tolist(), {"type": "image", "img_id": img_id}))

            text_id = f"txt_{img_id}"
            vectors.append((text_id, text_embeddings[j].tolist(), {"type": "text", "caption": caption, "img_id": img_id}))

        # Upsert vectors to Pinecone
        index.upsert(vectors=vectors)
        print(f"Processed and stored {len(vectors)} vectors.")

def main():
    """Main function to execute the script."""
    # Load the Flickr30k dataset
    dataset = load_dataset("nlphuji/flickr30k")  # Corrected dataset path

    # Determine the batch to start from
    last_processed_batch = 0  # Set this to 0 to start from the beginning, or adjust if resuming

    # Generate and store embeddings starting from the last processed batch
    generate_embeddings_and_store(dataset, start_batch=last_processed_batch * 32)  # Multiply by batch size to get the starting point

if __name__ == "__main__":
    main()
