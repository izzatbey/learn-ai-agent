from dotenv import load_dotenv
from .agents import(
    PlannerAgent,
    CoderAgent,
    TesterAgent,
    DebuggerAgent,
    DocumentationAgent,
    CodeReviewerAgent,
    DependencyManagerAgent,
    get_agent
)
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph.message import add_messages

load_dotenv()

class CodingState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    task: str
    plan: str
    code_generated: bool
    tests_passed: bool
    needs_debugging: bool
    current_step: bool
    file_created: List[str]
    next_action: str
    
class CodingOrchestration:
    def __init__(self):
        self.planner = PlannerAgent()
        self.coder = CoderAgent()
        self.tester = TesterAgent()
        self.debugger = DebuggerAgent()
        self.documentation = DocumentationAgent()
        self.reviewer = CodeReviewerAgent()
        self.dependency_manager = DependencyManagerAgent()
        
    def _planner_node(self, state: CodingState) -> CodingState:
        """Node for planning the coding task"""
        
        
        plan = self.planner.run(state["task"])
        print(f"Planning completed:\n{plan}")
        return state
    