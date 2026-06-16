# This code defines two agents:
#  - a Researcher (who reads the primary site) and
#  - a Fact-Checker (who fetches external references and asks follow-ups)

# This script is parallelization Ready:
#   change the edges so read_doc and research_web run at the same time using:
#   - workflow.add_edge(START, "read_doc") and
#   - workflow.add_edge(START, "research_web").

import os
from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 1. Configuration & Tools
os.environ["TAVILY_API_KEY"] = "your_tavily_key"
os.environ["OPENAI_API_KEY"] = "your_openai_key"
search_tool = TavilySearchResults(max_results=2)

llm = ChatOpenAI(model="gpt-4o-mini")

# 2. Define the Shared State
class AgentState(TypedDict):
  messages: Annotated[list, add_messages]
  primary_doc_content: str
  external_refs: List[str]
  question: str

# 3. Agent 1: The Document Reader
def doc_agent(state: AgentState):
  # Example: Loading a specific blog post or doc site
  loader = WebBaseLoader("https://lilianweng.github.io")
  docs = loader.load()
  content = docs[0].page_content[:2000] # Limit for demo
  return {"primary_doc_content": content}

# 4. Agent 2: The Web Researcher (External Data)
def research_agent(state: AgentState):
  query = f"Current trends related to: {state['question']}"
  results = search_tool.invoke(query)
  refs = [r['url'] for r in results]
  return {"external_refs": refs, "messages": [f"Found external data at: {refs}"]}

# 5. Agent 3: The Synthesizer & Follow-up

def synthesis_agent(state: AgentState):
  prompt = f"""
    Based on this primary text: {state['primary_doc_content']}
    And these external references: {state['external_refs']}
    Answer the user question: {state['question']}
    Then, provide a list of sources.
    Finally, ask a thought-provoking follow-up question.
  """

  response = llm.invoke(prompt)
  return {"messages": [response]}

# 6. Build the Workflow
workflow = StateGraph(AgentState)
workflow.add_node("read_doc", doc_agent)
workflow.add_node("research_web", research_agent)
workflow.add_node("synthesize", synthesis_agent)

# Define the flow
workflow.add_edge(START, "read_doc")
workflow.add_edge("read_doc", "research_web")
workflow.add_edge("research_web", "synthesize")
workflow.add_edge("synthesize", END)

# 7. Execute
app = workflow.compile()
input_data = {"question": "How does the memory component in LLM agents compare to human memory?"}
for output in app.stream(input_data):
  for key, value in output.items():
      print(f"\n--- Node: {key} ---")

     if "messages" in value:
        print(value["messages"][-1])




























