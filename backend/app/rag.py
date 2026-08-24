from dataclasses import dataclass
import re


@dataclass
class Document:
    title: str
    content: str


class SimpleRetriever:
    """Dependency-free retrieval layer for local development.

    The interface is intentionally compatible with replacing this implementation
    with Pinecone/pgvector later without changing the agent API.
    """

    def __init__(self):
        self.documents: list[Document] = []

    def add(self, title: str, content: str):
        self.documents.append(Document(title=title, content=content))

    def search(self, query: str, limit: int = 3) -> list[Document]:
        query_terms = set(re.findall(r"\w+", query.lower()))
        scored: list[tuple[int, Document]] = []
        for doc in self.documents:
            terms = set(re.findall(r"\w+", doc.content.lower()))
            score = len(query_terms & terms)
            scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for score, doc in scored[:limit] if score > 0]


retriever = SimpleRetriever()
