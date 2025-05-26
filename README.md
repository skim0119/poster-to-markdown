# Poster to Markdown CLI

A command-line tool that converts research poster images into well-structured markdown summaries. It leverages OpenAI's API for intelligent content extraction and ArXiv integration for finding related research papers.

## Features

- **Poster Processing**: Convert poster images (PNG, JPEG, HEIC) to structured markdown summaries
- **ArXiv Integration**: Search for related papers and automatically include them in summaries
- **Multiple Formats**: Support for various image formats including HEIC
- **Batch Processing**: Process entire directories of poster images

## Installation

```bash
pip install poster-to-markdown
```

Then set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Usage

> Currently, we support png, jpeg, and heic image formats.

One can customize the prompt by modifying `poster_to_markdown/prompts.py`.

### Process Posters

Convert poster images to markdown summaries:

```bash
# Process a single poster
poster-to-markdown -f poster.jpg

# Process entire directory
poster-to-markdown -d /path/to/posters -o /path/to/output
```

### Note

The amount of token it takes to process a poster is around 1k-10k for input and 3k-10k for output.
This number may vary depending on the size and detail of the poster image or the model used.
