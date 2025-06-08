from typing import Annotated, Any, Dict, List

from langchain_core.messages import AIMessage, AnyMessage, BaseMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from core.services.ai_agent.nodes.greeting import Greeting
from core.services.ai_agent.nodes.intent_detection import IntentDetector
from core.services.ai_agent.nodes.make_order import MakeOder
from core.services.ai_agent.nodes.product import Product
from core.services.ai_agent.nodes.route_intent import route_intent
from core.services.ai_agent.nodes.should_continue import should_continue
from core.services.ai_agent.state.agent_state import AgentState
from core.services.ai_agent.tools.product_tools import ProductTools
from core.services.common.tools.make_order_tool import make_order_tool

workflow = StateGraph(AgentState)


workflow.add_node("intent_detection", IntentDetector(llm_temperature=0))
workflow.add_node("greeting", Greeting(llm_temperature=0.1))

product_tools = ProductTools(collection_name="e_commerce_ai").create_tools()
workflow.add_node("product_tools", ToolNode(product_tools))

product = Product(tools=product_tools, llm_temperature=0.1)
workflow.add_node("product", product)

make_order = MakeOder(llm_temperature=0.1)
workflow.add_node("make_order", make_order)

workflow.add_node("make_order_tools", ToolNode([make_order_tool]))

workflow.set_entry_point("intent_detection")

# Conditional edges from intent_detection
workflow.add_conditional_edges(
    "intent_detection",
    route_intent,
    {
        "product": "product",
        "greeting": "greeting",
        "make_order": "make_order",
        "other": "greeting",  # Default to greeting for unrecognized intents
    },
)

# Conditional edges from product node
workflow.add_conditional_edges(
    "product",
    should_continue,
    {
        "continue": "product_tools",
        "end": END,
    },
)
workflow.add_edge("product_tools", "product")

workflow.add_conditional_edges(
    "make_order",
    should_continue,
    {
        "continue": "make_order_tools",
        "end": END,
    },
)
workflow.add_edge("make_order_tools", "make_order")

# Edge from tools back to product for continued conversation

# Edge from greeting to end
workflow.add_edge("greeting", END)
workflow.add_edge("make_order", END)

graph = workflow.compile()
