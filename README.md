# Academic Research Workflow Agent

## 1. 项目简介

Academic Research Workflow Agent 是一个面向研究生学术研究场景的论文阅读与写作辅助系统。项目基于 RAG（Retrieval-Augmented Generation，检索增强生成）框架，将文档解析、文本切分、向量检索、真实大模型调用和多类学术任务工具整合为一个统一工作流。

本项目的目标不是代替研究者完成论文写作，而是辅助完成以下研究工作：

- 快速读取和解析学术论文；
- 基于论文原文进行 RAG 问答；
- 生成单篇论文精读卡片；
- 对多篇论文进行横向比较；
- 生成文献综述框架；
- 检查学术写作段落的结构、逻辑和表达问题；
- 通过 Streamlit 前端提供可交互使用界面；
- 通过项目级评估脚本验证系统稳定性。

---

## 2. 已实现功能

当前项目已经实现以下模块：

| 模块 | 功能 | 状态 |
|---|---|---|
| 模块一 | 文档解析工具 | 已完成 |
| 模块二 | 文本切分工具 | 已完成 |
| 模块三 | Chroma 向量检索工具 | 已完成 |
| 模块四 | 基础 RAG 问答工具 | 已完成 |
| 模块五 | 单篇论文精读工具 | 已完成 |
| 模块六 | 多篇论文对比工具 | 已完成 |
| 模块七 | 文献综述框架生成工具 | 已完成 |
| 模块八 | 学术写作检查工具 | 已完成 |
| 模块九 | 统一学术研究工作流 | 已完成 |
| 模块十 | Streamlit 前端交互界面 | 已完成 |
| 模块十一 | 项目评估与验收脚本 | 已完成 |
| 模块十二 | README 与项目说明文档完善 | 当前模块 |

---

## 3. 核心工作流

项目整体流程如下：

```text
原始文档
  ↓
文档解析
  ↓
文本切分 chunk
  ↓
写入 Chroma 向量数据库
  ↓
语义检索相关片段
  ↓
调用真实 LLM API
  ↓
生成学术任务结果
```

在此基础上，系统进一步封装出五类学术任务：

```text
1. 基础 RAG 问答
2. 单篇论文精读
3. 多篇论文对比
4. 文献综述框架生成
5. 学术写作检查
```

这些任务统一由：

```text
app/tools/workflow_tools.py
```

中的 `AcademicResearchWorkflow` 进行调度。

---

## 4. 技术栈

本项目主要使用以下技术：

| 类型 | 技术 |
|---|---|
| 编程语言 | Python |
| 文档解析 | pypdf, python-docx |
| 文本切分 | 自定义 chunk 切分工具 |
| 向量数据库 | Chroma |
| Embedding | sentence-transformers / Chroma 默认 embedding |
| 大模型接口 | OpenAI-compatible API |
| 环境变量管理 | python-dotenv |
| 前端界面 | Streamlit |
| 项目评估 | 自定义 evaluate_project.py |
| 版本管理 | Git + GitHub |

---

## 5. 项目目录结构

