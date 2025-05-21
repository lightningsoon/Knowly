# 知识库管理软件——知了

![管理界面](/images/admin.jpg)

## 简介

**知了** 是一款面向个人的现代化知识库管理软件，致力于为用户提供高效、便捷、智能的知识存储与管理体验。无论是文本、表格、图片、文档，还是结构化、半结构化、非结构化数据，都能轻松管理，助力每个人成为高效的知识工作者。

## 核心特性

- **单文件高效存储**  
  采用创新的数据存储方式，所有知识内容都可存储于单一文件中，无需复杂的分库分表，极大简化部署与迁移，查询与筛选性能优越。

- **全平台支持**  
  支持移动端（iOS/Android）与桌面端（Windows/Mac/Linux）同步使用，随时随地记录与查找知识，真正实现"人人可用"。

- **多数据结构兼容**  
  兼容多种数据类型与结构，包括文本、Markdown、表格、图片、PDF、音频等，满足不同场景下的知识管理需求。

- **智能数据迭代**  
  内置自动归纳、去重、分类等智能功能，支持版本管理，帮助用户持续优化和完善知识库内容。

- **安全与隐私**  
  本地加密存储，支持云端同步，保障数据安全与隐私。

## 适用场景

- 个人信息管理
- 学习笔记与资料分享
- 项目文档与研究资料管理
- 代码片段与技术文档管理
- 为大模型（如 LLM）提供个性化数据，提升智能问答与辅助决策能力

## 使用方式

1. 打开知了的网页或小程序
2. 创建或导入你的知识库文件
3. 随时随地添加、检索、管理你的知识内容

## 贡献与反馈

欢迎提出建议和反馈，也欢迎加入开发和维护！


## 安装说明
### 安装前准备

