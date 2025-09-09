# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path
from embeddings_store import EmbeddingStore
from models import sentiment_pipe, predict_priority, predict_intent
from db_init import init_db
import json
import hashlib
import os

BASE = Path(__file__).parent
DB = BASE / "tickets.db"
init_db()
es = EmbeddingStore(path=str(BASE / "kb_store"))

app = Flask(__name__)
CORS(app)

def save_ticket(channel, text, priority, intent, sentiment, compliance):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
      INSERT INTO tickets (channel, raw_text, priority, intent, sentiment, compliance_flag)
      VALUES (?, ?, ?, ?, ?, ?)
    ''', (channel, text, priority, intent, sentiment, int(compliance)))
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def log_ai_action(ticket_id, step, detail):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO ai_logs (ticket_id, step, detail) VALUES (?,?,?)', (ticket_id, step, detail))
    conn.commit()
    conn.close()

@app.route("/ingest", methods=["POST"])
def ingest():
    payload = request.json or {}
    text = payload.get("text","")
    channel = payload.get("channel","web")
    sentiment = "NEUTRAL"
    try:
        sentiment = sentiment_pipe(text)[0]["label"]
    except Exception:
        sentiment = "UNKNOWN"
    intent, intent_score = predict_intent(text)
    priority = predict_priority(text)
    banned = ["suicide", "terror", "explosive"]
    compliance = any(b in text.lower() for b in banned)
    ticket_id = save_ticket(channel, text, priority, intent, sentiment, compliance)
    log_ai_action(ticket_id, "ingest", json.dumps({"priority":priority,"intent":intent,"sentiment":sentiment,"compliance":compliance}))
    return jsonify({"ticket_id": ticket_id, "priority": priority, "intent": intent, "sentiment": sentiment, "compliance": compliance})

@app.route("/kb/add", methods=["POST"])
def kb_add():
    payload = request.json or {}
    texts = payload.get("texts",[])
    metas = payload.get("metas",[{}]*len(texts))
    es.add(texts, metas)
    return jsonify({"status":"ok","added":len(texts)})

@app.route("/rag", methods=["POST"])
def rag():
    data = request.json or {}
    ticket_id = data.get("ticket_id")
    question = data.get("question","")
    results = es.search(question, k=4)
    passages = [r[1].get("text") if isinstance(r[1], dict) and r[1].get("text") else str(r[1]) for r in results]
    safe_answer = "Relevant KB passages found:\n\n"
    for i,p in enumerate(passages,1):
        safe_answer += f"{i}. {p}\n\n"
    safe_answer += f"Automated suggestion: follow the steps above. If unresolved, escalate to human (ticket {ticket_id})."
    log_ai_action(ticket_id or -1, "rag", json.dumps({"question":question,"retrieved_count":len(passages)}))
    return jsonify({"passages": passages, "answer": safe_answer})

@app.route("/tickets", methods=["GET"])
def list_tickets():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, channel, priority, intent, sentiment, compliance_flag, created_at FROM tickets ORDER BY created_at DESC LIMIT 500')
    rows = c.fetchall()
    cols = ["id","channel","priority","intent","sentiment","compliance_flag","created_at"]
    res = [dict(zip(cols, r)) for r in rows]
    conn.close()
    return jsonify(res)

@app.route("/ai_logs", methods=["GET"])
def get_logs():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, ticket_id, step, detail, created_at FROM ai_logs ORDER BY created_at DESC LIMIT 500')
    rows = c.fetchall()
    cols = ["id","ticket_id","step","detail","created_at"]
    res = [dict(zip(cols, r)) for r in rows]
    conn.close()
    return jsonify(res)

@app.route("/export_logs", methods=["POST"])
def export_logs():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT id, ticket_id, step, detail, created_at FROM ai_logs ORDER BY created_at ASC')
    rows = c.fetchall()
    cols = ["id","ticket_id","step","detail","created_at"]
    logs = [dict(zip(cols,r)) for r in rows]
    bytestext = json.dumps(logs, indent=2).encode("utf-8")
    h = hashlib.sha256(bytestext).hexdigest()
    out_path = BASE / f"ai_logs_snapshot_{h}.json"
    with open(out_path, "wb") as f:
        f.write(bytestext)
    conn.close()
    return jsonify({"snapshot_file": str(out_path), "sha256": h})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
