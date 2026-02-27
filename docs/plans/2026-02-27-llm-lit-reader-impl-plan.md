# LLM Literature Reader Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a web-based LLM-assisted literature reading tool with PDF upload, embedded viewer, annotations, and LLM chat with ripgrep search.

**Architecture:** FastHTML server-rendered app with DaisyUI. Three-column layout: collapsible file sidebar, PDF iframe viewer, LLM chat panel. PDF parsed to Markdown on upload for LLM context retrieval via ripgrep.

**Tech Stack:** FastHTML, DaisyUI, markitdown, openai (DeepSeek), ripgrep

---

## Phase 1: Project Setup

### Task 1: Initialize Python project structure

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `.env.example`

**Step 1: Write requirements.txt**

```txt
fasthtml
markitdown
openai
python-dotenv
httpx
```

**Step 2: Write config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

UPLOAD_DIR = "uploads"
```

**Step 3: Write .env.example**

```bash
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

**Step 4: Commit**

```bash
git add requirements.txt config.py .env.example
git commit -m "feat: add project dependencies and config"
```

---

### Task 2: Create uploads directory and verify project runs

**Files:**
- Modify: `app.py` - minimal FastHTML app
- Modify: `config.py` - ensure upload dir exists

**Step 1: Write minimal app.py**

```python
from fasthtml.common import *
from config import UPLOAD_DIR

app = FastHTML(hdrs=(picolink(), tailwindcss()))

rt = app.route

@rt("/")
def get():
    return Titled("LLM Literature Reader",
        H1("LLM Literature Reader"),
        P("Welcome to your literature reading companion!")
    )

serve()
```

**Step 2: Update config.py to create upload directory**

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
```

**Step 3: Run and verify**

```bash
pip install -r requirements.txt
python app.py
```

Expected: Server starts on http://localhost:5001

**Step 4: Commit**

```bash
git add app.py config.py
git commit -m "feat: add minimal FastHTML app with upload directory"
```

---

## Phase 2: Three-Column Layout

### Task 3: Build three-column layout with DaisyUI

**Files:**
- Modify: `app.py` - add layout

**Step 1: Write app.py with three-column layout**

```python
from fasthtml.common import *
from config import UPLOAD_DIR

app = FastHTML(hdrs=(
    picolink(),
    Script(src="https://cdn.tailwindcss.com"),
    Script(src="https://cdn.jsdelivr.net/npm/daisyui@4"),
))

rt = app.route

def file_sidebar():
    return Div(
        cls="flex flex-col h-full bg-base-200 w-64 min-h-screen p-4",
        id="sidebar",
    )(
        H2("Files", cls="text-xl font-bold mb-4"),
        Button("Upload PDF", cls="btn btn-primary btn-sm mb-4"),
        Div(id="file-list", cls="flex-1 overflow-y-auto")(
            P("No files uploaded", cls="text-sm text-gray-500")
        )
    )

def pdf_viewer():
    return Div(
        cls="flex-1 bg-base-100 p-4",
        id="pdf-viewer",
    )(
        Iframe(src="", cls="w-full h-full border-none", id="pdf-frame")
    )

def chat_panel():
    return Div(
        cls="w-96 bg-base-200 p-4 flex flex-col",
        id="chat-panel",
    )(
        H2("LLM Chat", cls="text-xl font-bold mb-4"),
        Div(id="chat-messages", cls="flex-1 overflow-y-auto mb-4")(
            P("Start a conversation about your paper...", cls="text-sm")
        ),
        Form(hx_post="/chat", hx_target="#chat-messages")(
            Input(name="message", cls="input input-bordered w-full", placeholder="Ask about the paper..."),
            Button("Send", cls="btn btn-primary mt-2")
        )
    )

@rt("/")
def get():
    return Titled("LLM Literature Reader",
        Div(cls="flex h-screen")(
            file_sidebar(),
            pdf_viewer(),
            chat_panel()
        )
    )

serve()
```

**Step 2: Verify layout loads**

Run: `python app.py`
Expected: Three-column layout visible

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add three-column layout with DaisyUI"
```

---

## Phase 3: File Upload & Management

