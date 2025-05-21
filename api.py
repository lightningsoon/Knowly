from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from control import DocumentController
import os
import signal
import sys

app = FastAPI()
controller = DocumentController()

def handle_exit(sig, frame):
    print('收到退出信号，正在优雅关闭...')
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> JSONResponse:
    """上传文档
    
    参数:
        file: 上传的文件
        
    返回:
        JSONResponse: 包含上传结果的响应
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.txt', '.docx')):
            raise HTTPException(status_code=400, detail="只支持 .txt 和 .docx 格式的文件")
        
        # 保存上传的文件
        base_name = os.path.basename(file.filename)
        temp_file_path = os.path.join(controller.temp_path, base_name)
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 保存文档
        success, msg = controller.data.save_document(temp_file_path, base_name)
        if not success:
            raise HTTPException(status_code=400, detail=msg)
        
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return JSONResponse(content={
            "success": True,
            "message": f"文档 '{os.path.basename(file.filename)}' 上传成功"
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/process/{file_name}")
async def process_document(file_name: str) -> JSONResponse:
    """处理文档（切片和向量化）
    
    参数:
        file_name: 要处理的文件名
        
    返回:
        JSONResponse: 包含处理结果的响应
    """
    try:
        # 检查文件是否存在
        file_path = controller.data.get_document_path(file_name)
        if not file_path:
            raise HTTPException(status_code=404, detail=f"文件 '{file_name}' 不存在")
        
        # 处理文档
        result = controller.process_document(file_path)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.delete("/delete/{file_name}")
async def delete_document(file_name: str) -> JSONResponse:
    """删除文档
    
    参数:
        file_name: 要删除的文件名
        
    返回:
        JSONResponse: 包含删除结果的响应
    """
    try:
        # 检查文件是否存在
        if not controller.data.document_exists(file_name):
            raise HTTPException(status_code=404, detail=f"文件 '{file_name}' 不存在")
        
        result = controller.delete_document(file_name)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@app.get("/search")
async def search_documents(
    query: str,
    similarity_threshold: float = 0.2,
    top_k: int = 5
) -> JSONResponse:
    """搜索文档
    
    参数:
        query: 搜索查询
        similarity_threshold: 相似度阈值 (默认: 0.2)
        top_k: 返回结果数量 (默认: 5)
        
    返回:
        JSONResponse: 包含搜索结果的响应
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="搜索内容不能为空")
        
        result = controller.search_documents(query, similarity_threshold, top_k)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

@app.get("/list")
async def list_documents() -> JSONResponse:
    """列出所有文档
    
    返回:
        JSONResponse: 包含文档列表的响应
    """
    try:
        result = controller.list_documents()
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")

@app.post("/query")
async def query(
    prompt: str = Body(...),
    db_name: str = Body(...),
    similarity_threshold: float = Body(0.2),
    chunk_cnt: int = Body(5)
) -> JSONResponse:
    """定向单文件检索接口
    参数:
        prompt: 检索内容
        db_name: 文件名（知识库名）
        similarity_threshold: 相似度阈值
        chunk_cnt: 返回结果数量
    返回:
        JSONResponse: 检索结果
    """
    try:
        result = controller.search_documents_with_db(prompt, db_name, similarity_threshold, chunk_cnt)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return JSONResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008) 