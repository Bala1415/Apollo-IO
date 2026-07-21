import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

# Note: In a production environment, you might want to use a robust search API 
# like Tavily, Serper, or Google Custom Search. Here we define the interface 
# that you can implement with your preferred provider.

def search_web(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search the web for a given query and return a list of results.
    
    This is a placeholder that should be wired up to your actual search API 
    (e.g., TavilySearchResults from langchain_community).
    """
    logger.info(f"Searching web for: {query}")
    try:
        from langchain_community.tools.ddg_search import DuckDuckGoSearchResults
        tool = DuckDuckGoSearchResults(max_results=max_results)
        # The DuckDuckGo tool usually returns a string, so we will parse it.
        # Alternatively, we can use DuckDuckGoSearchRun for raw output.
        # Here we just use the tool and return the output inside our standard format.
        result = tool.invoke({"query": query})
        return [{"url": "https://duckduckgo.com", "content": str(result)}]
    except ImportError:
        logger.warning("langchain_community or duckduckgo-search is not installed. Returning mock results.")
        return [{"url": f"https://example.com/search?q={query}", "content": f"Mock search result for {query}"}]
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return [{"url": f"https://example.com/search?q={query}", "content": f"Error: {e}"}]

def search_company_news(company_domain: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search the web specifically for recent news about a company.
    """
    query = f"{company_domain} company recent news"
    return search_web(query, max_results)

def extract_website_content(url: str, max_chars: int = 5000) -> str:
    """
    Extract text content from a given website URL.
    """
    logger.info(f"Extracting content from: {url}")
    try:
        # Provide a standard User-Agent to avoid basic blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, header, footer, and nav elements to reduce noise
        for element in soup(["script", "style", "header", "footer", "nav", "noscript"]):
            element.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        
        # Limit the extracted text to avoid exceeding LLM context windows
        return text[:max_chars]
    except Exception as e:
        logger.error(f"Failed to extract content from {url}: {e}")
        return f"Error extracting content: {str(e)}"
