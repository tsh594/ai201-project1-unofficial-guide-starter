import os
import chromadb
from sentence_transformers import SentenceTransformer

def run_pipeline():
    print("--- Starting RAG Ingestion Pipeline ---")

    # 1. Initialize local persistent database and embedding model
    db_path = "./chroma_db"
    client = chromadb.PersistentClient(path=db_path)

    # Using our specified local model
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Create or reset our specific housing collection
    collection_name = "gmu_housing_reviews"
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass
    collection = client.create_collection(name=collection_name)

    # 2. Document Ingestion & Cleaning
    docs_folder = "./documents"
    if not os.path.exists(docs_folder):
        print(f"ERROR: Cannot find folder '{docs_folder}'. Make sure it exists!")
        return

    all_chunks = []
    all_metadatas = []
    all_ids = []
    chunk_counter = 0

    # Loop over doc1.txt through doc10.txt
    for filename in sorted(os.listdir(docs_folder)):
        if filename.endswith(".txt"):
            file_path = os.path.join(docs_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Simple cleaning: normalize spaces and drop extra empty lines
            cleaned_text = " ".join(raw_text.split())

            # 3. Chunking Strategy (Size: 500 characters, Overlap: 50 characters)
            chunk_size = 500
            overlap = 50

            start = 0
            while start < len(cleaned_text):
                end = start + chunk_size
                chunk = cleaned_text[start:end]

                # Check that chunk isn't empty space
                if chunk.strip():
                    all_chunks.append(chunk)
                    all_metadatas.append({"source": filename})
                    all_ids.append(f"id_{chunk_counter}")
                    chunk_counter += 1

                start += (chunk_size - overlap)

    print(f"Processed documents. Total text chunks generated: {len(all_chunks)}")

    # Print sample chunks for milestone validation requirement
    print("\n--- Milestone 3 Checkpoint: Inspecting 5 Sample Chunks ---")
    for i in range(min(5, len(all_chunks))):
        print(f"\n[Sample Chunk #{i+1}] | Source: {all_metadatas[i]['source']}")
        print(f"Text: \"{all_chunks[i][:120]}...\"")
    print("------------------------------------------------------\n")

    # 4. Generate Embeddings & Load Into ChromaDB Vector Store
    print("Generating vector mathematical embeddings and loading into database...")
    embeddings = model.encode(all_chunks).tolist()

    collection.add(
        embeddings=embeddings,
        documents=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids
    )
    print("Successfully built vector database and saved inside './chroma_db' folder!")

    # 5. Milestone 4 Checkpoint: Test Semantic Retrieval Function
    print("\n--- Milestone 4 Checkpoint: Testing Search Retrieval ---")
    test_query = "What delivery issues happen at Camden Fairfax Corner?"
    print(f"Querying database for: '{test_query}'")

    query_embedding = model.encode([test_query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2  # Look for top matching context
    )

    print("\nTop Retrievable Matches Found:")
    for idx in range(len(results['documents'][0])):
        doc = results['documents'][0][idx]
        src = results['metadatas'][0][idx]['source']
        print(f"-> Match from [{src}]: \"{doc[:150]}...\"")
    print("------------------------------------------------------")

if __name__ == "__main__":
    run_pipeline()
