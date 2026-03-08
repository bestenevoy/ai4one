#!/usr/bin/env python3
"""
MCP Web tools for agents to search and fetch web content.
- Web search via DuckDuckGo (no API key required)
- Web page content extraction
- URL validation and info

Run this module to start a standalone MCP server.
"""
from __future__ import annotations

import argparse
import re
import urllib.parse
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP


def parse_args():
    parser = argparse.ArgumentParser(description="MCP Web Server")
    parser.add_argument(
        "--port", type=int, default=50004, help="Server port (default: 50004)"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    parser.add_argument(
        "--transport", "-t",
        default="stdio",
        choices=["stdio", "sse", "mcp", "streamable-http"],
        help="Transport protocol",
    )

    try:
        args = parser.parse_args()
    except SystemExit:
        class Args:
            port = 50004
            host = "0.0.0.0"
            log_level = "INFO"
            transport = "stdio"
        args = Args()
    return args


mcp = FastMCP("ai4one_web_server")


# ========== Web Search ==========

@mcp.tool()
def web_search(
    query: str,
    max_results: int = 5,
    region: str = "us-en",
) -> List[Dict]:
    """Search the web using DuckDuckGo (no API key required).

    Args:
        query: Search query string.
        max_results: Maximum number of results to return (default: 5, max: 20).
        region: Region for search results (e.g., 'us-en', 'zh-cn', 'ja-jp').

    Returns:
        List of search results with title, url, and snippet.
    """
    max_results = min(max_results, 20)

    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return [{"error": "duckduckgo-search not installed. Run: pip install duckduckgo-search"}]

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region=region, max_results=max_results))

        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")[:500] if r.get("body") else "",
            })
        return formatted
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


@mcp.tool()
def web_search_news(
    query: str,
    max_results: int = 5,
    region: str = "us-en",
) -> List[Dict]:
    """Search news using DuckDuckGo.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.
        region: Region for search results.

    Returns:
        List of news results with title, url, snippet, and date.
    """
    max_results = min(max_results, 20)

    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return [{"error": "duckduckgo-search not installed"}]

    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, region=region, max_results=max_results))

        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("body", "")[:500] if r.get("body") else "",
                "source": r.get("source", ""),
                "date": r.get("date", ""),
            })
        return formatted
    except Exception as e:
        return [{"error": f"News search failed: {str(e)}"}]


# ========== Web Page Fetch ==========

@mcp.tool()
def web_fetch(
    url: str,
    timeout: int = 30,
    max_length: int = 10000,
) -> Dict:
    """Fetch and extract text content from a web page.

    Args:
        url: URL to fetch.
        timeout: Request timeout in seconds (default: 30).
        max_length: Maximum text length to return (default: 10000).

    Returns:
        Dictionary with title, text, url, and metadata.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return {"error": "Required packages not installed. Run: pip install requests beautifulsoup4"}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Get title
        title = ""
        if soup.title:
            title = soup.title.string or ""

        # Get main content
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|article|post|entry", re.I))
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

        # Clean up text
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines)

        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length] + "\n... [truncated]"

        return {
            "title": title,
            "text": text,
            "url": url,
            "length": len(text),
            "status": response.status_code,
        }
    except requests.exceptions.Timeout:
        return {"error": f"Request timed out after {timeout} seconds"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to parse page: {str(e)}"}


@mcp.tool()
def web_fetch_links(
    url: str,
    timeout: int = 30,
    max_links: int = 50,
) -> Dict:
    """Extract all links from a web page.

    Args:
        url: URL to fetch.
        timeout: Request timeout in seconds.
        max_links: Maximum number of links to return.

    Returns:
        Dictionary with url, links list, and count.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return {"error": "Required packages not installed"}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        base_url = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))

        links = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)[:100]

            # Resolve relative URLs
            if href.startswith("/"):
                href = base_url + href
            elif not href.startswith(("http://", "https://")):
                continue

            if href not in seen:
                seen.add(href)
                links.append({"url": href, "text": text})

            if len(links) >= max_links:
                break

        return {
            "url": url,
            "links": links,
            "count": len(links),
        }
    except Exception as e:
        return {"error": f"Failed to fetch links: {str(e)}"}


# ========== URL Utilities ==========

@mcp.tool()
def url_info(url: str) -> Dict:
    """Get information about a URL without fetching the full content.

    Args:
        url: URL to check.

    Returns:
        Dictionary with URL components and metadata.
    """
    try:
        import requests
    except ImportError:
        return {"error": "requests not installed"}

    parsed = urllib.parse.urlparse(url)

    info = {
        "url": url,
        "scheme": parsed.scheme,
        "domain": parsed.netloc,
        "path": parsed.path,
        "query": parsed.query,
        "is_valid": bool(parsed.scheme and parsed.netloc),
    }

    # Try to get headers
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        info["status_code"] = response.status_code
        info["content_type"] = response.headers.get("Content-Type", "")
        info["content_length"] = response.headers.get("Content-Length", "")
        info["final_url"] = response.url if response.url != url else url
        info["accessible"] = response.status_code < 400
    except Exception as e:
        info["accessible"] = False
        info["error"] = str(e)

    return info


@mcp.tool()
def url_encode(text: str) -> str:
    """Encode text for use in a URL.

    Args:
        text: Text to encode.

    Returns:
        URL-encoded string.
    """
    return urllib.parse.quote(text, safe="")


@mcp.tool()
def url_decode(encoded: str) -> str:
    """Decode a URL-encoded string.

    Args:
        encoded: URL-encoded string.

    Returns:
        Decoded string.
    """
    return urllib.parse.unquote(encoded)


# ========== Server Runner ==========

def run_server():
    import anyio

    args = parse_args()

    mcp.settings.port = args.port
    mcp.settings.host = args.host

    match args.transport:
        case "stdio":
            anyio.run(mcp.run_stdio_async)
        case "sse":
            mount_path = None
            print(f"Server URL: http://{args.host}:{args.port}/{args.transport}")
            anyio.run(lambda: mcp.run_sse_async(mount_path))
        case "mcp":
            print(f"Server URL: http://{args.host}:{args.port}/{args.transport}")
            anyio.run(mcp.run_streamable_http_async)


if __name__ == "__main__":
    run_server()
