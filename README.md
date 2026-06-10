# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

The system covers unofficial student reviews, hidden logistical details, and real pricing landscapes of off-campus housing options immediately surrounding George Mason University (Fairfax campus). This knowledge is highly valuable because official university housing websites only feature sanitized commercial property listings, basic geographic coordinates, or sponsored property advertisements. They omit the actual daily living experiences of students. Unofficial insights—such as recurring delivery mapping issues, broken complex security features, apartment layout design flaws, and historical neighborhood townhouse pricing shifts—are normally scattered organically across hundreds of disorganized social media threads, making it incredibly difficult for incoming students to search or synthesize them effectively.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit r/gmu community thread | Text Document | documents/doc1.txt |
| 2 | Reddit r/gmu community thread | Text Document | documents/doc2.txt |
| 3 | Reddit r/gmu community thread | Text Document | documents/doc3.txt |
| 4 | Reddit r/gmu community thread | Text Document | documents/doc4.txt |
| 5 | Reddit r/gmu community thread | Text Document | documents/doc5.txt |
| 6 | Reddit r/gmu community thread | Text Document | documents/doc6.txt |
| 7 | Reddit r/gmu community thread | Text Document | documents/doc7.txt |
| 8 | Reddit r/gmu community thread | Text Document | documents/doc8.txt |
| 9 | Reddit r/gmu community thread | Text Document | documents/doc9.txt |
| 10| Reddit r/gmu community thread | Text Document | documents/doc10.txt|

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Our source documents consist of authentic student opinions and forum posts that are relatively brief and dense, generally falling between 300 and 800 characters total. Using a fixed chunk size of 500 characters allows a student's complete core argument or housing critique to fit entirely inside a single data segment. The 50-character overlap provides a safety margin; if a specific financial metric, landlord warning, or complex address happens to fall right on the edge of a character division, the overlapping window ensures the text context is preserved in both text slices instead of being cut off midsentence. Preprocessing before chunking was done by using Python's string splitting to condense erratic extra white spaces and strip away double empty lines from forum copy-pasting.