### Task 4: Implement PDF upload endpoint

**Files:**
- Modify: `app.py` - add upload route

**Step 1: Add upload route to app.py**

```python
from pathlib import Path
from starlette.requests import UploadFile

@rt("/upload")
async def post(file: UploadFile):
    filebuffer = await file.read()
    filepath = Path(UPLOAD_DIR) / file.filename
    filepath.write_bytes(filebuffer)

    # Parse PDF to Markdown
    from markitdown import MarkItDown
    md = MarkItDown()
    result = md.convert(str(filepath))
    md_filepath = filepath.with_suffix(filepath.suffix + ".md")
    md_filepath.write_text(result.text_content)

    return P(f"Uploaded {file.filename} and parsed to Markdown")
```

**Step 2: Update upload button to use HTMX**

Replace the static Button with:
```python
Form(hx_post="/upload", hx_target="#upload-result", enc_type="multipart/form-data")(
    Input(type="file", name="file", accept=".pdf", cls="file-input file-input-bordered file-input-sm w-full max-w-xs"),
    Button("Upload", type="submit", cls="btn btn-primary btn-sm mt-2"),
    Div(id="upload-result")
)
```

**Step 3: Test upload**

Run: `python app.py`
Upload a PDF file via web interface

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add PDF upload with Markdown parsing"
```

---

### Task 5: List uploaded files in sidebar

**Files:**
- Modify: `app.py` - add file listing

**Step 1: Add file listing function**

```python
def get_file_list():
    upload_path = Path(UPLOAD_DIR)
    pdf_files = list(upload_path.glob("*.pdf"))

    if not pdf_files:
        return P("No files uploaded", cls="text-sm text-gray-500")

    items = []
    for f in pdf_files:
        items.append(
            Div(
                cls="cursor-pointer hover:bg-base-300 p-2 rounded",
                hx_get=f"/select/{f.name}",
                hx_target="#pdf-frame",
            )(f.name)
        )
    return Div(*items)
```

**Step 2: Add select endpoint**

```python
@rt("/select/{fname}")
def get(fname: str):
    return Script(f"document.getElementById('pdf-frame').src = '/file/{fname}'")
```

**Step 3: Add file serving endpoint**

```python
@rt("/file/{fname}")
def get(fname: str):
    from starlette.responses import FileResponse
    return FileResponse(f"{UPLOAD_DIR}/{fname}", media_type="application/pdf")
```

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add file listing and selection"
```

---

## Phase 4: Annotations

### Task 6: Implement annotation storage

**Files:**
- Modify: `app.py` - add annotation endpoints
- Create: `annotation.py` - annotation helpers

**Step 1: Create annotation.py**

```python
import json
from pathlib import Path
from config import UPLOAD_DIR

def get_annotation_path(pdf_name: str) -> Path:
    return Path(UPLOAD_DIR) / f"{pdf_name}.annotations.json"

def load_annotations(pdf_name: str) -> dict:
    path = get_annotation_path(pdf_name)
    if path.exists():
        return json.loads(path.read_text())
    return {"highlights": [], "notes": []}

def save_annotations(pdf_name: str, data: dict):
    path = get_annotation_path(pdf_name)
    path.write_text(json.dumps(data, indent=2))
```

**Step 2: Add annotation endpoints**

```python
@rt("/annotations/{fname}")
def get(fname: str):
    return load_annotations(fname)

@rt("/annotations/{fname}")
async def post(fname: str, request: Request):
    data = await request.json()
    save_annotations(fname, data)
    return {"status": "saved"}
```

**Step 3: Commit**

```bash
git add annotation.py app.py
git commit -m "feat: add annotation storage"
```

---

## Phase 5: LLM Integration

### Task 7: Set up DeepSeek API client

**Files:**
- Modify: `llm.py` - LLM client

**Step 1: Create llm.py**

```python
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

# Tool definition for ripgrep search
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_document",
        "description": "Search the current document content using ripgrep. Use this when you need to find specific information or verify claims in the paper.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    }
}

def chat(messages: list, tools: list = None):
    return client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        tools=tools
    )
```

**Step 2: Test API connection**

