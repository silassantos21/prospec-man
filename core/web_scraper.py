"""Web scraping de URLs de referência usando httpx + BeautifulSoup."""

import asyncio
import re
from typing import Any
import httpx
from bs4 import BeautifulSoup

TIMEOUT = 20
CONTENT_LIMIT = 3000
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _extract_content(html: str, url: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "aside", "noscript", "iframe"]):
        tag.decompose()

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if not meta_desc:
        meta_desc = soup.find("meta", attrs={"property": "og:description"})
    description = meta_desc.get("content", "").strip() if meta_desc else ""

    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])[:10]]

    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"content|main|body", re.I))
        or soup.find(class_=re.compile(r"content|main|body", re.I))
        or soup.find("body")
    )
    raw_text = main_content.get_text(separator="\n", strip=True) if main_content else ""
    # Remove linhas vazias excessivas
    content = re.sub(r"\n{3,}", "\n\n", raw_text)[:CONTENT_LIMIT]

    og_image = soup.find("meta", attrs={"property": "og:image"})
    image_url = og_image.get("content", "") if og_image else ""

    return {
        "url": url,
        "title": title,
        "description": description,
        "headings": headings,
        "content": content,
        "image_url": image_url,
        "success": True,
        "error": None,
    }


async def _scrape_url(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    try:
        response = await client.get(url, follow_redirects=True, timeout=TIMEOUT)
        response.raise_for_status()
        return _extract_content(response.text, url)
    except httpx.TimeoutException:
        return {"url": url, "success": False, "error": "Timeout ao acessar a URL"}
    except httpx.HTTPStatusError as e:
        return {"url": url, "success": False, "error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"url": url, "success": False, "error": str(e)}


async def _scrape_all(urls: list[str]) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(headers=HEADERS, verify=False) as client:
        tasks = [_scrape_url(client, url) for url in urls]
        return await asyncio.gather(*tasks)


def scrape_urls(urls: list[str]) -> list[dict[str, Any]]:
    """Faz scraping de uma lista de URLs de forma assíncrona."""
    if not urls:
        return []
    return asyncio.run(_scrape_all(urls))


def format_scraped_content(scraped: list[dict[str, Any]]) -> str:
    """Formata o conteúdo raspado em markdown para envio ao Claude."""
    if not scraped:
        return ""

    parts = []
    for item in scraped:
        if item.get("success"):
            headings_str = " | ".join(item.get("headings", [])[:5]) or "N/A"
            part = (
                f"### Referência: {item['url']}\n"
                f"**Título:** {item.get('title', 'N/A')}\n"
                f"**Descrição:** {item.get('description', 'N/A')}\n"
                f"**Seções Encontradas:** {headings_str}\n\n"
                f"**Conteúdo Principal:**\n{item.get('content', '')}\n"
            )
        else:
            part = f"### Referência: {item['url']}\n**Erro:** {item.get('error', 'Desconhecido')}\n"
        parts.append(part)

    return "\n---\n".join(parts)
