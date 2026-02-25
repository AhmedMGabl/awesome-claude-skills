---
name: vector-database-patterns
description: Vector database patterns covering embedding generation, similarity search, metadata filtering, indexing strategies, RAG integration, and Pinecone/Weaviate/Chroma usage.
---

# Vector Database Patterns

This skill should be used when building applications with vector databases for semantic search and AI. It covers embeddings, similarity search, filtering, indexing, RAG, and database clients.

## When to Use This Skill

Use this skill when you need to:

- Store and query vector embeddings
- Build semantic search applications
- Implement RAG (Retrieval-Augmented Generation)
- Choose between vector database providers
- Optimize indexing and search performance

## Embedding Generation

```python
from openai import OpenAI

client = OpenAI()

def get_embeddings(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]

# Single embedding
embedding = get_embeddings(["What is machine learning?"])[0]

# Batch embeddings
texts = ["doc1 content", "doc2 content", "doc3 content"]
embeddings = get_embeddings(texts)
```

## Pinecone

```python
from pinecone import Pinecone

pc = Pinecone(api_key="your-key")
index = pc.Index("my-index")

# Upsert vectors
index.upsert(vectors=[
    {"id": "doc1", "values": embedding1, "metadata": {"source": "wiki", "category": "science"}},
    {"id": "doc2", "values": embedding2, "metadata": {"source": "blog", "category": "tech"}},
])

# Query with metadata filter
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    filter={"category": {"$eq": "science"}},
)

for match in results.matches:
    print(f"{match.id}: {match.score:.4f} - {match.metadata}")
```

## Chroma

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"},
)

# Add documents (auto-embeds with default model)
collection.add(
    ids=["doc1", "doc2", "doc3"],
    documents=["Machine learning basics", "Deep learning guide", "NLP tutorial"],
    metadatas=[{"category": "ml"}, {"category": "dl"}, {"category": "nlp"}],
)

# Query
results = collection.query(
    query_texts=["neural networks"],
    n_results=3,
    where={"category": {"$in": ["ml", "dl"]}},
)
```

## Weaviate

```python
import weaviate
from weaviate.classes.config import Property, DataType, Configure

client = weaviate.connect_to_local()

# Create collection
collection = client.collections.create(
    name="Document",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    properties=[
        Property(name="title", data_type=DataType.TEXT),
        Property(name="content", data_type=DataType.TEXT),
        Property(name="category", data_type=DataType.TEXT),
    ],
)

# Insert
collection.data.insert({"title": "ML Guide", "content": "...", "category": "ml"})

# Search
response = collection.query.near_text(
    query="machine learning",
    limit=5,
    filters=weaviate.classes.query.Filter.by_property("category").equal("ml"),
)
```

## RAG Integration

```python
def rag_query(question: str, collection, llm_client) -> str:
    # 1. Generate query embedding
    query_embedding = get_embeddings([question])[0]

    # 2. Retrieve relevant documents
    results = collection.query(vector=query_embedding, top_k=5, include_metadata=True)
    context = "\n\n".join(match.metadata["text"] for match in results.matches)

    # 3. Generate answer with context
    response = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Answer based on context:\n\n{context}"},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content
```

## Indexing Strategies

```python
# Chunking documents for indexing
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "],
)

chunks = splitter.split_text(document_text)

# Index with metadata
vectors = []
for i, chunk in enumerate(chunks):
    embedding = get_embeddings([chunk])[0]
    vectors.append({
        "id": f"doc-{doc_id}-chunk-{i}",
        "values": embedding,
        "metadata": {
            "text": chunk,
            "doc_id": doc_id,
            "chunk_index": i,
            "source": "knowledge_base",
        },
    })

index.upsert(vectors=vectors, batch_size=100)
```

## Additional Resources

- Pinecone: https://docs.pinecone.io/
- Chroma: https://docs.trychroma.com/
- Weaviate: https://weaviate.io/developers/weaviate
