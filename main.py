from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import gradio as gr
from api import app as api_app
from gui import get_doc_page

app = FastAPI()

# 挂载API
app.mount("/api/doc", api_app)

# 挂载GUI
doc_page = get_doc_page()
app = gr.mount_gradio_app(app, doc_page, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)