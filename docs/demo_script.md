# Smart Research Assistant - 5 Minute Capstone Demo Script

**Preparation Before Demo:**
1. Ensure Ollama is running (`ollama run qwen2.5:1.5b` in a separate terminal).
2. Start backend: `uvicorn backend.main:app --reload`
3. Start frontend: `npm run dev`
4. Open `http://localhost:5173`

---

## 1. Search & Select (1 Min)
**Action:** In the Chat box, type: "Find recent papers on Federated Learning in Healthcare."
**Talking Points:** 
> "Our application acts as an agentic gateway to OpenAlex. Instead of just listing papers, it pulls abstracts, embeds them using BAAI/bge-small-en-v1.5, and ranks them against our search query using Cosine Similarity. You can see the Similarity Score directly on the cards."

**Action:** Click the [+] icon on 3 highly relevant papers. 
**Talking Points:** 
> "As I select these, they are placed into our 'Working Context', ready for our LLM agents."

## 2. Generate Summaries (1 Min)
**Action:** Click the "Generate Summary" button on the first selected paper. Wait for the task bar to complete.
**Talking Points:** 
> "Our Summary Agent extracts the Objective, Methodology, Findings, and Limitations. This isn't just a generic prompt—it's highly structured and uses vector retrieval from the paper's contents. The result is cached in SQLite so we never pay the token cost to generate it again."

## 3. Compare Papers (1 Min)
**Action:** Click the "Compare (3)" button in the Working Context header.
**Talking Points:** 
> "Now, our Comparison Agent kicks in. Instead of reading raw PDFs, it reads the structured summaries we just cached. It produces a rigid Markdown table comparing their methodologies and findings, and generates insights into overall Research Trends."

## 4. Chat with Papers [RAG Mode] (1 Min)
**Action:** Type in the chat: "Based on the selected papers, what are the primary limitations mentioned by the authors?"
**Talking Points:** 
> "Because we have papers selected, the Chat Agent operates in Document-Grounded RAG Mode. It queries ChromaDB to find specific chunks related to 'limitations' from these 3 papers and strictly grounds its answer in that text to prevent hallucinations."

## 5. Generate Final Report & Export (1 Min)
**Action:** Navigate to the "Reports" tab. Click "+ New". Type Topic: "Federated Learning in Healthcare" and enter the IDs of the 3 papers. Click Generate.
**Talking Points:** 
> "This is the culmination of the workflow. The Report Service asynchronously gathers our cached summaries, the cached comparison table, and passes them to the LLM to synthesize a comprehensive IEEE-style report."
> 
> "Notice the References at the bottom. Our LLM is expressly forbidden from hallucinating citations. Instead, our Citation Service calculates accurate IEEE citations from the database metadata and forcefully injects them."

**Action:** Click "Download PDF", open the downloaded file. Click "Download DOCX", open the file.
**Talking Points:** 
> "Finally, we can instantly export this Markdown into fully structured PDF and Word documents, ready for submission."
