# Poster to Markdown CLI

A powerful command-line tool that converts research poster images into well-structured markdown summaries. It leverages OpenAI's Vision API for intelligent content extraction and includes ArXiv integration for finding related research papers.

## Features

- **Poster Processing**: Convert poster images (PNG, JPEG, HEIC) to structured markdown summaries
- **ArXiv Integration**: Search for related papers and automatically include them in summaries
- **Multiple Formats**: Support for various image formats including HEIC
- **Batch Processing**: Process entire directories of poster images
- **Standalone ArXiv Search**: Search ArXiv papers with advanced filtering

## Installation

```bash
pip install poster-to-markdown
```

Then set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Usage

### Process Posters

Convert poster images to markdown summaries:

```bash
# Process a single poster
poster-to-markdown -f poster.jpg

# Process entire directory
poster-to-markdown -d /path/to/posters
```