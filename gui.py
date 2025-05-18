import gradio as gr
import requests
from typing import List, Dict
import random
def get_doc_page():
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
    # def refresh_list():
    #     return random.sample(['1','2','3'],2)
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
            
    def gr_refresh_list():
        return gr.update(choices=refresh_list())

    with gr.Blocks(title="文档管理系统") as doc_page:
        gr.Markdown("# 文档管理系统")
        
        # 文档管理部分
        gr.Markdown("## 文档管理")
        with gr.Group():
            file_input = gr.File(label="上传文档")
            with gr.Row():
                upload_btn = gr.Button("上传")
                process_btn = gr.Button("处理")
            upload_output = gr.Textbox(label="操作结果")
        
        with gr.Group():
            doc_dropdown = gr.Dropdown(
                info="选择要处理的文档",
                choices=[],
                label="文档列表",
                multiselect=False,
                allow_custom_value=True
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
        
        
        
        # 绑定事件
        upload_btn.click(upload_file, inputs=[file_input], outputs=[upload_output])
        process_btn.click(process_file, inputs=[doc_dropdown], outputs=[upload_output])
        refresh_btn.click(gr_refresh_list,outputs=[doc_dropdown])
        delete_btn.click(delete_file, inputs=[doc_dropdown], outputs=[delete_output])
        search_btn.click(search_docs, inputs=[search_input], outputs=[search_output])
        
        # 初始加载文档列表 (传入 request)
        doc_page.load(refresh_list, inputs=None, outputs=[doc_dropdown])
    
    return doc_page 