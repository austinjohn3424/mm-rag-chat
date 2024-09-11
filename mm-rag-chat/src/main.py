# main.py
import gradio as gr
from config import setup_logging, logging
from database import fetch_metadata
from vector_db import initialize_pinecone, query_pinecone
from ml_models import initialize_clip, generate_clip_embedding, analyze_query_with_gemini, generate_response_with_gemini

def process_and_query(text):
    try:
        query_analysis = analyze_query_with_gemini(text)
        logging.info(f"Generated query instructions: {query_analysis}")

        if "find images with" in query_analysis:
            keywords = query_analysis.split("find images with")[-1].strip()
            enhanced_query = f"Find images with {keywords}"
        else:
            enhanced_query = text

        query_embedding_clip = generate_clip_embedding(clip_model, clip_processor, enhanced_query)

        pinecone_results = query_pinecone(pinecone_index, query_embedding_clip)
        logging.info(f"Retrieved {len(pinecone_results)} results from Pinecone")

        similarity_threshold = 0.75
        filtered_results = [result for result in pinecone_results if result['score'] >= similarity_threshold]
        logging.info(f"Filtered results to {len(filtered_results)} based on similarity threshold of {similarity_threshold}")

        img_ids = [match['id'].split('_')[1] for match in filtered_results]

        metadata_results = fetch_metadata(img_ids)
        logging.info(f"Retrieved {len(metadata_results)} metadata results from MySQL")

        for result in metadata_results:
            if "image_path" in result:
                result["image_path"] = result["image_path"].replace("flikr30k-images", "flikr30k")

        response_text = generate_response_with_gemini(text, metadata_results)

        return {"response": response_text, "images": [result['image_path'] for result in metadata_results], "metadata_results": metadata_results}

    except Exception as e:
        logging.error(f"Unexpected error in process_and_query: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

def gradio_query(text):
    try:
        results = process_and_query(text)
        log_interaction(text, results)

        if "error" in results:
            return results["error"], [], []

        response_text = results.get("response", "No response generated")
        image_paths = results.get("images", [])
        metadata_results = results.get("metadata_results", [])

        return response_text, image_paths, metadata_results
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logging.error(error_message)
        return error_message, [], []

def log_interaction(query, result):
    logging.info(f"User Query: {query}")
    logging.info(f"Result: {result}")

def main():
    iface = gr.Interface(
        fn=gradio_query,
        inputs=[
            gr.Textbox(label="Enter Text Query")
        ],
        outputs=[
            gr.Textbox(label="Generated Response"),
            gr.Gallery(label="Retrieved Images"),
            gr.JSON(label="Metadata Results")
        ],
        title="Multimodal Chat Application",
        description="Query images and text from the Flickr30k dataset"
    )
    iface.launch(share=True)

if __name__ == "__main__":
    setup_logging()
    pinecone_index = initialize_pinecone()
    clip_model, clip_processor = initialize_clip()
    main()
