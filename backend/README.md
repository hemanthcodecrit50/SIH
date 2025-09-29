# SIH Project Overview

This project provides an end-to-end pipeline for generating personalized agricultural advisories for farmers using AI and external data sources.

## File Summaries

### advisory_pipeline.py
Main orchestration script. Runs the workflow: classifies intent, retrieves static and external info, personalizes advisory, generates response using LLM, delivers via SMS/WhatsApp/app/TTS/PDF, logs actions, and updates learning.

### models/intent_classifier/__init__.py
Implements intent classification using IndicBERT (HuggingFace Transformers). Includes code for training on custom data and mapping queries to domain-specific intents.

### models/intent_classifier/data/train.jsonl
Sample training data mapping farmer queries to intent labels for training the intent classifier.

### models/advisory_llm/__init__.py
Implements the advisory generation engine using IndicGPT. Includes code for training on KCC (Kisan Call Center) Q&A data and generating advisories from aggregated context.

### models/advisory_llm/data/kcc_train.jsonl
Sample KCC dataset with question-answer pairs for fine-tuning IndicGPT.

### retrieval/rag.py
Retrieves relevant static information using FAISS vector search over documents in `data/static_db`. Embeds queries and finds the most relevant document.

### retrieval/mcp_api.py
REST API clients for market, weather, pest, and scheme data. Uses environment variables for API keys and endpoints. Returns structured info for each intent.

### retrieval/redis_store.py
Handles personalization using Redis. Fetches and updates per-farmer profiles and generates personalized advisory context.

### delivery/sms.py
Sends advisories to farmers via SMS using Twilio. Includes stub for phone number lookup.

### delivery/whatsapp.py
Stub for sending advisories via WhatsApp. (Implementation can be extended with WhatsApp API.)

### delivery/app.py
Stub for sending app push notifications to farmers.

### delivery/tts_pdf.py
Generates TTS audio using gTTS and PDF reports using ReportLab for advisories.

### logging/action_log.py
Logs farmer actions and updates their timeline. (Implementation can be extended for persistent storage.)

### learning/continuous_learning.py
Updates farmer profiles and learns from logs/yields for improved personalization.

### data/static_db/
Contains static documents (manuals, PoPs, FAQs) used for RAG retrieval.

### data/farmer_profiles/
Stores per-farmer logs and yield history.

### requirements.txt
Lists all required Python packages for the project.

### .env
Environment variables for API keys, Redis, Twilio, etc.

### content/test.png
Placeholder image file.

---

## Usage

1. Prepare training data for intent classification and advisory generation.
2. Set up environment variables in `.env`.
3. Install dependencies from `requirements.txt`.
4. Run `advisory_pipeline.py` to generate and deliver advisories.

## Running the Flask Backend

To start the API server, run this command in your terminal from the SIH directory:

```
python api.py
```

- This will start the server at `http://127.0.0.1:8000`
- Use `/advisory`, `/speech`, and `/audio` endpoints as before.

---
   Run the following command in your terminal:
   ```
   uvicorn api:app --reload
   ```
   - This will start the FastAPI server at `http://127.0.0.1:8000`.

4. **Access the API**  
   - Use the `/advisory` endpoint for text queries.
   - Use the `/speech` endpoint for speech queries.
   - Use the `/audio` endpoint to get the generated advisory audio.

5. **(Optional) Frontend**  
   Open `index.html` in your browser to interact with the API.

## Troubleshooting: FastAPI/uvicorn "unreachable" issue

If you see `INFO: Uvicorn running on http://127.0.0.1:8000` but cannot access it in your browser:

1. **Check the endpoint:**  
   - The root URL `/` does not serve a page by default.
   - Try accessing the docs at:  
     ```
     http://127.0.0.1:8000/docs
     ```
   - Or test the `/advisory` endpoint using a tool like [Postman](https://www.postman.com/) or `curl`.

2. **Firewall/Antivirus:**  
   - Ensure your firewall or antivirus is not blocking Python or port 8000.

3. **Port conflict:**  
   - Make sure no other service is using port 8000.

4. **Network:**  
   - If running in a VM or container, check network settings.

5. **Code errors:**  
   - Check the terminal for any error messages after startup.

6. **Static files:**  
   - If you want to serve your frontend (`index.html`), you need to use a static files mount in FastAPI or open the HTML file directly in your browser.

---

**To test the API quickly:**
- Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

