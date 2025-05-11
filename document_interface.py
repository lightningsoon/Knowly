import gradio as gr
import os
import requests
from html_string import plain_html

API_BASE_URL = "http://localhost:8008/api/doc"

def get_document_block():
    with gr.Blocks(theme=gr.themes.Base(), css=".gradio_container { background-color: #f0f0f0; }") as doc_interface:
        gr.HTML(plain_html)
        
        with gr.Tab("文档上传"):
            with gr.Row():
                with gr.Column(scale=2):
                    uploaded_file = gr.File(
                        label="上传文档",
                        file_types=[".docx", ".txt"],
                        file_count="single"
                    )
                    upload_btn = gr.Button("上传并处理", variant="primary")
                    status = gr.Textbox(label="处理状态", interactive=False)
            
            with gr.Row():
                with gr.Column(scale=2):
                    file_list = gr.Dropdown(
                        choices=[],
                        label="已上传文档",
                        interactive=True,
                        multiselect=True
                    )
                    delete_btn = gr.Button("删除选中文档", variant="stop")
        
        with gr.Tab("文档检索"):
            with gr.Row():
                with gr.Column(scale=2):
                    query = gr.Textbox(
                        label="输入检索问题",
                        placeholder="请输入您的问题...",
                        lines=3
                    )
                    with gr.Row():
                        similarity_threshold = gr.Slider(
                            minimum=0,
                            maximum=1,
                            value=0.2,
                            step=0.01,
                            label="相似度阈值"
                        )
                        top_k = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=5,
                            step=1,
                            label="召回数量"
                        )
                    search_btn = gr.Button("检索", variant="primary")
            
            with gr.Row():
                with gr.Column(scale=2):
                    results = gr.Textbox(
                        label="检索结果",
                        lines=10,
                        interactive=False
                    )
        
        def update_file_list():
            try:
                response = requests.get(f"{API_BASE_URL}/list")
                if response.status_code == 200:
                    return gr.update(choices=response.json()["documents"])
                return gr.update(choices=[])
            except Exception as e:
                return gr.update(choices=[])
        
        def handle_upload(file):
            if file is None:
                return "请选择文件"
            try:
                files = {"file": (file.name, open(file.name, "rb"))}
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                return response.json()["message"]
            except Exception as e:
                return f"处理失败: {str(e)}"
        
        def handle_delete(files):
            if not files:
                return "请选择要删除的文件"
            try:
                for file in files:
                    response = requests.delete(f"{API_BASE_URL}/delete/{file}")
                    if response.status_code != 200:
                        return response.json()["message"]
                return "删除成功"
            except Exception as e:
                return f"删除失败: {str(e)}"
        
        def handle_search(query, threshold, k):
            if not query:
                return "请输入检索问题"
            try:
                response = requests.get(
                    f"{API_BASE_URL}/search",
                    params={
                        "query": query,
                        "similarity_threshold": threshold,
                        "top_k": k
                    }
                )
                if response.status_code == 200:
                    results = response.json()["results"]
                    formatted_results = []
                    for doc in results:
                        formatted_results.append(f"\n来自文档 '{doc['document']}' 的检索结果：")
                        for result in doc["results"]:
                            formatted_results.append(f"相似度: {result['similarity']:.2f}")
                            formatted_results.append(f"内容: {result['content']}\n")
                    return "\n".join(formatted_results)
                return response.json()["message"]
            except Exception as e:
                return f"检索失败: {str(e)}"
        
        upload_btn.click(
            fn=handle_upload,
            inputs=[uploaded_file],
            outputs=[status]
        ).then(
            fn=update_file_list,
            outputs=[file_list]
        )
        
        delete_btn.click(
            fn=handle_delete,
            inputs=[file_list],
            outputs=[status]
        ).then(
            fn=update_file_list,
            outputs=[file_list]
        )
        
        search_btn.click(
            fn=handle_search,
            inputs=[query, similarity_threshold, top_k],
            outputs=[results]
        )
        
        doc_interface.load(
            fn=update_file_list,
            outputs=[file_list]
        )
    
    return doc_interface 