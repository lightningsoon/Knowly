# 知识库管理软件——知了

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

## 快速开始

1. 打开知了的网页或小程序
2. 创建或导入你的知识库文件
3. 随时随地添加、检索、管理你的知识内容

## 贡献与反馈

欢迎提出建议和反馈，也欢迎加入开发和维护！

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

# 文档智能处理系统

这是一个基于FastAPI和Gradio构建的文档智能处理系统，支持文档上传、向量化和智能检索功能。

## 功能特点

1. 文档上传
   - 支持上传docx和txt格式的文档
   - 自动进行文本提取和向量化
   - 文件名作为唯一标识，重复上传会提示覆盖

2. 文档管理
   - 查看已上传文档列表
   - 支持删除文档及其向量索引

3. 智能检索
   - 支持自然语言问题检索
   - 可调节相似度阈值和召回数量
   - 显示检索结果及其相似度分数

## 安装说明

1. 克隆项目并安装依赖：
```bash
git clone [项目地址]
cd [项目目录]
pip install -r requirements.txt
```

2. 启动服务：
```bash
python main.py
```

3. 访问系统：
   - 打开浏览器访问 http://localhost:8000
   - 文档管理界面：http://localhost:8000/documents

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

## 技术栈

- FastAPI：后端框架
- Gradio：Web界面
- LangChain：文档处理
- FAISS：向量存储
- Sentence-Transformers：文本向量化

## 注意事项

1. 确保上传的文档格式正确（docx或txt）
2. 文档处理可能需要一定时间，请耐心等待
3. 建议定期清理不需要的文档以节省存储空间
