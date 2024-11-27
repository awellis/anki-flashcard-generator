# Anki flashcard generator


In this project, I'm using an LLM to automatically generate flashcards for spaced repetition software [Anki](https://apps.ankiweb.net/).


## Setup

1. Create a new virtual environment:

```bash
python -m venv .venv
```

Or use the `Create environment` action in VSCode.

2. Activate the environment:

In `bash` or `zsh`:

```bash
source .venv/bin/activate
```

In `fish`:
```fish
source .venv/bin/activate.fish
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```


4. Create a `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=<your-openai-api-key>
```

5. For further instructions, see [the Anki task](https://virtuelleakademie.github.io/promptly-engineered/projects/anki/).
