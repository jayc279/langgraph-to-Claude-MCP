# Conversion from LangChain / LangGraph flow to Claude MCP

## Parallelization Ready
- The `langchain-graph.py` can be changed such that the edges read_doc and research_web run at the same time using:
  - workflow.add_edge(START, "read_doc") and
  - workflow.add_edge(START, "research_web").

## Modularity:
- Each agent is a standalone function.
- If you want to change the search tool to a different API, you only edit one node.
    
## Structured Output:
- We keep the primary_doc_content separate from the chat messages in the State,
- ensuring the LLM doesn't get confused by "messy" data.

**This code defines two agents:**
- a Researcher (who reads the primary site) and
- a Fact-Checker (who fetches external references and asks follow-ups)

## Conversion of LangChain LangGraph flow to Claude MCP flow
1. convert the Python nodes (read_doc and research_web) into Model Context Protocol (MCP) tools. The orchestration and final synthesis logic are entirely removed from Python and handled dynamically by the LLM via its system prompt.

2. The MCP Server Script (mcp_agent_server.py)This standalone Python script replaces the LangChain/LangGraph infrastructure. It uses the FastMCP framework to automatically expose your tools via JSON-RPC standard over standard input/output (stdio).

### Instructions to run the MCP
1. System Instructions (.cursorrules or Claude System Prompt)
The execution graph structure is completely eliminated. Instead, you create a rule base that instructs the LLM how to coordinate its execution steps sequentially:

2. Prompt (These can be converted to Claude SKILL.md - using `skill-creator`:  
  
`You are an expert agent execution controller mimicking a strict pipeline. When answering a user's question, you MUST execution these exact operations in order:`
  
`1. Always run the 'fetch_primary_document' tool first to gather baseline information.`  
`2. Next, execute the 'research_web_trends' tool passing the user's question as input.`  
`3. Once both tools have returned their payloads, synthesize the final response.`  
  
`Your final output response must match this schema structure:`  
`Synthesized Answer: [Your answer comparing the source context and external data]`  
`Sources: [List out all the URLs returned from both tools]`  
`Follow-up: [Provide one thought-provoking follow-up question]`  
  
## How to Execute the Flow
- Instead of compiling and running a graph in terminal scripts, you invoke the system naturally inside Cursor Composer or Claude Code:

### Type this exact prompt inside Claude Code or Cursor Composer:
- "How does the memory component in LLM agents compare to human memory?"

`The LLM reads your instructions, identifies the fetch_primary_document and research_web_trends tools exposed through your local MCP instance, executes them natively over standard input/output streams, and generates the formatted final response.`

