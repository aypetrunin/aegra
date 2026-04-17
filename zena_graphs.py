"""Adapters exposing zena graphs to aegra's file-based loader.

aegra loads graph files via `importlib.spec_from_file_location` and places them
under a synthetic `aegra_graphs.*` namespace, which breaks relative imports
inside target files. This wrapper uses absolute imports against the `src.*`
namespace package (on sys.path via `dependencies: ["/deps/langgraph"]` in
aegra.zena.json).

Secondary concern: `src.zena_create_graph` calls `asyncio.run()` at import time
to pre-build the 8 agent graphs — that works under legacy langgraph-api (no
running loop at module import), but fails under aegra, which loads graph
modules inside the FastAPI lifespan (running loop).

Workaround: we do NOT import `src.zena_create_graph`. We import only the
building blocks (state schema, MCP agent factory) and expose each graph as an
async 0-arg factory. Per aegra loader, async 0-arg factories are awaited once
at startup — equivalent to the original `asyncio.run()` fan-out, but done
inside aegra's event loop.
"""

import os

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

# Absolute imports against src.* (namespace package at /deps/langgraph/src).
# These modules do NOT call asyncio.run() at import time.
from src.zena_create_agent import create_agent_mcp
from src.zena_state import Context, InputState, OutputState, State
from src.zena_redialog_graph import graph_agent_redialog  # noqa: F401 — re-export


async def _make_agent_graph(mcp_port_env: str) -> CompiledStateGraph:
    port = os.getenv(mcp_port_env)
    agent = await create_agent_mcp(mcp_port=port)
    workflow = StateGraph(
        state_schema=State,
        input_schema=InputState,
        output_schema=OutputState,
        context_schema=Context,
    )
    workflow.add_node("agent", agent)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    return workflow.compile()


async def graph_sofia() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_SOFIA")


async def graph_anisa() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_ANISA")


async def graph_annitta() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_ANNITTA")


async def graph_anastasia() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_ANASTASIA")


async def graph_alena() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_ALENA")


async def graph_valentina() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_VALENTINA")


async def graph_marina() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_MARINA")


async def graph_egoistka() -> CompiledStateGraph:
    return await _make_agent_graph("MCP_PORT_EGOISTKA")
