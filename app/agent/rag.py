import os

DOC_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "it_policy.md")
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings

    if not os.path.exists(DOC_PATH):
        raise FileNotFoundError(f"Knowledge document missing at {DOC_PATH}")

    loader = TextLoader(DOC_PATH, encoding="utf-8")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=40)
    chunks = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    _retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return _retriever

def query_knowledge_base(query: str) -> str:
    retriever = get_retriever()
    results = retriever.invoke(query)
    if not results:
        return "No relevant corporate IT documentation located for this query."
    return "\n\n".join([doc.page_content for doc in results])