**Final chunk count:** 14 chunks

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` running locally.

**Production tradeoff reflection:** If deploying this system for thousands of real users where operational budget constraints are completely removed, I would evaluate migrating to a modern API-hosted model such as OpenAI's `text-embedding-3-large` or Cohere's `embed-english-v3.0`. The primary tradeoffs to balance would be:
1. *Context Length Limits:* The local MiniLM model is hard-capped at a tiny 256 input tokens, whereas modern cloud embedding layers handle up to 8,192 tokens. This allows much larger, complex text structures to be embedded simultaneously.
2. *Accuracy on Domain-Specific Text:* High-dimensional commercial embeddings capture deep, nuanced contextual relationships (like mapping the slang term "kinks" to operational faults), whereas a smaller local model has a less expressive semantic space.
3. *Latency and Hosting:* Local execution via MiniLM provides instantaneous, free vector searches with zero network dependency or usage cost. Moving to a cloud API introduces potential network latency and variable per-token transaction fees that would increase as user traffic scales.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** Grounding is enforced through a strict system prompt embedded directly inside the execution code of `app.py`. The exact system instructions fed to the model state:
"You are 'The Unofficial Guide' AI assistant specialized in GMU off-campus housing. Your task is to answer the user's question using ONLY the provided document context below. CRITICAL RULES: 1. Ground your answer explicitly and exclusively in the provided text pieces. 2. Do NOT extrapolate or assume anything not written. 3. If the provided context does not contain the answer, you must state exactly: 'I do not have enough information to answer this based on the unofficial guide documents.'"

**How source attribution is surfaced in the response:**
Source attribution is guaranteed programmatically through the Python script architecture rather than leaving it to the creative choice of the LLM. When ChromaDB completes its semantic retrieval, the application extracts the metadata dictionary containing the source filename (e.g., `doc7.txt`) for each of the top 4 matched text chunks. These filenames are added to a clean, isolated Python set to remove duplicates, formatted with bullet points, and displayed directly inside an independent, read-only text field box named "Retrieved Source Citations" in the Gradio user interface.
---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the pros and cons of living at The Flats at University? | Pros include individual room leasing, roommate profile matching, and academic-year leases. Cons include high prices and appliance kinks. | The Flats offers individual room leasing and roommate pairing via questionnaires. It allows flexible academic leases. However, it is pricey and has technical appliance kinks. | Relevant | Accurate |
| 2 | Why do students complain about Trillium Apartments? | Students complain about broken building safety features and terrible management response times. | Living there is described as a nightmare because building safety features frequently break and management response times are terrible. | Relevant | Accurate |
| 3 | What is the average cost of renting a room in a townhouse near GMU? | Rent ranges from ultra-lucky finds at $550 a month up to modern market trends of $850 to $1200 a month. | Townhouse room rent can be as low as $550 per month in a shared setup, but current market trends show prices pushing up to a range of $850 to $1200 a month. | Relevant | Accurate |
| 4 | What delivery issues should someone expect at Camden Fairfax Corner? | The complex layout is confusing for GPS maps, forcing a half-mile walk to the main community entrance to meet drivers. | The complex layout is confusing, and addresses cannot be found by GPS. Residents must walk half a mile to the main entrance to meet couriers. | Relevant | Accurate |
| 5 | Is the ground floor a good option at Fairfax Square Apartments? | No, ground floor units have issues with bugs/pests and a distinct lack of natural sunlight due to landscaping. | No, ground floor units are not recommended because they experience issues with pests and suffer from a lack of natural sunlight due to landscaping. | Relevant | Accurate |

**Retrieval quality:** Relevant  
**Response accuracy:** Accurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** What is the best major at George Mason University?

**What the system returned:** I do not have enough information to answer this based on the unofficial guide documents.

**Root cause (tied to a specific pipeline stage):** This test represents a deliberate out-of-scope defensive query designed to stress-test the system's generation guardrails. During the Retrieval stage, the vector database searched for semantic fragments matching "academic majors" across our 10 housing files. Because all vector distance match scores were poor, the chunks returned to the prompt context were entirely unrelated to the question. Once passed to the Generation stage, the strict instructions within the system prompt successfully blocked the LLM from using its pre-trained training data, causing it to intentionally trigger our required safety refusal string rather than inventing a hallucinated response.

**What you would change to fix it:** If the goal was to actually expand the scope of the app to answer academic questions, I would expand the Document Ingestion pipeline by collecting 10 additional source text files containing raw student forum discussions regarding GMU degree selections, class difficulty profiles, and department rankings, and ingest them directly into the ChromaDB collection.
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** The initial design layout in `planning.md` was incredibly helpful because it forced me to establish the exact chunk sizes, text overlap counts, and target evaluation answers prior to writing code. This served as a complete technical architectural specification that I could feed directly into the AI tool. This structure prevented the AI from writing generic, bloated boilerplate and ensured it generated code perfectly fitted to our short-form files.

**One way your implementation diverged from the spec, and why:** The implementation diverged from the planning document during the integration of the environment security variables. In the blueprint, I intended to pass raw configurations directly, but during construction, I introduced `python-dotenv` and a structured safety verification block to read `GROQ_API_KEY` from an isolated, git-ignored `.env` file. This change was necessary to follow professional security standards and prevent private application keys from being accidentally leaked into public GitHub code repositories.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I provided the AI with my complete "Chunking Strategy" parameters (500 character limits, 50 character overlaps), the "Documents" database summary table, and the text architecture diagram from my `planning.md` file.
- *What it produced:* It generated a clean, standalone Python script named `pipeline.py` utilizing the `chromadb` library and `sentence-transformers` to automate document reading, white-space cleaning, character slicing, and local database population.
- *What I changed or overrode:* I overrode the document reading loop to include an explicit Python `sorted()` function. The AI originally wrote an arbitrary file reader, but adding sorting ensured that `doc1.txt` through `doc10.txt` are processed in perfect alphabetical order, making terminal logging and chunk indexing much cleaner to audit.

**Instance 2**

- *What I gave the AI:* I supplied the AI with my strict system prompt grounding instructions, the required LLM model parameter (`llama-3.3-70b-versatile`), and the request to wrap the system inside a web browser layout using `Gradio`.
- *What it produced:* It produced a unified frontend application script (`app.py`) that successfully connected user text boxes to the database search queries and handled cloud completion messages.
- *What I changed or overrode:* I completely overrode the visual layout structu