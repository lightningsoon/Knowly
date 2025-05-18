from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import gradio as gr
from api import app as api_app
from gui import get_doc_page
import signal
import os
import sys
import uvicorn # 明确导入uvicorn

# 修改信号处理，强制退出
def force_exit(signum, frame):
    print("强制退出服务")
    os._exit(0)  # 使用os._exit直接退出进程，不等待

# 注册信号处理器
signal.signal(signal.SIGINT, force_exit)  # CTRL+C
signal.signal(signal.SIGTERM, force_exit) # kill命令

app = FastAPI()

# 挂载API
app.mount("/api/doc", api_app)

# 挂载GUI
doc_page = get_doc_page()
app = gr.mount_gradio_app(app, doc_page, path="/")

# 将Uvicorn启动移到这里，确保Gradio组件初始化完成
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)