```text
academic-research-agent/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main_test.py
│   ├── tools/
│   │   ├── document_tools.py
│   │   ├── rag_tools.py
│   │   ├── paper_tools.py
│   │   ├── compare_tools.py
│   │   ├── review_tools.py
│   │   ├── writing_tools.py
│   │   └── workflow_tools.py
│   ├── services/
│   │   ├── vector_service.py
│   │   └── llm_service.py
│   └── database/
│       └── db.py
├── data/
│   ├── raw_docs/
│   └── demo_docs/
├── storage/
│   ├── chroma/
│   └── sqlite/
├── frontend/
│   └── streamlit_app.py
├── outputs/
│   ├── reports/
│   └── cards/
├── evaluate_project.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 6. 环境配置

### 6.1 创建虚拟环境

```powershell
python -m venv .venv
```

激活虚拟环境：

```powershell
.\.venv\Scripts\activate
```

### 6.2 安装依赖

```powershell
pip install -r requirements.txt
```

若使用 Streamlit 前端，需确保 `requirements.txt` 中包含：

```text
streamlit
```

---

## 7. 大模型 API 配置

项目通过 `.env` 文件读取 LLM 配置。

在项目根目录创建：

```text
.env
```

参考 `.env.example` 填写：

```env
LLM_PROVIDER=api
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-pro
```

说明：

- `.env` 文件包含真实 API Key，不应提交到 GitHub；
- `.env.example` 只保留示例字段；
- 若暂时不调用真实模型，可将 `LLM_PROVIDER` 设置为 `mock`。

---

## 8. 文档数据放置

默认文档目录为：

```text
data/demo_docs/
```

也可以将自己的论文放入：

```text
data/raw_docs/
```

支持的文档格式包括：

```text
.txt
.md
.pdf
.docx
```

说明：

- PDF 需尽量使用非扫描版 PDF；
- 扫描版 PDF 暂不支持 OCR；
- 某些 PDF 解析时可能出现非致命 warning，例如 `startxref` 或 `MediaBox` 提示，只要文本能成功解析，一般不影响运行。

---

## 9. 命令行测试

开发阶段可以运行：

```powershell
python -m app.main_test
```

该脚本用于测试文档解析、文本切分、向量检索、RAG 问答以及部分学术任务工具。

---

## 10. 启动 Streamlit 前端

在项目根目录运行：

```powershell
streamlit run frontend/streamlit_app.py
```

正常启动后会显示：

```text
Local URL: http://localhost:8501
```

前端支持以下任务：

```text
1. 基础 RAG 问答
2. 单篇论文精读
3. 多篇论文对比
4. 文献综述框架生成
5. 学术写作检查
```

首次使用前，建议在侧边栏点击：

```text
重建向量索引
```

---

## 11. 项目评估脚本

项目提供一键评估脚本：

```powershell
python evaluate_project.py
```

该脚本会自动执行：

```text
1. 文档解析成功率检查
2. 文本切分可用性检查
3. 向量索引可用性检查
4. 检索命中率检查
5. RAG 问答可用性检查
6. 单篇精读可用性检查
7. 多篇对比可用性检查
8. 写作检查可用性检查
```

当前评估结果示例：

```text
文档解析成功率：3/3 = 100.00% | 通过
文本切分可用性：217/217 | 通过
向量索引可用性：217/217 | 通过
检索命中率：5/5 = 100.00% | 通过
RAG 问答可用性：通过
单篇精读可用性：通过
多篇对比可用性：通过
写作检查可用性：通过
总通过项：8/8 = 100.00%
项目评估结果：通过
```

注意：评估脚本会清空并重建当前 Chroma 向量索引，这是预期行为。

---

## 12. 主要功能说明

### 12.1 基础 RAG 问答

用户输入问题后，系统会从向量库中检索相关 chunk，并调用 LLM 生成回答，同时返回依据来源和不确定性说明。

示例任务：

```text
人工智能如何影响企业创新韧性？
```

---

### 12.2 单篇论文精读

系统可围绕指定论文生成结构化精读卡片，包含：

```text
1. 研究背景
2. 研究问题
3. 理论基础
4. 数据与方法
5. 核心变量
6. 主要结论
7. 创新点
8. 局限性
9. 对研究的启发
```

系统使用混合检索策略，结合向量检索、关键词检索和结构性页码偏好，提升论文结论、变量测量、方法设计等部分的定位效果。

---

### 12.3 多篇论文对比

系统支持对多篇论文进行横向比较，比较维度包括：

```text
1. 研究问题
2. 理论基础
3. 数据与方法
4. 核心变量
5. 主要结论
```

对比工具采用双路检索融合：

```text
PaperReadingTool 的混合检索
+
CompareTool 的中英文向量检索
```

以兼顾中文论文和英文论文的检索效果。

---

### 12.4 文献综述框架生成

系统可以基于多篇论文的结构化摘要生成文献综述框架，包括：

```text
1. 综述主题界定
2. 已有研究的主要脉络
3. 可划分的文献类别
4. 已有研究的共同结论
5. 已有研究的差异与分歧
6. 现有研究不足
7. 后续研究方向
8. 可用于论文写作的文献综述章节框架
```

该模块的来源是前置模块生成的结构化摘要，因此来源显示为：

```text
来源类型=summary | 摘要维度=research_question
```

---

### 12.5 学术写作检查

系统可对用户输入的论文段落进行检查，重点包括：

```text
1. 结构完整性
2. 逻辑连贯性
3. 学术表达规范性
4. 论据与文献支撑
5. 表达清晰度
6. 重复与冗余
7. 理论机制合理性
8. 变量表述一致性
```

输出包括：

```text
1. 总体判断
2. 主要问题清单
3. 逐项修改建议
4. 可保留的优点
5. 需要补充文献或证据的位置
6. 局部示范修改
```

---

## 13. 统一工作流入口

核心统一入口位于：

```text
app/tools/workflow_tools.py
```

支持任务类型：

```python
task_type = "rag_answer"
task_type = "single_paper_reading"
task_type = "paper_comparison"
task_type = "literature_review"
task_type = "writing_check"
```

示例调用：

```python
workflow.run_task(
    task_type="rag_answer",
    question="人工智能如何影响企业创新韧性？",
    top_k=3,
)
```

---

## 14. 当前局限

当前版本仍存在以下局限：

1. 暂不支持扫描版 PDF 的 OCR；
2. 文献综述框架质量依赖输入论文数量和主题相关度；
3. 多篇论文对比目前主要面向结构化摘要，不等同于系统性文献综述；
4. 对英文论文和中文论文的检索策略仍有进一步优化空间；
5. 当前前端为基础 Streamlit 版本，尚未实现用户登录、任务历史记录和结果导出；
6. 当前写作检查只针对用户输入文本，不会自动验证参考文献真实性。

---

## 15. 后续扩展方向

后续可继续扩展：

```text
1. 支持上传文件并自动写入 raw_docs；
2. 支持导出 Word / Markdown / Excel 报告；
3. 支持任务历史记录与 SQLite 存储；
4. 支持更细粒度的论文结构识别；
5. 支持批量生成文献阅读卡片；
6. 支持引用链追踪与原文页码回溯；
7. 支持 FastAPI 后端接口；
8. 支持部署到服务器或云平台；
9. 支持更多 LLM Provider；
10. 支持更严格的评估指标和自动化测试。
```

---

## 16. Git 提交记录参考

项目主要阶段性提交包括：

```text
Implement document parsing tools
Implement text chunking tools
Implement Chroma vector service
Implement basic RAG answer service
Expand single paper reading card
Implement paper comparison tool
Improve comparison retrieval quality
Implement literature review framework tool
Implement academic writing check tool
Implement unified academic workflow tool
Implement Streamlit workflow interface
Add project evaluation script
```

---

## 17. 使用注意事项

- 不要提交 `.env`；
- 不要提交真实 API Key；
- 不要提交大型论文原文数据；
- 不要提交 `storage/chroma/` 中的向量索引文件；
- 使用真实 API 时会产生调用费用；
- 长文献综述和完整精读会消耗更多 API 调用次数；
- 评估脚本会重建 Chroma 索引，运行前需确认当前索引可以被覆盖。

---

## 18. License

本项目当前用于学习、研究和课程项目展示。正式开源前可进一步补充许可证说明。