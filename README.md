# mm-rag-chat
Quick POC of mm-RAG chat-based search application for the Flickr30k dataset (https://huggingface.co/datasets/nlphuji/flickr30k?library=datasets). 

https://612a80d447442136e6.gradio.live/ (lasts for 72 hours will update if requested, generated by Gradio)
Used GCP VM, GCS Bucket, GCP SQL DB, GCP Logging, Pinecone Vector DB, CLIP Model, Gemini Model (Vertex AI), Gradio UI

Overview
This project implements a multimodal chat application that allows users to query both text and images from the Flickr30 dataset using a Retrieval-Augmented Generation (RAG) approach. The application integrates text and image data, using vector-based retrieval and large language models to generate meaningful responses to user queries.

Features

Multimodal RAG Integration: Retrieves both text and images from the Flickr30 dataset.
Vector Database Integration: Uses Pinecone for efficient vector-based retrieval.
LLM Integration: Leverages the Gemini model for query analysis and response generation.
User-friendly Interface: Implements a Gradio interface for easy interaction.
Metadata Storage: Stores and retrieves image metadata using MySQL.
Conversation Logging: Logs user interactions using Google Cloud Logging.

Installation

1. Clone the repository:
git clone https://github.com/austinjohn3424/mm-rag-chat.git
cd mm-rag-chat
3. Create and activate a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate
4. Install the required dependencies:
pip install -r requirements.txt

Configuration

1. Set up Google Cloud Platform:

Create a new project or use an existing one.
Enable necessary APIs (Vertex AI, Cloud Logging).
Set up service account credentials and download the JSON key file.
Set the GOOGLE_APPLICATION_CREDENTIALS environment variable:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

2. Set up Pinecone:

Create a Pinecone account and set up a new index.
Update the API_KEY and INDEX_NAME in config.py.


3. Set up MySQL Database:

Create a MySQL database and import the Flickr30 metadata.
Update the MYSQL_CONFIG in config.py with your database credentials.

Workflow was as follows
1. Download/Parse Flickr30k dataset to understand data structure (provided in .arrow) in GCP VM
2. Upload images to GCS Bucket for retrieval
3. Upload dataset metadata and image path to GCP MySQL DB
4. Generate vector embeddings using CLIP and upsert to Pinecone Vector DB
5. Gradio UI to receive user input test text queries
6. Process text query with Gemini, use CLIP to convert to vectors to look up in Pinecone DB
7. Display returned images and image metadata
8. Generate Gemini response based on queried images and user's text input
9. Log user input, image/vector query and LLM responses in GCP Logging 

Usage

To use the application ensure all credentials are filled in src/config.py and then run src/main.py

Utils folder is to parse dataset and get it into GCS/Pinecone, these files also need to be filled in with credentials. Everything is currently based on GCP and Pinecone so it will have to be adapted to your env. 

![image](https://github.com/user-attachments/assets/3d92feff-87b4-4090-ba86-7407687d2c81)
![image](https://github.com/user-attachments/assets/e05882f6-96cb-44d8-b50d-840fba3921c6)

Note performance isn't that great and the models need more tuning or I need to look into other ones. 

Example of GCP Logging:
![image](https://github.com/user-attachments/assets/12b2f3ad-8a2f-4b1c-a07b-e8b026d7ff86)

