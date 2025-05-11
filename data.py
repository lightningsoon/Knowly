import os
import shutil
from typing import List, Dict, Optional
import json

class DocumentData:
    def __init__(self):
        self.db_path = "VectorStore"
        self.temp_path = "temp_files"
        self.file_path = "File"
        
        # 确保必要的目录存在
        os.makedirs(self.db_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
        os.makedirs(self.file_path, exist_ok=True)
    
    def save_document(self, file_path: str, file_name: str) -> bool:
        """保存文档"""
        try:
            target_path = os.path.join(self.file_path, file_name)
            shutil.copy2(file_path, target_path)
            return True
        except Exception:
            return False
    
    def get_document_path(self, file_name: str) -> Optional[str]:
        """获取文档路径"""
        file_path = os.path.join(self.file_path, file_name)
        if os.path.exists(file_path):
            return file_path
        return None
    
    def delete_document(self, file_name: str) -> bool:
        """删除文档"""
        try:
            # 删除文件
            file_path = os.path.join(self.file_path, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 删除向量存储
            db_path = os.path.join(self.db_path, os.path.splitext(file_name)[0])
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            
            return True
        except Exception:
            return False
    
    def list_documents(self) -> List[str]:
        """列出所有文档"""
        try:
            return [f for f in os.listdir(self.file_path) if os.path.isfile(os.path.join(self.file_path, f))]
        except Exception:
            return []
    
    def document_exists(self, file_name: str) -> bool:
        """检查文档是否存在"""
        file_path = os.path.join(self.file_path, file_name)
        return os.path.exists(file_path)
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            for file_name in os.listdir(self.temp_path):
                file_path = os.path.join(self.temp_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception:
            pass 