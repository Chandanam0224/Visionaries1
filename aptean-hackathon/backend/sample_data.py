# sample_data.py
from embeddings_store import EmbeddingStore
from db_init import init_db
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
init_db()
es = EmbeddingStore(path=str(BASE / "kb_store"))

kb_texts = [
 "How to reset your password: account-settings -> security -> reset password. If user cannot reset, file support ticket with id and device info.",
 "Refund policy: refunds processed within 5-7 business days after approval. Required fields: order_id, proof of purchase.",
 "Troubleshoot login: ensure user email verified, clear cache, try reset link, check caps-lock.",
 "Shipping delays: check carrier status, expected delays page, and send compensation policy if eligible."
]
metas = [{"id": i, "text": t} for i,t in enumerate(kb_texts)]
es.add(kb_texts, metadatas=metas)

# insert example ticket
conn = sqlite3.connect(BASE / "tickets.db")
c = conn.cursor()
c.execute("INSERT INTO tickets (channel, raw_text, priority, intent, sentiment, compliance_flag) VALUES (?, ?, ?, ?, ?, ?)",
          ("email", "I need a refund for order #12345. I never received it.", "P2", "billing", "NEGATIVE", 0))
conn.commit()
conn.close()
print("Sample KB and ticket created.")
