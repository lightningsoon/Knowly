import os
import shutil
from typing import List, Dict
import gradio as gr
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, Docx2txtLoader
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

DB_PATH = "VectorStore"
TEMP_PATH = "temp_files"

# 确保必要的目录存在
os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)

# 初始化文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# 初始化嵌入模型
embeddings = HuggingFaceEmbeddings(
    model_name="shibing624/text2vec-base-chinese",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

app = FastAPI()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """处理上传的文档，进行文本提取、分块和向量化"""
    try:
        # 获取文件名（不含扩展名）作为知识库名称
        file_name = os.path.splitext(file.filename)[0]
        db_path = os.path.join(DB_PATH, file_name)
        
        # 检查是否已存在同名知识库
        if os.path.exists(db_path):
            return JSONResponse(
                status_code=400,
                content={"message": f"警告：已存在同名文件 '{file_name}'，请先删除或使用其他名称"}
            )
        
        # 保存上传的文件
        temp_file_path = os.path.join(TEMP_PATH, file.filename)
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 根据文件类型选择加载器
        if file.filename.endswith('.txt'):
            loader = TextLoader(temp_file_path, encoding='utf-8')
        elif file.filename.endswith('.docx'):
            loader = Docx2txtLoader(temp_file_path)
        else:
            os.remove(temp_file_path)
            return JSONResponse(
                status_code=400,
                content={"message": "不支持的文件类型"}
            )
        
        # 加载文档
        documents = loader.load()
        
        # 文本分块
        texts = text_splitter.split_documents(documents)
        
        # 创建向量存储
        vectorstore = FAISS.from_documents(texts, embeddings)
        
        # 保存向量存储
        vectorstore.save_local(db_path)
        
        # 清理临时文件
        os.remove(temp_file_path)
        
        return JSONResponse(
            status_code=200,
            content={"message": f"文档 '{file_name}' 处理成功"}
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"处理失败: {str(e)}"}
        )

@app.delete("/delete/{file_name}")
async def delete_document(file_name: str):
    """删除指定的文档及其向量存储"""
    try:
        db_path = os.path.join(DB_PATH, file_name)
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
            return JSONResponse(
                status_code=200,
                content={"message": f"文档 '{file_name}' 删除成功"}
            )
        return JSONResponse(
            status_code=404,
            content={"message": f"文档 '{file_name}' 不存在"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"删除失败: {str(e)}"}
        )

@app.get("/search")
async def search_documents(query: str, similarity_threshold: float = 0.2, top_k: int = 5):
    """搜索文档"""
    try:
        results = []
        for db_name in os.listdir(DB_PATH):
            db_path = os.path.join(DB_PATH, db_name)
            if os.path.isdir(db_path):
                vectorstore = FAISS.load_local(db_path, embeddings)
                docs = vectorstore.similarity_search_with_score(query, k=top_k)
                
                # 过滤相似度低于阈值的结果
                filtered_docs = [(doc, score) for doc, score in docs if score <= similarity_threshold]
                
                if filtered_docs:
                    doc_results = []
                    for doc, score in filtered_docs:
                        doc_results.append({
                            "similarity": 1 - score,
                            "content": doc.page_content
                        })
                    results.append({
                        "document": db_name,
                        "results": doc_results
                    })
        
        if not results:
            return JSONResponse(
                status_code=404,
                content={"message": "未找到相关结果"}
            )
        
        return JSONResponse(
            status_code=200,
            content={"results": results}
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"检索失败: {str(e)}"}
        )

@app.get("/list")
async def list_documents():
    """列出所有已处理的文档"""
    try:
        documents = [d for d in os.listdir(DB_PATH) if os.path.isdir(os.path.join(DB_PATH, d))]
        return JSONResponse(
            status_code=200,
            content={"documents": documents}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"获取文档列表失败: {str(e)}"}
        ) 