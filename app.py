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
