# Pview

Pview (Paper view) a three column web application for reading papers. It is built using the FastHTML framework and OpenAI's API. The left column is for the list of the paper, the middle column is for the paper reading, and right column is for Chat-like interaction with the paper. The right column is powered by OpenAI's API or OpenAI compatible API, which allows users to ask questions about the paper and get answers in real-time.

## Technology Stack

- `python`: The programming language used in this project, version 3.12 or above is recommended.
- `python-fastahtml`: FastHTML framework for building web applications, please refer to [python-fastahtml](https://www.fastht.ml/docs/llms-ctx.txt) for more details.
- `openai`: OpenAI SDK
- `uv`: A modern Python package manager, please refer to [uv](https://pypi.org/project/uv/) for more details.

## Environment

Please use `uv` to manage the dependencies in this project. You can run `uv --help` to see the usage of `uv`.

Here are the useful commands:

- Initialize a project: `uv init`
- Install dependencies: `uv sync`
- Add a dependency: `uv add <package-name>`
- Remove a dependency: `uv remove <package-name>`
- Run a script: `uv run <script-name>`

## Version Control

### commit message

```text
<emoji> <type>(<scope>): <description>
```

1. Emoji Types:
    - ✨ feat: New features
    - 🐞 fix: Bug fixes
    - 🦄 refactor: Code refactoring, no function changes
    - 🌈 style: Style modifications
    - 🐎 ci: CI related changes
    - 📃 docs: Documentation updates
    - 🐳 chore: Miscellaneous changes
    - 🎉 init: Initial commit

2. Scope:
    - Use a short, descriptive scope
    - Basically, it should be the name of the file or module affected
    - If no scope is applicable, omit it

3. Description:
    - Write a concise description of the changes
    - Use present tense ("add feature" not "added feature")
    - Start with lowercase

**IMPORTANT**: Please don't include any "Co-Authored-By".
