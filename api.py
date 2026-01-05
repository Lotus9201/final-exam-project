import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. 在初始化時加入標題與描述
app = FastAPI(
    title="名言佳句 API",
    description="這是一個名言佳句管理系統的 API，可以用來新增、修改、刪除和查詢名言資料。"
)

class PostCreate(BaseModel):
    text: str
    author: str
    tags: str

class PostResponse(PostCreate):
    id: int

def get_db_conn():
    conn = sqlite3.connect('quotes.db')
    conn.row_factory = sqlite3.Row
    return conn

# 2. 新增根路徑端點 (Read Root)，讓介面多出第一條 GET /
@app.get("/", include_in_schema=True)
def read_root():
    return {"message": "Welcome to Quote API"}

@app.get("/quotes", response_model=list[PostResponse])
def get_quotes():
    with get_db_conn() as conn:
        rows = conn.execute("SELECT * FROM quotes").fetchall()
        return [dict(row) for row in rows]

@app.post("/quotes", response_model=PostResponse)
def create_quote(quote: PostCreate):
    with get_db_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)",
            (quote.text, quote.author, quote.tags)
        )
        new_id = cursor.lastrowid
        conn.commit()
        return {**quote.model_dump(), "id": new_id}

@app.put("/quotes/{quote_id}", response_model=PostResponse)
def update_quote(quote_id: int, quote: PostCreate):
    with get_db_conn() as conn:
        cursor = conn.execute(
            "UPDATE quotes SET text=?, author=?, tags=? WHERE id=?",
            (quote.text, quote.author, quote.tags, quote_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Quote not found")
        conn.commit()
        return {**quote.model_dump(), "id": quote_id}

@app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int):
    with get_db_conn() as conn:
        cursor = conn.execute("DELETE FROM quotes WHERE id=?", (quote_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Quote not found")
        conn.commit()
        return {"message": "Quote deleted successfully"}