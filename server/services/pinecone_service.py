# services/pinecone_service.py
import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from google import genai
from config import settings

# LangChain + LangChain-Pinecone imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
from langchain_pinecone import PineconeVectorStore
from models.pinecone import QueryResponse, QueryResult

from pinecone import Pinecone as PineconeClient, ServerlessSpec

class GeminiEmbeddings(Embeddings):
    def __init__(self, client: genai.Client, model: str):
        self.client = client
        self.model  = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.models.embed_content(model=self.model, contents=texts)
        return [e.values for e in resp.embeddings]

    def embed_query(self, text: str) -> list[float]:
        resp = self.client.models.embed_content(model=self.model, contents=[text])
        return resp.embeddings[0].values

class PineconeService:
    def __init__(self, index_name: str = "luvonai"):
        # init Pinecone SDK client
        self.pc = PineconeClient(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT,
        )
        # ensure index exists
        if index_name not in [i["name"] for i in self.pc.list_indexes()]:
            self.pc.create_index(
                name=index_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        self.index_name = index_name

        # Gemini client + embeddings wrapper
        self.client     = genai.Client(api_key=settings.GENAI_KEY)
        self.embeddings = GeminiEmbeddings(self.client, "gemini-embedding-exp-03-07")

        # text splitter
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)

    async def ingest_pdf_bytes(
        self,
        pdf_bytes: bytes,
        filename: str,
        namespace: str = "",
        metadata: dict = {},
    ):
        # write to temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
            tf.write(pdf_bytes)
            tmp_path = tf.name

        try:
            # load & split
            docs = PyPDFLoader(tmp_path).load_and_split(self.splitter)
            # attach any extra metadata
            for d in docs:
                d.metadata.update({"source": filename, **metadata})

            # ONE-LINER upsert via langchain-pinecone
            PineconeVectorStore.from_documents(
                docs,
                index_name=self.index_name,
                embedding=self.embeddings,
                namespace=namespace,
                pinecone_api_key=settings.PINECONE_API_KEY,
            )

            return {"status": "success", "chunks": len(docs)}
        finally:
            os.remove(tmp_path)

    async def query(
        self,
        prompt: str,
        top_k: int = 3,
        namespace: str = "",
        filter: dict = None,
    ) -> QueryResponse:
        # wrap existing index for querying
        vectordb = PineconeVectorStore(
            index=self.pc.Index(self.index_name),
            embedding=self.embeddings,
            namespace=namespace,
        )
        docs = vectordb.similarity_search(prompt, k=top_k, filter=filter)
        qrs = []
        for doc in docs:
            # if you need scores, switch to similarity_search_with_score
            # docs_with_scores = vectordb.similarity_search_with_score(...)
            qrs.append(
                QueryResult(
                    id=doc.metadata.get("id", ""),
                    score=doc.metadata.get("score", 0.0),
                    text=doc.page_content,
                    meta=doc.metadata,
                )
            )
        return QueryResponse(results=qrs)
# from pinecone import Pinecone, ServerlessSpec
# from config import settings
# from typing import List, Dict, Any
# import tiktoken
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from google import genai
# import os
# import PyPDF2
# import io
# from fastapi import FastAPI, UploadFile, File, HTTPException, status
# from models.pinecone import QueryRequest, QueryResponse, QueryResult

# class PineconeService:
#     def __init__(self):
#         self.pc = Pinecone(api_key=settings.PINECONE_KEY)
#         self.client = genai.Client(api_key=settings.GENAI_KEY)
#         self.model = "gemini-embedding-exp-03-07"
        
#         # self.embeddings = OpenAIEmbeddings(
#         #     openai_api_key=settings.OPENAI_API_KEY,
#         #     model="text-embedding-3-small"
#         # )
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=3000,
#             chunk_overlap=200,
#             length_function=len,
#         )
#         self.index_name = "luvonai"

#     def create_index(self, index_name: str, dimension: int = 3072, metric: str = "cosine"):
#         """
#         Create a new Pinecone index with specified parameters
        
#         Args:
#             index_name (str): Name of the index to create
#             dimension (int): Dimension of the vectors to be stored
#             metric (str): Distance metric to use (e.g., "cosine", "euclidean")
#         """
#         try:
#             self.pc.create_index(
#                 name=index_name,
#                 dimension=dimension,
#                 metric=metric,
#                 spec=ServerlessSpec(
#                     cloud="aws",
#                     region="us-east-1"
#                 )
#             )
#             print("Index created...")
#             return {"status": "success", "message": f"Index {index_name} created successfully"}
#         except Exception as e:
#             print("Index creation fail: " + str(e))
#             return {"status": "error", "message": str(e)}

#     async def process_pdf(self, file_content: bytes) -> List[str]:
#         """
#         Process a PDF file and extract text chunks
        
#         Args:
#             file_content (bytes): The PDF file content
            
