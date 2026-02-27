from fasthtml.common import *
from pathlib import Path
from starlette.requests import UploadFile
from config import UPLOAD_DIR
from markitdown import MarkItDown

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
        Form(hx_post="/upload", hx_target="#upload-result", enc_type="multipart/form-data")(
            Input(type="file", name="file", accept=".pdf", cls="file-input file-input-bordered file-input-sm w-full max-w-xs"),
            Button("Upload", type="submit", cls="btn btn-primary btn-sm mt-2"),
            Div(id="upload-result")
        ),
        Div(id="file-list", cls="flex-1 overflow-y-auto")(
            P("No files uploaded", cls="text-sm text-gray-500")
        )
    )

def pdf_viewer():
    return Div(
        cls="flex-1 bg-base-100 p-4",
        id="pdf-viewer",
    )(
        Iframe(src="", cls="w-full h-full border-none", id="pdf-frame", sandbox="allow-scripts allow-same-origin")
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
