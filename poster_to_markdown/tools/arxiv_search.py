import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import arxiv
import mcp.types as types
from dateutil import parser

DEFAULT_MAX_RESULTS = 10

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

search_tool = {
    "type": "function",
    "name": "handle_search",
    "description": (
        "Search for papers on arXiv with query and filtering, "
        "return the most relevant papers."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query string"},
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
            },
            "date_from": {
                "type": "string",
                "description": "Start date for filtering (ISO format)",
            },
            "date_to": {
                "type": "string",
                "description": "End date for filtering (ISO format)",
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "arXiv categories to filter by",
            },
            "include_abstract": {
                "type": "boolean",
                "description": "Whether to include paper abstracts in results",
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object with proper timezone handling."""
    if not date_str:
        return None
    try:
        date = parser.parse(date_str)
        if not date.tzinfo:
            date = date.replace(tzinfo=timezone.utc)
        return date
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing date {date_str}: {str(e)}")
        raise ValueError(f"Invalid date format: {date_str}")


def _is_within_date_range(
    date: datetime, start: Optional[datetime], end: Optional[datetime]
) -> bool:
    """Check if a date falls within the specified range."""
    if start and date < start:
        return False
    if end and date > end:
        return False
    return True


def _process_paper(paper: arxiv.Result, include_abstract: bool = True) -> Dict[str, Any]:
    """Process paper information with resource URI."""
    result = {
        "id": paper.get_short_id(),
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "categories": paper.categories,
        "published": paper.published.isoformat(),
        "url": paper.pdf_url,
        "resource_uri": f"arxiv://{paper.get_short_id()}",
        "doi": paper.doi,
        "comment": paper.comment,
        "journal_ref": paper.journal_ref,
        "primary_category": paper.primary_category,
    }

    if include_abstract:
        result["abstract"] = paper.summary

    return result


def handle_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle paper search requests with enhanced error handling and filtering."""
    try:
        client = arxiv.Client()
        max_results = int(arguments.get("max_results", DEFAULT_MAX_RESULTS))
        include_abstract = arguments.get("include_abstract", True)

        # Build search query with category filtering
        query = arguments["query"]
        if categories := arguments.get("categories"):
            category_filter = " OR ".join(f"cat:{cat}" for cat in categories)
            query = f"({query}) AND ({category_filter})"

        # Parse dates
        date_from = _parse_date(arguments.get("date_from"))
        date_to = _parse_date(arguments.get("date_to"))

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,  # Always sort by relevance
        )

        # Process results with date filtering
        results = []
        for paper in client.results(search):
            if _is_within_date_range(paper.published, date_from, date_to):
                results.append(_process_paper(paper, include_abstract))

            if len(results) >= max_results:
                break

        response_data = {
            "total_results": len(results),
            "query": query,
            "filters": {
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
                "categories": arguments.get("categories"),
            },
            "papers": results,
        }

        return [types.TextContent(type="text", text=json.dumps(response_data, indent=2))]

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    except arxiv.ArxivError as e:
        logger.error(f"arXiv API error: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: arXiv API error - {str(e)}")]
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return [
            types.TextContent(
                type="text", text=f"Error: An unexpected error occurred - {str(e)}"
            )
        ]
