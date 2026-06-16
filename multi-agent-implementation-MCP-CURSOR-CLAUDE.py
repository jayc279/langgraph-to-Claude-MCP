import os
from typing import List
from mcp.server.fastmcp import FastMCP
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults

# Initialize FastMCP server
mcp = FastMCP("LangGraph Migration Server")

# Set environmental keys if not already available in environment
os.environ.setdefault("TAVILY_API_KEY", "your_tavily_key")

@mcp.tool()
def fetch_primary_document(url: str = "https://lilianweng.github.io") -> str:
    """
    Loads and reads the core primary text or blog posts from a target URL.
    Returns the first 2000 characters of the content.
    """
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs[0].page_content[:2000]
    except Exception as e:
        return f"Error loading document: {str(e)}"

@mcp.tool()
def research_web_trends(question: str) -> List[str]:
    """
    Searches the live web using Tavily for current trends related to a specific question.
    Returns a list of external URL references.
    """
    try:
        search_tool = TavilySearchResults(max_results=2)
        query = f"Current trends related to: {question}"
        results = search_tool.invoke(query)
        return [r['url'] for r in results]
    except Exception as e:
        return [f"Error searching web: {str(e)}"]

if __name__ == "__main__":
    mcp.run(transport="stdio")