去[阿里云百炼](https://bailian.console.aliyun.com/?spm=5176.29597918.J_SEsSjsNv72yRuRFS2VknO.2.72ac7b08diFZe7&tab=model#/efm/model_experience_center/text)获取api-key，需要用到embedding模型接口。

1. 克隆项目并安装依赖：
```bash
git clone [项目地址]
cd [项目目录]
pip install -r requirements.txt
```

2. 启动服务：
```bash
export DASHSCOPE_API_KEY="填你的阿里云百炼api-key"
python main.py
```

3. 访问系统：
   - 打开浏览器访问 http://localhost:8000
   - 部署在服务器上 http://<你的ip地址>:8000

## 使用说明

1. 文档上传
   - 点击"文档上传"标签页
   - 选择要上传的docx或txt文件
   - 点击"上传并处理"按钮
   - 等待处理完成

2. 文档管理
   - 在"已上传文档"下拉列表中选择要删除的文档
   - 点击"删除选中文档"按钮进行删除

3. 文档检索
   - 点击"文档检索"标签页
   - 在输入框中输入检索问题
   - 调整相似度阈值和召回数量（可选）
   - 点击"检索"按钮获取结果

## 注意事项

1. 确保上传的文档格式正确（docx或txt）
2. 文档处理可能需要一定时间，请耐心等待
3. 建议定期清理不需要的文档以节省存储空间
### 接口文档
访问 `http://localhost:8000/docs` 查看Swagger文档


# API 文档
所有API接口均以 `/api/doc` 为基础路径。

## API端点

| 方法   | 路径        | 功能                |
|--------|-------------|---------------------|
| POST   | /upload     | 文件上传            |
| GET    | /documents  | 获取文档列表        |
| DELETE | /documents  | 删除指定文档        |
| POST   | /query      | 执行文档检索        |
| GET    | /health     | 服务健康检查        |

## 测试脚本
```bash
# 执行自动化测试
chmod +x test_api.sh
./test_api.sh
```



## 1. 上传文档

- **URL**: `/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **参数**:
    - `file`: 上传的文件 (类型: `UploadFile`, 支持 `.txt`, `.docx`)
- **成功响应 (200)**:
  ```json
  {
    "success": true,
    "message": "文档 '文件名' 上传成功"
  }
  ```
- **失败响应 (400/500)**:
  ```json
  {
    "detail": "错误信息"
  }
  ```

## 2. 处理文档（切片和向量化）

- **URL**: `/process/{file_name}`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **路径参数**:
    - `file_name`: 要处理的文件名 (string)
- **请求体参数**:
    - `chunk_size`: 分块长度 (integer, 默认: 50)
    - `separator`: 分割符号 (string, 默认: "\n")
- **成功响应 (200)**:
  ```json
  {
    "success": true,
    "message": "文档 '文件名' 处理成功"
  }
  ```
- **失败响应 (400/404/500)**:
  ```json
  {
    "detail": "错误信息"
  }
  ```

## 3. 删除文档

- **URL**: `/delete/{file_name}`
- **Method**: `DELETE`
- **路径参数**:
    - `file_name`: 要删除的文件名 (string)
- **成功响应 (200)**:
  ```json
  {
    "success": true,
    "message": "文档 '文件名' 删除成功"
  }
  ```
- **失败响应 (400/404/500)**:
  ```json
  {
    "detail": "错误信息"
  }
  ```

## 4. 搜索所有文档

- **URL**: `/search`
- **Method**: `GET`
- **查询参数**:
    - `query`: 搜索查询 (string, 必选)
    - `similarity_threshold`: 相似度阈值 (float, 默认: 0.2)
    - `top_k`: 返回结果数量 (integer, 默认: 5)
- **成功响应 (200)**:
  ```json
  {
    "success": true,
    "results": [
      {
        "file_name": "文档名",
        "similarity": 0.85,
        "content": "相关内容片段..."
      }
      // ...更多结果
    ]
  }
  ```
- **失败响应 (400/500)**:
  ```json
  {
    "detail": "错误信息"
  }
  ```

## 5. 列出所有文档

- **URL**: `/list`
- **Method**: `GET`
- **成功响应 (200)**:
  ```json
  {
    "success": true,
    "documents": ["文件名1.txt", "文件名2.docx"]
  }
  ```
- **失败响应 (500)**:
  ```json
  {
    "detail": "错误信息"
  }
  ```

## 6. 定向单文件检索

- **URL**: `/query`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **请求体参数**:
    - `prompt`: 检索内容 (string, 必选)
    - `db_name`: 文件名 (string, 必选, 不带后缀，作为知识库名)
    - `similarity_threshold`: 相似度阈值 (float, 默认: 0.2)
    - `chunk_cnt`: 返回结果数量 (integer, 默认: 5)
- **成功响应 (200)**:
  ```json
  {
    "success": true,
    "results": [
      {
        "file_name": "文档名",
        "similarity": 0.85,
        "content": "相关内容片段..."
      }
      // ...更多结果
    ]
  }
  ```
- **失败响应 (400/500)**:
  ```json
  {
    "detail": "错误信息"
  }
  ```



## 项目结构
```
.
├── api.py         # FastAPI接口
├── gui.py         # Gradio界面
├── control.py     # 业务逻辑控制
├── data.py        # 数据层操作
├── main.py        # 服务入口
└── test_api.sh    # API测试脚本
```

## 常见问题

Q: 文件上传失败提示文件已存在？
A: 系统禁止重复上传同名文件，请先删除旧版本

Q: 服务无法正常关闭？
A: 使用Ctrl+C关闭后等待5秒强制终止

Q: 文档列表不更新？
A: 点击刷新按钮或切换分页触发更新

---

# Knowledge Base Management Software — Knowly

## Introduction

**Knowly** is a modern knowledge base management software designed for individuals. It aims to provide an efficient, convenient, and intelligent experience for storing and managing all types of knowledge. Whether it's text, tables, images, documents, or structured, semi-structured, or unstructured data, Knowly helps you manage everything with ease, empowering everyone to become a highly efficient knowledge worker.

## Key Features

- **Efficient Single-file Storage**  
  Uses an innovative data storage approach, allowing all knowledge content to be stored in a single file. No need for complex database setups, greatly simplifying deployment and migration, with excellent search and filtering performance.

- **Cross-platform Support**  
  Supports both mobile (iOS/Android) and desktop (Windows/Mac/Linux), enabling you to record and access your knowledge anytime, anywhere.

- **Multi-format Compatibility**  
  Compatible with various data types and formats, including text, Markdown, tables, images, PDFs, audio, and more, meeting the needs of different knowledge management scenarios.

- **Smart Data Iteration**  
  Built-in features for automatic summarization, deduplication, and classification, with version management to help you continuously optimize and refine your knowledge base.

- **Security & Privacy**  
  Local encrypted storage with optional cloud sync to ensure your data is safe and private.

## Use Cases

- Personal information management
- Study notes and material sharing
- Project documentation and research management
- Code snippets and technical documentation management
- Providing personalized data for large language models (LLMs) to enhance intelligent Q&A and decision-making

## Getting Started

1. Open the Knowly web app or mini program
2. Create or import your knowledge base file
3. Add, search, and manage your knowledge anytime, anywhere

## Contribution & Feedback

We welcome suggestions and feedback, and invite you to join us in development and maintenance!