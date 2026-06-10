import os
import chromadb
import gradio as gr
from groq import Groq
from sentence_transformers import SentenceTransformer

# ----------------------------------------------------------------------
# Load secret API key from the local environment configuration (.env)
# ----------------------------------------------------------------------
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip().replace('"', '').replace("'", "")

# ----------------------------------------------------------------------
# Connect to database, load the embedding model, init the Groq client
# ----------------------------------------------------------------------
db_client = chromadb.PersistentClient(path="./chroma_db")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
collection = db_client.get_collection(name="gmu_housing_reviews")

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

LLM_MODEL = "llama-3.3-70b-versatile"

# Dropdown choices: "All Documents" plus doc1.txt ... doc10.txt
DOC_CHOICES = ["All Documents"] + [f"doc{i}.txt" for i in range(1, 11)]


# ----------------------------------------------------------------------
# STEP 1 — Isolated Search Query Extraction
# When there is chat history, ask the LLM to rewrite the (possibly vague)
# follow-up into a standalone keyword query that vector search will love.
# When history is empty, just use the raw question.
# ----------------------------------------------------------------------
def build_search_query(message, llm_history):
    # No history -> fall back to the raw user question directly
    if not llm_history:
        return message

    # Use only the last 2 turns (up to 4 messages) for context
    recent_turns = llm_history[-4:]
    history_text = ""
    for turn in recent_turns:
        speaker = "User" if turn["role"] == "user" else "Assistant"
        history_text += f"{speaker}: {turn['content']}\n"

    rewrite_prompt = (
        "Look at this user question and the past turns of chat history. "
        "Generate a single, concise string of search keywords optimal for "
        "vector database retrieval (e.g., if the user asks a follow-up like "
        "'How long is the walk from there?', output \"King's Park West walk to "
        "campus time\"). Output ONLY the standalone search query string, nothing else.\n\n"
        f"--- CHAT HISTORY ---\n{history_text}\n"
        f"--- CURRENT USER QUESTION ---\n{message}\n\n"
        "Standalone search query:"
    )

    try:
        completion = groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": rewrite_prompt}],
            temperature=0.0,
            max_tokens=60,
        )
        search_query = completion.choices[0].message.content.strip().strip('"').strip()
        # Safety net: if the rewrite came back empty, use the raw message
        return search_query if search_query else message
    except Exception:
        # If the rewrite call fails for any reason, never block the user
        return message


# ----------------------------------------------------------------------
# Main chat handler
# ----------------------------------------------------------------------
def ask_unofficial_guide(message, display_history, llm_history, selected_doc):
    if not message or not message.strip():
        return display_history, llm_history, ""

    # STEP 1: get the best possible vector-search query
    search_query = build_search_query(message, llm_history)

    # STEP 2: Metadata filtering — restrict to one document if chosen
    query_args = {
        "query_embeddings": embedding_model.encode([search_query]).tolist(),
        "n_results": 4,
    }
    if selected_doc and selected_doc != "All Documents":
        query_args["where"] = {"source": selected_doc}

    search_results = collection.query(**query_args)
    retrieved_chunks = search_results["documents"][0]
    retrieved_metadata = search_results["metadatas"][0]

    # Format the retrieved context blocks and collect citations
    context_text = ""
    source_set = set()
    for idx, chunk in enumerate(retrieved_chunks):
        source_name = retrieved_metadata[idx]["source"]
        context_text += f"\n[Document Context — {source_name}]\n{chunk}\n"
        source_set.add(source_name)

    # STEP 3: Gentle but grounded system prompt
    system_prompt = (
        "You are 'The Unofficial Guide', an AI assistant for GMU off-campus housing.\n\n"
        "Answer the user's current question using the provided Document Context pieces. "
        "You may use the conversation history to understand pronouns or references "
        "(like 'there' or 'it'), but do not invent facts outside the text documents. "
        "If the text context doesn't contain the answer at all, say: "
        "'I do not have enough information to answer this based on the unofficial guide documents.'\n\n"
        f"--- START DOCUMENT CONTEXT ---\n{context_text}\n--- END DOCUMENT CONTEXT ---"
    )

    # Build the message list: system + recent history + current question
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(llm_history)
    messages.append({"role": "user", "content": message})

    # STEP 4: Generate the grounded answer
    try:
        completion = groq_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.2,
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        answer = f"System Error connecting to Groq API: {str(e)}"
        display_history = display_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ]
        return display_history, llm_history, ""

    # Programmatically format the sources footer
    if "do not have enough information" in answer.lower() or not source_set:
        sources_text = "No source material utilized."
    else:
        sources_text = ", ".join(sorted(source_set))

    bubble = f"{answer}\n\n---\n📚 **Sources:** {sources_text}"

    # Update the visible chat window
    display_history = display_history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": bubble},
    ]

    # Update hidden memory with the CLEAN answer (no footer) for follow-ups
    llm_history = llm_history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": answer},
    ]

    return display_history, llm_history, ""


def reset_chat():
    """Clear the visible chat and the hidden conversation memory."""
    return [], [], ""


# ----------------------------------------------------------------------
# Gradio UI
# ----------------------------------------------------------------------
with gr.Blocks(title="GMU Unofficial Housing Guide") as demo:
    gr.Markdown("# 📬 The Unofficial GMU Off-Campus Housing Guide")
    gr.Markdown(
        "### Chat about real student experiences with apartments, townhouses, prices, "
        "and landlords around Fairfax. Ask follow-up questions naturally!"
    )

    # Hidden conversation memory (clean version sent to the LLM)
    llm_state = gr.State([])

    with gr.Row():
        doc_dropdown = gr.Dropdown(
            choices=DOC_CHOICES,
            value="All Documents",
            label="🔎 Filter search to a specific document source",
        )

    chatbot = gr.Chatbot(
        label="Conversation",
        height=450,
    )

    with gr.Row():
        input_box = gr.Textbox(
            label="Ask your question (plain English):",
            placeholder="e.g., Tell me about townhouses in King's Park West... then: How long is the walk to campus?",
            lines=2,
            scale=4,
        )
        submit_btn = gr.Button("Send", variant="primary", scale=1)

    clear_btn = gr.Button("🗑️ Clear Conversation")

    # Wire up the actions
    submit_btn.click(
        fn=ask_unofficial_guide,
        inputs=[input_box, chatbot, llm_state, doc_dropdown],
        outputs=[chatbot, llm_state, input_box],
    )
    input_box.submit(
        fn=ask_unofficial_guide,
        inputs=[input_box, chatbot, llm_state, doc_dropdown],
        outputs=[chatbot, llm_state, input_box],
    )
    clear_btn.click(
        fn=reset_chat,
        inputs=None,
        outputs=[chatbot, llm_state, input_box],
    )

if __name__ == "__main__":
    demo.launch()
