import os
import chromadb
import gradio as gr
from groq import Groq
from sentence_transformers import SentenceTransformer

# Load secret API key from the local environment configurations (.env file)
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip().replace('"', '').replace("'", "")

# Connect to database and load embedding layer locally
db_client = chromadb.PersistentClient(path="./chroma_db")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
collection = db_client.get_collection(name="gmu_housing_reviews")

# Initialize our free production cloud inference engine
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_unofficial_guide(question):
    if not question.strip():
        return "Please input a valid question.", "No sources used."

    # 1. Retrieval Phase (Top-k = 4 chunks)
    query_vector = embedding_model.encode([question]).tolist()
    search_results = collection.query(
        query_embeddings=query_vector,
        n_results=4
    )

    retrieved_chunks = search_results['documents'][0]
    retrieved_metadata = search_results['metadatas'][0]

    # Consolidate text context and log citations
    context_text = ""
    source_set = set()
    for idx, chunk in enumerate(retrieved_chunks):
        source_name = retrieved_metadata[idx]['source']
        context_text += f"\nDocument Context [{source_name}]: {chunk}\n"
        source_set.add(source_name)

    # 2. Bounded System Prompt Generation Phase
    system_prompt = (
        "You are 'The Unofficial Guide' AI assistant specialized in GMU off-campus housing.\n"
        "Your task is to answer the user's question using ONLY the provided document context below.\n"
        "CRITICAL RULES:\n"
        "1. Ground your answer explicitly and exclusively in the provided text pieces.\n"
        "2. Do NOT extrapolate or assume anything not written.\n"
        "3. If the provided context does not contain the answer, you must state exactly: "
        "'I do not have enough information to answer this based on the unofficial guide documents.'\n\n"
        f"--- START EXTRACTED LOGICAL CONTEXT ---\n{context_text}\n--- END CONTEXT ---"
    )

    # 3. LLM Cloud Execution
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.2  # Lower temperature guarantees high grounding compliance
        )
        answer = completion.choices[0].message.content

        # Check if model declared a refusal to answer due to missing text matching context
        if "do not have enough information" in answer.lower():
            sources_display = "No source material utilized."
        else:
            sources_display = "\n".join([f"• {src}" for src in sorted(source_set)])

        return answer, sources_display

    except Exception as e:
        return f"System Error connecting to Groq Brain API: {str(e)}", "N/A"

# 4. Gradio Production GUI Layout Builder
with gr.Blocks(title="GMU Unofficial Housing Guide") as demo:
    gr.Markdown("# 📬 The Unofficial GMU Off-Campus Housing Guide")
    gr.Markdown("### Search semantic student experiences regarding apartments, complexes, townhouse rentals, prices, and landlords around Fairfax.")

    with gr.Row():
        with gr.Column(scale=2):
            input_box = gr.Textbox(
                label="Ask your student question (Plain English):",
                placeholder="e.g., What are the issues with the ground floor at Fairfax Square?",
                lines=2
            )
            submit_btn = gr.Button("Search & Generate Grounded Answer", variant="primary")

        with gr.Column(scale=3):
            output_answer = gr.Textbox(label="Grounded AI Response Text (Strictly bounded):", lines=8, interactive=False)
            output_sources = gr.Textbox(label="Retrieved Source Citations (Filing Cabinet References):", lines=3, interactive=False)

    # Trigger parameters wireframe actions
    submit_btn.click(fn=ask_unofficial_guide, inputs=input_box, outputs=[output_answer, output_sources])
    input_box.submit(fn=ask_unofficial_guide, inputs=input_box, outputs=[output_answer, output_sources])

if __name__ == "__main__":
    demo.launch()