#         Returns:
#             List[str]: List of text chunks
#         """
#         try:
#             # Read PDF content
#             pdf_file = io.BytesIO(file_content)
#             pdf_reader = PyPDF2.PdfReader(pdf_file)
            
#             # Extract text from all pages
#             text = ""
#             for page in pdf_reader.pages:
#                 text += page.extract_text()
            
#             # Split text into chunks
#             chunks = self.text_splitter.split_text(text)
#             return chunks
            
#         except Exception as e:
#             raise Exception(f"Error processing PDF: {str(e)}")

#     async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
#         """
#         Get embeddings for a list of texts
        
#         Args:
#             texts (List[str]): List of text chunks to embed
            
#         Returns:
#             List[List[float]]: List of embeddings
#         """
#         try:
#             embeddings = self.client.models.embed_content(
#                 model= self.model,
#                 contents=texts)
#             #embeddings = await self.embeddings.aembed_documents(texts)
#             return [e.values for e in embeddings.embeddings]
#         except Exception as e:
#             raise Exception(f"Error getting embeddings: {str(e)}")

#     async def process_and_upload_file(self, file_content: bytes, file_name: str, namespace: str, metadata: Dict[str, Any] = None):
#         """
#         Process a file, create embeddings, and upload to Pinecone
        
#         Args:
#             file_content (bytes): The file content
#             file_name (str): Name of the file
#             index_name (str): Name of the Pinecone index
#             metadata (Dict[str, Any], optional): Additional metadata to store with vectors
#         """
#         try:
#             print("WORKING....")
            
#             ## Creates index if it doesn't already exist (for each org)
#             self.create_index(self.index_name)
            
#             # Process file and get chunks
#             chunks = await self.process_pdf(file_content)
            
#             # Get embeddings for chunks
#             embeddings = await self.get_embeddings(chunks)
            
#             print(embeddings)
                        
#             # Prepare vectors for upload
#             vectors = []
#             for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
#                 vector_metadata = {
#                     "text": chunk,
#                     "file_name": file_name,
#                     "chunk_index": i
#                 }
#                 if metadata:
#                     vector_metadata.update(metadata)
                
#                 vectors.append({
#                     "id": f"{file_name}-chunk-{i}",
#                     "values": embedding,
#                     "metadata": vector_metadata
#                 })
            
#             # Upload to Pinecone
#             print("UPloading vectors")
#             return await self.upsert_vectors(self.index_name, vectors, namespace=namespace)
            
#         except Exception as e:
#             raise Exception(f"Error processing and uploading file: {str(e)}")

#     async def upsert_vectors(self, index_name: str, vectors: list, namespace: str = ""):
#         """
#         Upload vectors to a Pinecone index
        
#         Args:
#             index_name (str): Name of the index to upload to
#             vectors (list): List of vectors to upload
#             namespace (str): Optional namespace for the vectors
        
#         Returns:
#             dict: Status of the upload operation
#         """
#         try:
#             # Get the index
#             index = self.pc.Index(index_name)
            
#             # Upsert the vectors
#             upsert_response = index.upsert(
#                 vectors=vectors,
#                 namespace=namespace
#             )
            
#             return {
#                 "status": "success", 
#                 "message": f"Successfully uploaded {len(vectors)} vectors",
#                 "upserted_count": upsert_response.upserted_count
#             }
            
#         except Exception as e:
#             return {"status": "error", "message": str(e)}

#     async def query_vectors(self, prompt: str, top_k: int = 3, namespace: str = "", filter: Dict = None):
#         """
#         Query vectors from a Pinecone index
        
#         Args:
#             index_name (str): Name of the index to query
#             query_vector (List[float]): Query vector
#             top_k (int): Number of results to return
#             namespace (str): Optional namespace to query
#             filter (Dict): Optional filter criteria
            
#         Returns:
#             dict: Query results
#         """
#         # 1) Embed the prompt
#         try:
#             embeddings = await self.get_embeddings([prompt])
#             query_vector = embeddings[0]
            
#             index = self.pc.Index(self.index_name)
#             resp = index.query(
#                 vector=query_vector,
#                 top_k=top_k,
#                 namespace=namespace,
#                 filter=filter,
#                 include_values=False,
#                 include_metadata=True,
#             )

#             # 4) Build the response including chunk text
#             results = []
#             for m in resp.matches:
#                 print(m)
#                 # Pull out the chunk text stored in metadata
#                 chunk_text = m.metadata.get("text", "")
#                 # Optionally remove it from metadata if you don't want duplication
#                 # metadata = {k:v for k,v in m.metadata.items() if k != "text"}
#                 results.append(QueryResult(
#                     id=m.id,
#                     score=m.score,
#                     metadata=m.metadata
#                 ))

#             return QueryResponse(results=results)
    
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Pinecone query failed: {e}")
    