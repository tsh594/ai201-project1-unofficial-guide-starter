# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Domain Summary: This system covers unofficial student reviews and logistical realities of off-campus housing options surrounding George Mason University in Fairfax, VA. This information is highly valuable because official university housing portals only list commercial properties and basic addresses without revealing true student experiences. Unofficial insights—such as hidden delivery hassles, specific complex safety issues, structural layout downsides, and local roommate pricing trends—are usually scattered across disorganized social media threads, making them difficult for incoming students to comprehensively search and analyze.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit r/gmu | The Flats at University - individual leasing terms and appliance kinks. | doc1.txt |
| 2 | Reddit r/gmu | King's Park West Townhouses - proximity and walking times for students. | doc2.txt |
| 3 | Reddit r/gmu | Budget Townhouse Living - cost comparisons ($550/mo) vs living alone. | doc3.txt |
| 4 | Reddit r/gmu | The Main vs The Flats - noise complaints and management warnings for The Main. | doc4.txt |
| 5 | Reddit r/gmu | Rent Market Trends - tracking Fairfax price hikes ($850-$1200) via Facebook groups. | doc5.txt |
| 6 | Reddit r/gmu | Trillium Apartments - structural safety and management response nightmares. | doc6.txt |
| 7 | Reddit r/gmu | Camden Fairfax Corner - package delivery mapping confusion and walking hassles. | doc7.txt |
| 8 | Reddit r/gmu | Fairfax Square Apartments - ground floor pest/sunlight issues vs upper floor space. | doc8.txt |
| 9 | Reddit r/gmu | Townhouse vs Campus Dorm Costs - 12-month lease value comparison. | doc9.txt |
| 10 | Reddit r/gmu | The Flats Leasing Terms - roommate pairing questionnaires and academic-year leases. | doc10.txt |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Reasoning:** Our source documents consist of short, dense, opinion-based student reviews and advice blocks (roughly 300 to 800 characters per document). Setting a chunk size of 500 characters ensures that an entire student review or key paragraph stays completely intact inside a single chunk. The 50-character overlap acts as a safety safety net—if a critical piece of advice (like a price point or a warning) spans across a text boundary, the overlap guarantees that context isn't severed, keeping chunks readable and semantically whole on their own.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 4

**Production tradeoff reflection:** If deploying for real users without cost constraints, I would evaluate enterprise models like OpenAI's `text-embedding-3-large` or Cohere's embeddings. Tradeoffs to weigh include: 1) **Context Length:** Enterprise models handle massive text inputs compared to MiniLM's 256-token limit. 2) **Accuracy:** Higher-dimensional models yield richer semantic matches on niche local terms. 3) **Latency & Cost:** Local models provide instantaneous retrieval with zero API cost, whereas external APIs introduce network latency and per-token pricing that scales with user traffic.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What are the pros and cons of living at The Flats at University? | Pros include individual room leasing (charging by bedroom, not unit), roommate pairing based on profiles, and academic-year leases. Cons include high prices and dealing with unhelpful management or new appliance kinks. |
| 2 | Why do students complain about Trillium Apartments? | Students describe it as an absolute nightmare and an ordeal due to building safety features frequently breaking down and terrible management response times. |
| 3 | What is the average cost of renting a room in a townhouse near GMU? | Rent ranges from ultra-lucky finds at $550 a month up to more recent standard market trends of $850 to $1200 a month for a single room. |
| 4 | What delivery issues should someone expect at Camden Fairfax Corner? | The complex layout is confusing and GPS maps cannot accurately find specific apartment doors. Packages/food are rarely delivered to the door, forcing a half-mile walk to the main community building entrance. |
| 5 | Is the ground floor a good option at Fairfax Square Apartments? | No, ground floor units have issues with bugs/pests and a distinct lack of natural sunlight due to the structural landscaping outside the windows. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Noisy Text Boundaries:** Because these documents contain rough social media text copy-pasted straight from internet forums, some data might contain URL links or symbols that could fragment cleanly into chunks.
2. **Strict Grounding Enforcement:** The Groq LLM might try to use its generalized training data to give generic housing advice (e.g., "Always read your lease carefully before moving in") instead of strictly relying on our 10 documents. The prompt must be heavily locked down to stop this.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```text
[Raw Documents (.txt)] ➔ [Document Ingestion & Cleaning]
                                  ⬇
                         [Chunking Strategy]
                                  ⬇
                  [Embeddings (all-MiniLM-L6-v2)]
                                  ⬇
                        [ChromaDB Vector Store] ➔ [Semantic Search Query]
                                                          ⬇
                                              [LLM Generation (Groq Llama-3.3)]
                                                          ⬇
                                                [Gradio Web UI Output]

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will use Claude/ChatGPT. I'll provide it with the full "Documents" table and "Chunking Strategy" section from this file. I expect it to generate a Python script that cleanly reads all .txt files from the documents/ folder, wipes out unnecessary whitespace, and slices them into 500-character pieces with a 50-character overlap. I will verify it by having the script print out 5 random chunks to visually check that they are readable text blocks rather than broken words.

**Milestone 4 — Embedding and retrieval:**
I will use Claude/ChatGPT. I'll pass my "Retrieval Approach" parameters and the "Architecture" diagram. I expect it to produce code that initializes all-MiniLM-L6-v2, processes the chunks from Milestone 3, stores them inside a local ChromaDB database collection along with filename metadata, and provides a search function. I will verify this by feeding it 3 of my test questions from the "Evaluation Plan" and checking that the printed database search results are highly relevant to the query.

**Milestone 5 — Generation and interface:**
I will use Claude/ChatGPT. I'll supply the "Evaluation Plan" queries, the Groq LLM model constraint (llama-3.3-70b-versatile), and the request for a Gradio UI. I expect it to write an application script that routes the user's input question to the vector search, feeds those results into a strictly bounded system prompt to enforce context grounding, and creates a clean web interface displaying the answer and the text sources used. I will verify it by launching the app in my browser and testing it live with an off-topic question to make sure it handles out-of-scope gracefully.
