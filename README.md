# Academic Research Agent

## 项目简介

本项目是一个面向研究生论文阅读与写作场景的学术研究工作流辅助 Agent。第一版目标是实现论文文档解析、文本切分、向量检索、RAG 问答和引用来源返回。

## 第一版功能

- PDF / Word / TXT / Markdown 文档解析
- 文本 chunk 切分
- Chroma 向量库索引
- 基于论文原文的 RAG 问答
- 回答结果返回引用来源

## 项目结构

```text
app/
data/
frontend/
outputs/
storage/

## 当前进度

- [x] 创建项目目录结构
- [x] 创建 Python 虚拟环境
- [x] 安装基础依赖
- [x] 初始化本地 Git
- [x] 创建 GitHub 远程仓库
- [x] 配置 `.env.example`
- [x] 配置 `.gitignore`
- [x] 准备本地测试文档目录
- [ ] 实现文档解析工具
- [ ] 实现文本 chunk 切分工具
- [ ] 实现 Chroma 向量索引
- [ ] 实现基础 RAG 问答
- [ ] 实现引用来源返回