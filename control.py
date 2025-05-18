import os
import shutil
from typing import List, Dict, Optional
import requests
from data import DocumentData
import dashscope
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
# 添加llama-index相关导入
from llama_index.core import VectorStoreIndex, Settings, SimpleDirectoryReader
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from llama_index.postprocessor.dashscope_rerank import DashScopeRerank

# 设置嵌入模型
EMBED_MODEL = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
    text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
)
Settings.embed_model = EMBED_MODEL

class DocumentController:
    def __init__(self):
        self.db_path = "VectorStore"
        self.temp_path = "temp_files"
        self.data = DocumentData()
        os.makedirs(self.db_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
    
    def process_document(self, file_path: str) -> Dict:
        """处理文档，包括文本提取和向量化"""
        try:
            file_name = os.path.basename(file_path)
            db_name = os.path.splitext(file_name)[0]
            
            # 保存文档
            # success, msg = self.data.save_document(file_path, file_name)
            # if not success:
            #     return {
            #         "success": False,
            #         "message": msg
            #     }
            
            # 使用llama-index处理文档
            try:
                # 读取文档
                documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
                
                # 创建索引
                index = VectorStoreIndex.from_documents(documents)
                
                # 保存向量存储
                db_path = os.path.join(self.db_path, db_name)
                # 如果向量库已存在，先删除再创建
                if os.path.exists(db_path):
                    shutil.rmtree(db_path)
                
                os.makedirs(db_path, exist_ok=True)
                index.storage_context.persist(persist_dir=db_path)
                
                return {
                    "success": True,
                    "message": f"文档 '{db_name}' 处理成功"
                }
            except Exception as e:
                # 报告错误
                return {
                    "success": False,
                    "message": f"向量化失败: {str(e)}"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"处理失败: {str(e)}"
            }
    
    def delete_document(self, file_name: str) -> Dict:
        """删除文档及其向量存储"""
        try:
            if self.data.delete_document(file_name):
                # 删除向量存储
                db_name = os.path.splitext(file_name)[0]
                db_path = os.path.join(self.db_path, db_name)
                if os.path.exists(db_path):
                    shutil.rmtree(db_path)
                
                return {
                    "success": True,
                    "message": f"文档 '{file_name}' 删除成功"
                }
            return {
                "success": False,
                "message": f"文档 '{file_name}' 不存在"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"删除失败: {str(e)}"
            }
    
    def search_documents(self, query: str, similarity_threshold: float = 0.2, top_k: int = 5) -> Dict:
        """搜索所有文档"""
        try:
            # 获取所有知识库
            docs = self.data.list_documents()
            if not docs:
                return {
                    "success": True,
                    "results": []
                }
            
            # 合并所有知识库结果
            all_results = []
            for doc in docs:
                db_name = os.path.splitext(doc)[0]
                doc_results = self._query_document(query, db_name, similarity_threshold, top_k)
                if doc_results:
                    all_results.extend(doc_results)
            
            # 按相似度排序并取前top_k个
            all_results = sorted(all_results, key=lambda x: x["similarity"], reverse=True)[:top_k]
            
            return {
                "success": True,
                "results": all_results
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"检索失败: {str(e)}"
            }
    
    def search_documents_with_db(self, query: str, db_name: str, similarity_threshold: float = 0.2, top_k: int = 5) -> Dict:
        """定向单文件检索"""
        try:
            results = self._query_document(query, db_name, similarity_threshold, top_k)
            if results is None:
                return {
                    "success": False,
                    "message": f"知识库 '{db_name}' 不存在或检索失败"
                }
            
            return {
                "success": True,
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"检索失败: {str(e)}"
            }
    
    def _query_document(self, prompt: str, db_name: str, similarity_threshold: float = 0.2, chunk_cnt: int = 5) -> List[Dict]:
        """使用llama-index查询文档"""
        db_path = os.path.join(self.db_path, db_name)
        if not os.path.exists(db_path):
            return None
        
        try:
            # 使用DashScope重排序
            dashscope_rerank = DashScopeRerank(top_n=chunk_cnt, return_documents=True)
            
            # 加载索引
            storage_context = StorageContext.from_defaults(persist_dir=db_path)
            index = load_index_from_storage(storage_context)
            
            # 创建检索器
            retriever_engine = index.as_retriever(similarity_top_k=20)
            
            # 获取结果
            retrieve_chunk = retriever_engine.retrieve(prompt)
            
            try:
                # 尝试使用重排序
                results = dashscope_rerank.postprocess_nodes(retrieve_chunk, query_str=prompt)
            except:
                # 重排序失败时使用原始结果
                results = retrieve_chunk[:chunk_cnt]
            
            # 格式化结果
            formatted_results = []
            for i, node in enumerate(results):
                if node.score >= similarity_threshold:
                    formatted_results.append({
                        "file_name": db_name,  # 文档名称
                        "similarity": node.score,  # 相似度分数
                        "content": node.text    # 文本内容
                    })
            
            return formatted_results
        except Exception as e:
            print(f"查询错误: {str(e)}")
            return None
    
    def list_documents(self) -> Dict:
        """列出所有文档"""
        try:
            documents = self.data.list_documents()
            return {
                "success": True,
                "documents": documents
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"获取文档列表失败: {str(e)}"
            } 