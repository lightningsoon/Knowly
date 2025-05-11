import os
import shutil
from typing import List, Dict, Optional
import requests
from data import DocumentData

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
            
            # 检查是否已存在同名文档
            if self.data.document_exists(file_name):
                return {
                    "success": False,
                    "message": f"警告：已存在同名文件 '{os.path.splitext(file_name)[0]}'，请先删除或使用其他名称"
                }
            
            # 保存文档
            if not self.data.save_document(file_path, file_name):
                return {
                    "success": False,
                    "message": f"保存文档失败"
                }
            
            # 调用向量化服务
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f)}
                response = requests.post("http://localhost:8008/upload_data", files=files)
                
                if response.status_code != 200:
                    # 删除已保存的文件
                    self.data.delete_document(file_name)
                    return {
                        "success": False,
                        "message": f"向量化失败: {response.text}"
                    }
            
            return {
                "success": True,
                "message": f"文档 '{os.path.splitext(file_name)[0]}' 处理成功"
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
        """搜索文档"""
        try:
            response = requests.get(
                "http://localhost:8008/query",
                params={
                    "prompt": query,
                    "db_name": "all",
                    "similarity_threshold": similarity_threshold,
                    "chunk_cnt": top_k
                }
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "results": response.json()
                }
            return {
                "success": False,
                "message": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"检索失败: {str(e)}"
            }
    
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