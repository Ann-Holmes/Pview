from fasthtml.common import *
from pathlib import Path
from starlette.requests import Request, UploadFile
from config import UPLOAD_DIR
from markitdown import MarkItDown
import subprocess
from llm import client, SEARCH_TOOL
from annotation import load_annotations

# Simple session-based chat history (for MVP)
chat_sessions = {}

app = FastHTML(hdrs=(
    picolink(),
    Script(src="https://cdn.tailwindcss.com"),
    Script(src="https://cdn.jsdelivr.net/npm/daisyui@4"),
    Script("""
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const btn = document.getElementById('sidebar-toggle');
    if (sidebar.classList.contains('w-64')) {
        sidebar.classList.remove('w-64');
        sidebar.classList.add('w-0');
        sidebar.classList.add('overflow-hidden');
        btn.style.left = '0rem';
        btn.innerHTML = '→';
    } else {
        sidebar.classList.remove('w-0');
        sidebar.classList.remove('overflow-hidden');
        sidebar.classList.add('w-64');
        btn.style.left = '16rem';
        btn.innerHTML = '←';
    }
}
"""),
))

rt = app.route

def file_sidebar():
    return Div(
        cls="flex flex-col h-full bg-base-200 w-64 min-h-screen p-4 transition-all duration-300",
        id="sidebar",
    )(
        H2("Files", cls="text-xl font-bold mb-4"),
        Form(hx_post="/upload", hx_target="#upload-result", enc_type="multipart/form-data")(
            Input(type="file", name="file", accept=".pdf", cls="file-input file-input-bordered file-input-sm w-full max-w-xs"),
            Button("Upload", type="submit", cls="btn btn-primary btn-sm mt-2"),
            Div(id="upload-result")
        ),
        Div(id="file-list", cls="flex-1 overflow-y-auto mt-4")(
            get_file_list()
        )
    )

def pdf_viewer():
    return Div(
        cls="flex-1 bg-base-100 p-4",
        id="pdf-viewer",
    )(
        Iframe(src="", cls="w-full h-full border-none", id="pdf-frame", sandbox="allow-scripts allow-same-origin")
    )

def chat_panel(current_file: str = ""):
    return Div(
        cls="w-96 bg-base-200 p-4 flex flex-col",
        id="chat-panel",
    )(
        H2("LLM Chat", cls="text-xl font-bold mb-4"),
        Div(id="chat-messages", cls="flex-1 overflow-y-auto mb-4")(
            P("Start a conversation about your paper...", cls="text-sm")
        ),
        Form(hx_post="/chat", hx_target="#chat-messages")(
            Input(type="hidden", name="current_file", value=current_file),
            Input(name="message", cls="input input-bordered w-full", placeholder="Ask about the paper..."),
            Button("Send", cls="btn btn-primary mt-2")
        )
    )

@rt("/upload")
async def post(file: UploadFile):
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = Path(file.filename).name
        filepath = Path(UPLOAD_DIR) / safe_filename
        filepath.write_bytes(await file.read())

        # Parse PDF to Markdown
        md = MarkItDown()
        result = md.convert(str(filepath))
        md_filepath = filepath.parent / f"{filepath.stem}.md"
        md_filepath.write_text(result.text_content)

        return P(f"Uploaded {safe_filename} and parsed to Markdown")
    except Exception as e:
        return P(f"Error: {str(e)}", cls="text-error")

@rt("/select/{fname}")
def get(fname: str):
    # Update both PDF viewer and chat panel's current file
    return Script(f"""
        document.getElementById('pdf-frame').src = '/file/{fname}';
        document.querySelector('input[name="current_file"]').value = '{fname}';
    """)

@rt("/file/{fname}")
def get(fname: str):
    from starlette.responses import FileResponse
    return FileResponse(f"{UPLOAD_DIR}/{fname}", media_type="application/pdf")


@rt("/annotations/{fname}")
def get(fname: str):
    from annotation import load_annotations
    return load_annotations(fname)


@rt("/annotations/{fname}")
async def post(fname: str, request: Request):
    from annotation import save_annotations
    data = await request.json()
    save_annotations(fname, data)
    return {"status": "saved"}


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


@rt("/")
def get():
    return Titled("LLM Literature Reader",
        Div(cls="flex h-screen relative")(
            # External toggle button (always visible)
            Button(
                "←",
                cls="btn btn-sm absolute z-10",
                id="sidebar-toggle",
                onclick="toggleSidebar()",
                style="left: 16rem; transition: left 0.3s;"
            ),
            file_sidebar(),
            pdf_viewer(),
            chat_panel("")
        )
    )


@rt("/chat")
async def post(request: Request):
    form = await request.form()
    user_message = form.get("message")
    current_file = form.get("current_file", "")

    # Use current_file as session key
    session_key = current_file or "default"

    # Initialize or get history
    if session_key not in chat_sessions:
        chat_sessions[session_key] = []

    # Load annotations if file is selected
    annotations = {}
    if current_file:
        annotations = load_annotations(current_file)

    # Build system message with annotations
    system_message = "You are a helpful research assistant helping the user understand a scientific paper."
    if annotations.get("highlights") or annotations.get("notes"):
        system_message += "\n\nUser has highlighted/annotated the following:\n"
        for h in annotations.get("highlights", []):
            system_message += f"- Highlight: {h.get('text', '')}\n"
        for n in annotations.get("notes", []):
            system_message += f"- Note: {n.get('text', '')}\n"

    # Build messages with history
    messages = [{"role": "system", "content": system_message}]
    messages.extend(chat_sessions[session_key])
    messages.append({"role": "user", "content": user_message})

    # Chat with function calling
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[SEARCH_TOOL]
    )

    # Handle function call if present
    result = response.choices[0].message
    assistant_message = result.content or ""

    if result.tool_calls:
        for call in result.tool_calls:
            if call.function.name == "search_document":
                import json
                query = json.loads(call.function.arguments)["query"]
                md_base = current_file.replace(".pdf", "") if current_file.endswith(".pdf") else current_file
                md_file = f"{UPLOAD_DIR}/{md_base}.md"
                try:
                    grep_result = subprocess.run(
                        ["rg", "-i", query, md_file, "-C", "2"],
                        capture_output=True, text=True
                    )
                    search_results = grep_result.stdout or "No results found"
                except Exception as e:
                    search_results = f"Error running search: {e}"

                messages.append({"role": "assistant", "content": result.content})
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": search_results
                })

                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
                result = response.choices[0].message
                assistant_message = result.content or ""

    # Save to history
    chat_sessions[session_key].append({"role": "user", "content": user_message})
    chat_sessions[session_key].append({"role": "assistant", "content": assistant_message})

    return P(assistant_message or "No response")


serve()
