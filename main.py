import getpass
import os
LANGSMITH_api_key = ''
ath = ""

groq_spi = ""

from langchain_community.llms import Ollama
from langchain_groq import ChatGroq

from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# llm = Ollama(
#     model="llama3"
# )  # assuming you have Ollama installed and have llama3 model pulled with `ollama pull llama3 `

llm = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key=groq_spi # Optional if not set as an environment variable
)

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


# _set_env("ANTHROPIC_API_KEY")
_set_env("LANGSMITH_API_KEY")

os.environ["LANGCHAIN_TRACING_V2"] = 'false'
os.environ["LANGCHAIN_PROJECT"] = "LangGraph Tutorial"


from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


# llm = ChatAnthropic(model="claude-3-haiku-20240307")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)


graph_builder.add_edge(START, "chatbot")


graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            print("Assistant:", value["messages"][-1])


_set_env("TAVILY_API_KEY")
# Check in : https://app.tavily.com/home
tool = TavilySearchResults(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")
