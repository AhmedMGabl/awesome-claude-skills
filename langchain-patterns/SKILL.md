---
name: langchain-patterns
description: LangChain patterns covering chains, agents, tools, RAG pipelines, memory, output parsers, vector stores, and LangGraph workflow orchestration.
---

# LangChain Patterns

This skill should be used when building LLM-powered applications with LangChain. It covers chains, agents, tools, RAG, memory, output parsers, vector stores, and LangGraph.

## When to Use This Skill

Use this skill when you need to:

- Build LLM-powered chains and agents
- Implement RAG (Retrieval-Augmented Generation)
- Create custom tools for agents
- Manage conversation memory
- Orchestrate workflows with LangGraph

## Basic Chain (LCEL)

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that summarizes text."),
    ("human", "Summarize the following:\n\n{text}"),
])

llm = ChatOpenAI(model="gpt-4o")
chain = prompt | llm | StrOutputParser()

result = chain.invoke({"text": "Long article content here..."})
```

## Structured Output

```python
from langchain_core.pydantic_v1 import BaseModel, Field

class ExtractedInfo(BaseModel):
    name: str = Field(description="Person's full name")
    email: str = Field(description="Email address")
    sentiment: str = Field(description="Overall sentiment: positive, negative, neutral")

structured_llm = llm.with_structured_output(ExtractedInfo)
result = structured_llm.invoke("Extract info from: Hi, I'm Alice (alice@example.com). Love your product!")
# result.name == "Alice", result.email == "alice@example.com"
```

## RAG Pipeline

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough

# Index documents
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = splitter.split_documents(raw_docs)
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# RAG chain
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer based on the context below.\n\nContext: {context}"),
    ("human", "{question}"),
])

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("What is the refund policy?")
```

## Custom Tools

```python
from langchain_core.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the product database for items matching the query."""
    results = db.search(query, limit=limit)
    return "\n".join(f"- {r.name}: ${r.price}" for r in results)

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified address."""
    email_service.send(to=to, subject=subject, body=body)
    return f"Email sent to {to}"

# Bind tools to model
llm_with_tools = llm.bind_tools([search_database, send_email])
```

## Agent with Tools

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

agent = create_react_agent(llm, [search_database, send_email])

result = agent.invoke({
    "messages": [HumanMessage(content="Find laptops under $500 and email the results to bob@example.com")]
})
```

## Memory / Chat History

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("placeholder", "{history}"),
    ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

response = with_history.invoke(
    {"input": "My name is Alice"},
    config={"configurable": {"session_id": "user-123"}},
)
```

## LangGraph Workflow

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    query: str
    context: str
    answer: str
    needs_review: bool

def retrieve(state: State) -> State:
    docs = retriever.invoke(state["query"])
    return {"context": format_docs(docs)}

def generate(state: State) -> State:
    answer = rag_chain.invoke({"context": state["context"], "question": state["query"]})
    return {"answer": answer, "needs_review": "I don't know" in answer}

def review(state: State) -> State:
    refined = llm.invoke(f"Improve this answer: {state['answer']}")
    return {"answer": refined.content}

def should_review(state: State) -> str:
    return "review" if state["needs_review"] else "end"

graph = StateGraph(State)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_node("review", review)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_conditional_edges("generate", should_review, {"review": "review", "end": END})
graph.add_edge("review", END)

app = graph.compile()
result = app.invoke({"query": "What is the return policy?"})
```

## Additional Resources

- LangChain: https://python.langchain.com/docs/
- LangGraph: https://langchain-ai.github.io/langgraph/
- LangSmith: https://docs.smith.langchain.com/
