import gradio as gr
import requests
from typing import List, Dict
import random
import os
def get_doc_page():
    def upload_file(file):
            if file is None:
                return "请选择要上传的文件"
            try:
                with open(file.name, "rb") as f:
                    files = {"file": (os.path.basename(file.name), f)}
                    response = requests.post("http://localhost:8008/api/doc/upload", files=files)
                    if response.status_code == 200:
                        return response.json()["message"]
                    return f"上传失败: {response.text}"
            except Exception as e:
                return f"上传失败: {str(e)}"
        
    def process_file(selected_doc):
        try:
            if not selected_doc:
                return "请先选择要处理的文档"
            response = requests.post(f"http://localhost:8008/api/doc/process/{selected_doc}")
            if response.status_code == 200:
                return response.json()["message"]
            return f"处理失败: {response.text}"
        except Exception as e:
            return f"处理失败: {str(e)}"
    
    def refresh_list():
        try:
            response = requests.get("http://localhost:8008/api/doc/list")
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    docs = data["documents"]
                    return docs
                return []
            return []
        except requests.exceptions.ConnectionError:
            print("API服务未就绪，稍后重试...")
            return []
        except Exception as e:
            print("获取文档列表失败",e)
            return []

    def delete_file(selected_doc):
        try:
            if not selected_doc:
                return "请先选择要删除的文档"
            response = requests.delete(f"http://localhost:8008/api/doc/delete/{selected_doc}")
            if response.status_code == 200:
                return response.json()["message"]
            else:
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
            


    with gr.Blocks(title="知了——知识库管理系统") as doc_page:
        gr.Markdown("# 知了——知识库管理系统\n 此处应有一些介绍。")
        
        # 文档管理部分
        gr.Markdown("## 第一步：上传")
        with gr.Group():
            file_input = gr.File(label="上传文档")
            upload_btn = gr.Button("上传")
            upload_output = gr.Textbox(label="操作结果")
        gr.Markdown("## 第二步：加工")
        with gr.Group():
            doc_dropdown = gr.Dropdown(
                info="选择要处理的文档",
                choices=[],
                label="文档列表",
                multiselect=False,
                allow_custom_value=True,interactive=True
            )
            refresh_btn = gr.Button("刷新")
            process_btn = gr.Button("处理")
            delete_btn = gr.Button("删除")
            process_output = gr.Textbox(label="操作结果")
        
        # 文档检索部分
        gr.Markdown("## 文档检索")
        with gr.Group():
            search_input = gr.Textbox(label="检索内容")
            search_btn = gr.Button("检索")
            search_output = gr.Textbox(label="检索结果", lines=10)
        
        
        
        # 绑定事件
        upload_btn.click(upload_file, inputs=[file_input], outputs=[upload_output])
        refresh_btn.click(fn=lambda :gr.update(choices=refresh_list()),outputs=[doc_dropdown])
        process_btn.click(process_file, inputs=[doc_dropdown], outputs=[process_output])
        delete_btn.click(delete_file, inputs=[doc_dropdown], outputs=[process_output]).then(fn=lambda :gr.update(choices=refresh_list()),outputs=[doc_dropdown])
        search_btn.click(search_docs, inputs=[search_input], outputs=[search_output])
        
        doc_page.load(fn=lambda :gr.update(choices=refresh_list()),inputs=[],outputs=[doc_dropdown])
    return doc_page 