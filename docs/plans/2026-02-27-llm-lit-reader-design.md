# LLM-Assisted Literature Reader - Design Document

**Date**: 2026-02-27
**Status**: Draft for Approval

## 1. Project Overview

A web-based literature reading tool with LLM assistance, built using FastHTML and DaisyUI. Users can upload PDF papers, read them in an embedded viewer, highlight/annotate, and chat with an LLM that has access to the paper content.

## 2. Technology Stack

- **Web Framework**: FastHTML (Python)
- **UI Library**: DaisyUI + Tailwind CSS
- **PDF Processing**: markitdown (convert PDF to Markdown for LLM context)
- **Search**: ripgrep (for LLM to query document content)
- **LLM Provider**: DeepSeek API (OpenAI-compatible)

## 3. UI Layout

```
+------------------+------------------------+------------------------+
|  File Sidebar    |   PDF Reader          |   LLM Chat            |
|  (Collapsible)  |   (iframe embed)      |   (DaisyUI chat)      |
|                  |                        |                        |
|  - Upload btn    |   [PDF content]       |   [Messages]          |
|  - File list     |                        |   [Input]             |
|                  |                        |                        |
+------------------+------------------------+------------------------+
```

- **Left Sidebar** (collapsible): File navigation, upload button, PDF file list
- **Center Panel**: Embedded PDF viewer (iframe)
- **Right Panel**: LLM chat interface with DaisyUI chat bubbles

## 4. Core Features

### 4.1 File Management
- Upload PDF files via web form
- Store files in `uploads/` directory (project-relative)
- Parse uploaded PDF to Markdown using markitdown (stored as `.md`)
- Store annotations in `<filename>.pdf.annotations.json`

### 4.2 PDF Viewer
- Use iframe to embed browser's native PDF viewer
- Display selected PDF from uploads folder
- Support basic highlight and annotation via JavaScript

### 4.3 Annotations
- Each PDF has a corresponding JSON file for annotations
- Annotation structure:
  ```json
  {
    "highlights": [
      {"text": "highlighted text", "page": 1, "position": {...}}
    ],
    "notes": [
      {"text": "note content", "page": 1, "highlightId": "..."}
    ]
  }
  ```

### 4.4 LLM Chat Integration
- Chat interface using DaisyUI chat component
- **Always include** user highlights/annotations in LLM context
- **LLM can autonomously** use ripgrep to search Markdown content for relevant context
- Support function calling for ripgrep search

### 4.5 LLM Function Calling
Define a tool for LLM to search document:
```json
{
  "name": "search_document",
  "description": "Search the current document using ripgrep",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Search query"}
    }
  }
}
```

## 5. Data Flow

1. **Upload**: User uploads PDF → save to `uploads/` → parse to Markdown
2. **View**: Select file → load PDF in iframe
3. **Annotate**: Add highlight/note → save to JSON file
4. **Chat**:
   - User sends message
   - System includes annotation data in prompt
   - LLM can call `search_document` function → run ripgrep → return results
   - LLM generates response

## 6. API Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Main application page |
| `/upload` | POST | Upload PDF file |
| `/files` | GET | List uploaded files |
| `/file/{name}` | GET | Serve PDF file |
| `/markdown/{name}` | GET | Serve parsed Markdown |
| `/annotations/{name}` | GET/POST | Get/save annotations |
| `/chat` | POST | LLM chat endpoint |
| `/search` | POST | ripgrep search endpoint |

## 7. File Structure

```
Pview/
├── app.py              # Main FastHTML application
├── uploads/            # Uploaded PDFs and parsed Markdown
│   ├── paper1.pdf
│   ├── paper1.pdf.md
│   ├── paper1.pdf.annotations.json
│   └── ...
├── docs/
│   └── plans/         # Design documents
└── requirements.txt   # Dependencies
```

## 8. Dependencies

```
fasthtml
markitdown
openai
python-dotenv
```

## 9. Acceptance Criteria

- [ ] Three-column layout with collapsible left sidebar
- [ ] PDF upload works, files stored in uploads/
- [ ] PDF parsed to Markdown on upload
- [ ] PDF displays in center panel via iframe
- [ ] Highlight and annotate text (saved to JSON)
- [ ] Chat interface with DaisyUI styling
- [ ] LLM receives highlights/annotations in every message
- [ ] LLM can search document content via ripgrep
- [ ] Configuration via environment variables (API keys, etc.)

## 10. Future Considerations (Out of Scope for MVP)

- Multiple document support with cross-document search
- Rich text annotations
- Export annotations
- User authentication
- Mobile responsive design
