import gradio as gr
import requests
from typing import List, Dict
import random
import os
import json
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
        
    def process_file(selected_doc, chunk_size, separator):
        try:
            if not selected_doc:
                return "请先选择要处理的文档"
            response = requests.post(f"http://localhost:8008/api/doc/process/{selected_doc}", json={"chunk_size": chunk_size, "separator": separator})
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
    
    def search_docs(query, db_name, similarity_threshold, chunk_cnt):
        if not query:
            return gr.update(visible=False), gr.update(value="请输入检索内容", visible=True)
        if not db_name:
            return gr.update(visible=False), gr.update(value="请选择要检索的文档", visible=True)
        db_name = os.path.splitext(db_name)[0]
        try:
            response = requests.post(
                "http://localhost:8008/api/doc/query",
                json={
                    "prompt": query,
                    "db_name": db_name,
                    "similarity_threshold": similarity_threshold,
                    "chunk_cnt": chunk_cnt
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    results = data["results"]
                    if not results:
                        return gr.update(visible=False), gr.update(value="未找到相关内容", visible=True)
                    return gr.update(value=json.dumps(results, ensure_ascii=False, indent=2), visible=True), gr.update(visible=False)
                return gr.update(visible=False), gr.update(value=data["message"], visible=True)
            return gr.update(visible=False), gr.update(value=f"检索失败: {response.text}", visible=True)
        except Exception as e:
            return gr.update(visible=False), gr.update(value=f"检索失败: {str(e)}", visible=True)
            


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
            with gr.Row():
                chunk_size_slider = gr.Slider(label="处理参数：分块长度", minimum=200, maximum=1000, step=1, value=500)
                separator_input = gr.Textbox(label="处理参数：分隔符号", value="\\n\\n\\n", max_lines=1)
            process_btn = gr.Button("处理")
            delete_btn = gr.Button("删除")
            process_output = gr.Textbox(label="操作结果")
        
        # 文档检索部分
        gr.Markdown("## 第三步 文档检索")
        with gr.Group():
            search_input = gr.Textbox(label="检索内容")
            with gr.Row():
                similarity_input = gr.Slider(label="相似度阈值", minimum=0, maximum=1, step=0.01, value=0.4)
                topk_input = gr.Number(label="返回条数", value=5, step=1, minimum=1)
            search_btn = gr.Button("检索")
            search_output_json = gr.Code(label="检索结果", language="json", lines=10, visible=False)
            search_output_text = gr.Textbox(label="检索结果", lines=10, visible=True)
        
        
        # 绑定事件
        upload_btn.click(upload_file, inputs=[file_input], outputs=[upload_output])
        refresh_btn.click(fn=lambda :gr.update(choices=refresh_list()),outputs=[doc_dropdown])
        process_btn.click(process_file, inputs=[doc_dropdown, chunk_size_slider, separator_input], outputs=[process_output])
        delete_btn.click(delete_file, inputs=[doc_dropdown], outputs=[process_output]).then(fn=lambda :gr.update(choices=refresh_list()),outputs=[doc_dropdown])
        search_btn.click(search_docs, inputs=[search_input, doc_dropdown, similarity_input, topk_input], outputs=[search_output_json, search_output_text])
        
        doc_page.load(fn=lambda :gr.update(choices=refresh_list()),inputs=[],outputs=[doc_dropdown])
    return doc_page 