import gradio as gr
import requests
from typing import List, Dict

def get_doc_page():
    with gr.Blocks(title="文档管理系统") as doc_page:
        gr.Markdown("# 文档管理系统")
        
        # 文档管理部分
        gr.Markdown("## 文档管理")
        with gr.Group():
            file_input = gr.File(label="上传文档")
            upload_btn = gr.Button("上传")
            upload_output = gr.Textbox(label="上传结果")
        
        with gr.Group():
            doc_list = gr.Dataframe(
                headers=["文件名"],
                datatype=["str"],
                label="文档列表"
            )
            refresh_btn = gr.Button("刷新列表")
            delete_btn = gr.Button("删除选中文档")
            delete_output = gr.Textbox(label="删除结果")
        
        # 文档检索部分
        gr.Markdown("## 文档检索")
        with gr.Group():
            search_input = gr.Textbox(label="检索内容")
            search_btn = gr.Button("检索")
            search_output = gr.Textbox(label="检索结果", lines=10)
        
        def upload_file(file):
            if file is None:
                return "请选择要上传的文件"
            
            try:
                with open(file.name, "rb") as f:
                    files = {"file": (file.name, f)}
                    response = requests.post("http://localhost:8008/api/doc/upload", files=files)
                    if response.status_code == 200:
                        return response.json()["message"]
                    return f"上传失败: {response.text}"
            except Exception as e:
                return f"上传失败: {str(e)}"
        
        def refresh_list():
            try:
                response = requests.get("http://localhost:8008/api/doc/list")
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        return [[doc] for doc in data["documents"]]
                    return []
                return []
            except Exception:
                return []
        
        def delete_file(evt: gr.SelectData):
            try:
                file_name = evt.data[0]
                response = requests.delete(f"http://localhost:8008/api/doc/delete/{file_name}")
                if response.status_code == 200:
                    return response.json()["message"]
                return f"删除失败: {response.text}"
            except Exception as e:
                return f"删除失败: {str(e)}"
        
        def search_docs(query):
            if not query:
                return "请输入检索内容"
            
            try:
                response = requests.get(
                    "http://localhost:8008/api/doc/search",
                    params={"query": query}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        results = data["results"]
                        if not results:
                            return "未找到相关内容"
                        
                        output = []
                        for result in results:
                            output.append(f"文档: {result['file_name']}")
                            output.append(f"相似度: {result['similarity']:.2f}")
                            output.append(f"内容: {result['content']}")
                            output.append("---")
                        return "\n".join(output)
                    return data["message"]
                return f"检索失败: {response.text}"
            except Exception as e:
                return f"检索失败: {str(e)}"
        
        # 绑定事件
        upload_btn.click(upload_file, inputs=[file_input], outputs=[upload_output])
        refresh_btn.click(refresh_list, outputs=[doc_list])
        doc_list.select(delete_file, outputs=[delete_output])
        search_btn.click(search_docs, inputs=[search_input], outputs=[search_output])
        
        # 初始加载文档列表
        doc_page.load(refresh_list, outputs=[doc_list])
    
    return doc_page 