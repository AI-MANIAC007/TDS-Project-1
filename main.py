# main.py
import os
import json
import uvicorn
import subprocess
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from datetime import datetime
import requests
from pathlib import Path
import sqlite3

app = FastAPI()

# ========= UTILITIES ========= #

def enforce_sandbox(task):
    if ".." in task or not task.startswith("/") and "/data" not in task:
        raise ValueError("Access outside /data is not allowed.")
    if "delete" in task.lower() or "rm " in task.lower():
        raise ValueError("Deletion operations are not permitted.")

def read_file(path):
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError
    return file_path.read_text()

def call_llm(task):
    url = "https://api.proxy.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['AIPROXY_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that extracts structured task commands."},
            {"role": "user", "content": task}
        ]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    return response.json()["choices"][0]["message"]["content"]

# ========= TASK EXECUTORS ========= #

def count_weekdays(file_path, weekday_name, out_path):
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    target_day = weekdays.get(weekday_name.lower())
    if target_day is None:
        raise ValueError("Invalid weekday")

    with open(file_path, "r") as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        try:
            date_obj = datetime.strptime(line.strip(), "%Y-%m-%d")
            if date_obj.weekday() == target_day:
                count += 1
        except:
            continue

    with open(out_path, "w") as f:
        f.write(str(count))

def sort_contacts(input_path, output_path):
    with open(input_path, "r") as f:
        contacts = json.load(f)

    sorted_contacts = sorted(
        contacts,
        key=lambda x: (x.get("last_name", ""), x.get("first_name", ""))
    )

    with open(output_path, "w") as f:
        json.dump(sorted_contacts, f, indent=2)

def recent_log_lines(log_dir, output_file):
    log_files = sorted(
        Path(log_dir).glob("*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:10]

    lines = []
    for f in log_files:
        with open(f, "r") as lf:
            first_line = lf.readline().strip()
            lines.append(first_line)

    with open(output_file, "w") as out:
        out.write("\n".join(lines))

def extract_total_sales(db_path, output_file):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type='Gold'")
    result = cursor.fetchone()[0] or 0
    with open(output_file, "w") as f:
        f.write(str(result))
    conn.close()

# ========= API ROUTES ========= #

@app.post("/run")
async def run_task(request: Request):
    task = request.query_params.get("task")
    if not task:
        raise HTTPException(status_code=400, detail="No task specified")

    try:
        enforce_sandbox(task)

        llm_response = call_llm(task).lower()

        # Simplified examples of how we map LLM text to actions
        if "wednesday" in llm_response and ".txt" in llm_response:
            count_weekdays("/data/dates.txt", "wednesday", "/data/dates-wednesdays.txt")
        elif "contacts" in llm_response and "sort" in llm_response:
            sort_contacts("/data/contacts.json", "/data/contacts-sorted.json")
        elif "log" in llm_response and "recent" in llm_response:
            recent_log_lines("/data/logs", "/data/logs-recent.txt")
        elif "gold" in llm_response and "ticket" in llm_response:
            extract_total_sales("/data/ticket-sales.db", "/data/ticket-sales-gold.txt")
        else:
            raise ValueError("LLM returned unknown command")

        return {"status": "success"}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read(path: str):
    try:
        content = read_file(path)
        return PlainTextResponse(content, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

# ========= ENTRYPOINT ========= #

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
