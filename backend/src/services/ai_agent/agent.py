from typing import Optional

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from src.models.agent.agent_state_model import AgentStateModel
from src.services.ai_agent.nodes.greeting import Greeting
from src.services.ai_agent.nodes.intent_detection import IntentDetector
from src.services.ai_agent.nodes.make_order import MakeOder
from src.services.ai_agent.nodes.product import Product
from src.services.ai_agent.nodes.route_intent import route_intent
from src.services.ai_agent.nodes.should_continue import should_continue
from src.services.ai_agent.tools.product_tools import ProductTools
from src.services.common.tools.make_order_tool import make_order_tool


class AIAgent(BaseModel):
    collection_name: str = Field(
        default="e_commerce_ai", description="Collection name for vector database"
    )
    llm_temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description="Temperature for LLM generation"
    )

    agent_state: BaseModel = Field(
        default_factory=AgentStateModel,
        description="State of the AI agent, including user input and intent",
    )
    # These fields will be set during initialization
    workflow: Optional[StateGraph] = Field(default=None, exclude=True)
    graph: Optional[object] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    def __init__(self, **data):
        super().__init__(**data)
        self._setup_workflow()

    def _setup_workflow(self):
        """Initialize and configure the workflow graph"""
        self.workflow = StateGraph(AgentStateModel)
        self._add_nodes()
        self._setup_edges()
        self.graph = self.workflow.compile()

    def _add_nodes(self):
        """Add all nodes to the workflow"""
        # Add basic nodes
        self.workflow.add_node("intent_detection", IntentDetector(llm_temperature=0))
        self.workflow.add_node(
            "greeting", Greeting(llm_temperature=self.llm_temperature)
        )

        # Add product related nodes
        product_tools = ProductTools(
            collection_name=self.collection_name
        ).create_tools()
        self.workflow.add_node("product_tools", ToolNode(product_tools))

        product = Product(tools=product_tools, llm_temperature=self.llm_temperature)
        self.workflow.add_node("product", product)

        # Add order related nodes
        make_order = MakeOder(llm_temperature=self.llm_temperature)
        self.workflow.add_node("make_order", make_order)
        self.workflow.add_node("make_order_tools", ToolNode([make_order_tool]))

    def _setup_edges(self):
        """Configure all edges and entry point"""
        # Set entry point
        self.workflow.set_entry_point("intent_detection")

        # Conditional edges from intent_detection
        self.workflow.add_conditional_edges(
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
        self.workflow.add_conditional_edges(
            "product",
            should_continue,
            {
                "continue": "product_tools",
                "end": END,
            },
        )
        self.workflow.add_edge("product_tools", "product")

        # Conditional edges from make_order node
        self.workflow.add_conditional_edges(
            "make_order",
            should_continue,
            {
                "continue": "make_order_tools",
                "end": END,
            },
        )
        self.workflow.add_edge("make_order_tools", "make_order")

        # Terminal edges
        self.workflow.add_edge("greeting", END)

    def get_graph(self):
        """Get the compiled graph"""
        return self.graph

    def invoke(self, input_data):
        """Execute the agent workflow"""
        if not self.graph:
            raise ValueError(
                "Graph not initialized. Please ensure workflow setup is complete."
            )
        return self.graph.invoke(input_data)

    def stream(self, input_data):
        """Stream the agent workflow execution"""
        if not self.graph:
            raise ValueError(
                "Graph not initialized. Please ensure workflow setup is complete."
            )
        return self.graph.stream(input_data)

    def reset_workflow(self):
        """Reset and reinitialize the workflow"""
        self._setup_workflow()

    def update_config(self, **kwargs):
        """Update configuration and reinitialize workflow"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._setup_workflow()


if __name__ == "__main__":
    # Example usage
    agent = AIAgent(
        collection_name="e_commerce_ai",
        llm_temperature=0.1,
    )
    graph = agent.get_graph()
    print("Graph initialized:", graph is not None)
