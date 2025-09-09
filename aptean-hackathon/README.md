Aptean Hackathon - AI Case Resolution Agent (local, no Docker)

1) Backend setup
   cd backend
   python -m venv .venv
   source .venv/bin/activate     # Windows: .\.venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   python db_init.py
   python sample_data.py
   python app.py

   Backend runs at http://localhost:8000

2) Frontend setup
   cd frontend
   npm install
   npm run dev

   Frontend runs at http://localhost:5173

3) Demo endpoints
   POST /ingest   {"channel":"email","text":"my order never arrived"}
   POST /kb/add   {"texts":["..."], "metas":[{"text":"..."}]}
   POST /rag      {"ticket_id":1, "question":"how to refund order"}
   GET  /tickets
   GET  /ai_logs
   POST /export_logs

Notes:
 - If faiss installation fails, the embedding store falls back to sklearn-based nearest neighbor.
 - Use small inputs in hackathon. Keep an eye on transformers memory use.
 - Models will download weights on first run (internet required).
