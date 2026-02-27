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