```bash
python -c "from llm import chat; print(chat([{'role': 'user', 'content': 'Hello'}]))"
```

**Step 3: Commit**

```bash
git add llm.py
git commit -m "feat: add DeepSeek API client"
```

---

### Task 8: Implement chat endpoint with annotations

**Files:**
- Modify: `app.py` - add chat logic

**Step 1: Add chat endpoint**

```python
import subprocess
from llm import client, SEARCH_TOOL

@rt("/chat")
async def post(request: Request):
    form = await request.form()
    user_message = form.get("message")
    current_file = form.get("current_file", "")

    # Load annotations if file is selected
    annotations = {}
    if current_file:
        annotations = load_annotations(current_file)

    # Build context with annotations
    system_message = "You are a helpful research assistant helping the user understand a scientific paper."
    if annotations.get("highlights") or annotations.get("notes"):
        system_message += "\n\nUser has highlighted/annotated the following:\n"
        for h in annotations.get("highlights", []):
            system_message += f"- Highlight: {h.get('text', '')}\n"
        for n in annotations.get("notes", []):
            system_message += f"- Note: {n.get('text', '')}\n"

    # Get chat history from session (simplified - use file-based for now)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    # Chat with function calling
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        tools=[SEARCH_TOOL]
    )

    # Handle function call if present
    result = response.choices[0].message
    if result.tool_calls:
        # Run ripgrep search
        for call in result.tool_calls:
            if call.function.name == "search_document":
                query = eval(call.function.arguments)["query"]
                md_file = f"{UPLOAD_DIR}/{current_file}.md"
                try:
                    grep_result = subprocess.run(
                        ["rg", "-i", query, md_file, "-C", "2"],
                        capture_output=True, text=True
                    )
                    search_results = grep_result.stdout or "No results found"
                except:
                    search_results = "Error running search"

                # Add search results and continue
                messages.append({"role": "assistant", "content": result.content})
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": search_results
                })

                # Get final response
                response = client.chat.completions.create(
                    model=DEEPSEEK_MODEL,
                    messages=messages
                )
                result = response.choices[0].message

    return P(result.content or "No response")
```

**Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add LLM chat with function calling"
```

---

### Task 9: Make chat persistent

**Files:**
- Modify: `app.py` - add session management

**Step 1: Add session-based chat history**

For simplicity, use a global dict (for production, use proper session/storage):
```python
chat_history = {}

@rt("/chat")
async def post(request: Request):
    form = await request.form()
    user_message = form.get("message")
    session_id = "default"  # Simplify for MVP

    # Initialize or get history
    if session_id not in chat_history:
        chat_history[session_id] = []

    # ... rest of chat logic with history
```

**Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add chat history persistence"
```

---

## Phase 6: UI Refinements

### Task 10: Make sidebar collapsible

**Files:**
- Modify: `app.py` - add collapse toggle

**Step 1: Add collapse button and JavaScript**

```python
def file_sidebar():
    return Div(
        cls="flex flex-col h-full bg-base-200 w-64 min-h-screen p-4 transition-all duration-300",
        id="sidebar",
    )(
        Div(cls="flex justify-between items-center mb-4")(
            H2("Files", cls="text-xl font-bold"),
            Button(
                "←",
                cls="btn btn-sm",
                onclick="toggleSidebar()"
            )
        ),
        # ... rest
    )

# Add script
Script("""
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar.style.width === '0px') {
        sidebar.style.width = '16rem';
    } else {
        sidebar.style.width = '0px';
    }
}
""")
```

**Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add collapsible sidebar"
```

---

## Phase 7: Integration & Testing

### Task 11: Full integration test

**Step 1: Create test PDF and verify flow**

- Upload a PDF
- Select it in sidebar
- View in PDF viewer
- Add some annotations (via JS for now)
- Chat with LLM

**Step 2: Verify function calling works**

Ask LLM: "Search for [specific term]" and verify ripgrep is called

**Step 3: Commit**

```bash
git add .
git commit -m "feat: complete MVP with full integration"
```

---

## Execution Options

**Plan complete and saved to `docs/plans/2026-02-27-llm-lit-reader-impl-plan.md`. Two execution options:**

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
