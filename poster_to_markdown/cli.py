"""
Poster to Markdown Converter

This module converts research poster images into structured markdown summaries.
It uses OpenAI's GPT-4.1-mini model to analyze poster content and generate
detailed markdown files.

Key Features:
- Supports multiple image formats (PNG, JPEG, HEIC)
- Automatically converts HEIC to JPEG
- Generates structured markdown with tags, authors, findings, and methodology
- Searches for related papers using arXiv
- Creates organized markdown files with consistent formatting

Usage:
    python -m poster_to_markdown -f <image_file> [-o <output_dir>]
    python -m poster_to_markdown -d <directory> [-o <output_dir>]
"""

import base64
import json
import os
from pathlib import Path

import click
import pillow_heif
from openai import OpenAI
from PIL import Image

from .prompts import FILENAME_PROMPT, POSTER_PROMPT
from .tools.arxiv_search import handle_search, search_tool


def process_image(image_path: Path, client: OpenAI) -> tuple[str, str]:
    """Process a single image and return markdown summary with filename.

    Args:
        image_path: Path to the input image file
        client: OpenAI client instance

    Returns:
        Tuple containing:
        - markdown_content: The generated markdown summary
        - title: The suggested filename for the markdown file

    Raises:
        Exception: If image processing or API call fails
    """
    temp_created = False
    temp_path = None

    try:
        # Convert HEIC to JPEG if needed
        if image_path.suffix.lower() == ".heic":
            heif_file = pillow_heif.read_heif(str(image_path))
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )
            # Save as temporary JPEG
            temp_path = image_path.with_suffix(".jpg")
            image.save(temp_path, format="JPEG")
            image_path = temp_path
            temp_created = True

        # Ensure image is in a supported format (convert to JPEG if needed)
        if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            img = Image.open(image_path)
            temp_path = image_path.with_suffix(".jpg")
            img.save(temp_path, format="JPEG")
            image_path = temp_path
            temp_created = True

        # Read image and encode properly as base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        input_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": POSTER_PROMPT},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]

        tools = [
            {"type": "web_search_preview"},
            search_tool,
        ]

        # Call OpenAI API
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=input_messages,
            tools=tools,
        )

        # Check for search function call
        for tool_call in response.output:
            if tool_call.type != "function_call":
                continue

            name = tool_call.name
            args = json.loads(tool_call.arguments)

            # Pretty print the tool call
            # print("\nTool Call:")
            # print(json.dumps({"name": name, "arguments": args}, indent=2))

            if name == "handle_search":
                result = handle_search(args)
            else:
                continue

            input_messages.append(tool_call)  # Not exactly sure why this is necessary
            input_messages.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result),
                }
            )
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=input_messages,
            tools=tools,
        )
        input_messages += [
            {
                "role": el.role,
                "content": el.content,
            }
            for el in response.output
        ]

        # Ask for filename after first prompt and tool calling
        input_messages.append(
            {
                "role": "user",
                "content": [{"type": "input_text", "text": FILENAME_PROMPT}],
            }
        )

        file_name_response = client.responses.create(
            model="gpt-4.1-mini",
            input=input_messages,
            store=False,
            # tools=tools,
        )

        # Result
        print(response.usage)
        print(file_name_response.usage)
        markdown_content = response.output[0].content[0].text
        title = (
            file_name_response.output[0].content[0].text.strip().replace(" ", "_")
        )  # Use the suggested filename and replace spaces with underscores

        return markdown_content, title

    finally:
        # Clean up temporary files
        if temp_created and temp_path and temp_path.exists():
            os.remove(temp_path)


def save_markdown(
    content: str, title: str, original_path: Path, output_dir: Path | None = None
) -> Path:
    """Save markdown content to a file.

    Args:
        content: Markdown content to save
        title: Filename (without extension)
        original_path: Path of the original image
        output_dir: Optional output directory (defaults to original image directory)

    Returns:
        Path to the saved markdown file
    """
    if output_dir is None:
        output_dir = original_path.parent
    else:
        if not output_dir.exists():
            click.echo(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{title}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def run(image_path: Path, output_dir: Path | None = None) -> None:
    """Process a single image file and save its markdown summary.

    Args:
        image_path: Path to the input image file
        output_dir: Optional output directory for markdown files
    """
    client = OpenAI()

    if image_path.suffix.lower() not in [
        ".png",
        ".jpg",
        ".jpeg",
        ".heic",
        # ".gif",
        # ".webp",
    ]:
        click.echo(f"Error: Unsupported file format {image_path}")
        return

    try:
        markdown_content, title = process_image(Path(image_path), client)
        output_path = save_markdown(markdown_content, title, Path(image_path), output_dir)
        click.echo(f"Created markdown summary: {output_path}")
    except Exception as e:
        click.echo(f"Error processing {image_path}: {str(e)}")


@click.command()
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Input image file (PNG, JPEG, or HEIC)",
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(exists=True),
    help="Process all images in directory",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Output directory for markdown files (default: same as input)",
)
def main(file: Path | None, directory: Path | None, output: Path | None) -> None:
    """Main entry point for the poster to markdown converter.

    Args:
        file: Path to a single image file
        directory: Path to a directory containing images
        output: Optional output directory for markdown files
    """
    if not file and not directory:
        click.echo("Error: Either -f or -d option must be provided")
        return

    output_dir = Path(os.path.expanduser(str(output))) if output else None

    if file:
        run(file, output_dir)

    if directory:
        dir_path = Path(directory)
        for image_path in dir_path.glob("*"):
            # If image path in md file exist, skip
            if (dir_path / f"{image_path.stem}.md").exists():
                continue
            run(image_path, output_dir)


if __name__ == "__main__":
    main()
