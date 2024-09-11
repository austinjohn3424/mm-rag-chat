# ml_models.py
import torch
from transformers import CLIPProcessor, CLIPModel
import numpy as np
from vertexai.generative_models import GenerativeModel
from config import PROJECT_ID, REGION, SAFETY_SETTINGS, logging

def initialize_clip():
    try:
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        logging.info("CLIP model and processor loaded successfully.")
        return model, processor
    except Exception as e:
        logging.error(f"Failed to load CLIP model and processor: {str(e)}")
        raise

def normalize_embedding(embedding):
    embedding = np.array(embedding)
    embedding = np.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0)
    norm = np.linalg.norm(embedding)
    if norm > 1e-10:
        normalized_embedding = embedding / norm
    else:
        logging.warning("Embedding norm is very close to zero, returning zero vector")
        normalized_embedding = np.zeros_like(embedding)
    normalized_embedding = np.clip(normalized_embedding, -1.0, 1.0)
    return normalized_embedding.tolist()

def generate_clip_embedding(model, processor, text):
    inputs = processor(text=[text], return_tensors="pt")
    with torch.no_grad():
        query_embedding = model.get_text_features(**inputs).cpu().numpy().flatten()
    return normalize_embedding(query_embedding)

def analyze_query_with_gemini(query):
    prompt = (
        f"Given the query '{query}', provide precise instructions to find only the most relevant images "
        f"that directly match the description. Exclude any images that do not match the core concept of the query."
    )
    
    generation_config = {
        "max_output_tokens": 1024,
        "temperature": 0.3,
        "top_p": 0.9,
    }

    model = GenerativeModel("gemini-1.5-flash-001")
    
    try:
        responses = model.generate_content(
            [prompt],
            generation_config=generation_config,
            safety_settings=SAFETY_SETTINGS
        )
        
        generated_instructions = responses.text.strip()
        logging.info(f"Successfully generated query analysis and instructions using Gemini: {generated_instructions}")
        return generated_instructions
    except Exception as e:
        logging.error(f"Error analyzing query with Gemini: {str(e)}")
        return f"Error analyzing query: {str(e)}"

def generate_response_with_gemini(query, retrieved_data):
    prompt = f"Given the following query: '{query}' and image data: {retrieved_data}, generate a response describing the images and their relevance to the query. Focus on how well the images match the query, describing the most relevant images first."
    
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.3,
        "top_p": 0.95,
    }

    model = GenerativeModel("gemini-1.5-flash-001")

    try:
        responses = model.generate_content(
            [prompt],
            generation_config=generation_config,
            safety_settings=SAFETY_SETTINGS
        )

        generated_text = responses.text.strip()
        logging.info(f"Successfully generated response from Gemini: {generated_text}")
        return generated_text
    except Exception as e:
        logging.error(f"Error generating response with Gemini: {str(e)}")
        return f"Error generating response: {str(e)}"
