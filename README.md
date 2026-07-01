# Academic Research Workflow Agent

## 1. 项目简介

Academic Research Workflow Agent 是一个面向研究生学术研究场景的论文阅读与写作辅助系统。项目基于 RAG（Retrieval-Augmented Generation，检索增强生成）框架，将文档解析、文本切分、向量检索、真实大模型调用、学术任务工具、前端交互和结果导出整合为一个统一工作流。

本项目的目标不是代替研究者完成论文写作，而是辅助研究者完成论文阅读、文献整理、论文对比、综述框架生成和学术写作检查等重复性、结构化工作。

当前项目已经形成一个完整的 v1.0 原型版本，具备从“文档输入”到“结果生成”再到“Word / Markdown 导出下载”的基本闭环。

---

## 2. 项目功能概览

本项目目前支持以下功能：

1. 读取和解析 `.txt`、`.md`、`.pdf`、`.docx` 文档；
2. 将长文档切分为可检索的文本片段；
3. 将文本片段写入 Chroma 向量数据库；
4. 基于向量检索实现 RAG 问答；
5. 生成单篇论文精读卡片；
6. 对多篇论文进行横向比较；
7. 基于多篇论文生成文献综述框架；
8. 对论文段落进行学术写作检查；
9. 通过统一 workflow 调度不同学术任务；
10. 通过 Streamlit 前端进行交互式使用；
11. 将结果导出为 Markdown 文件；
12. 将结果导出为 Word 文件；
13. 在 Streamlit 前端中下载导出文件；
14. 对 Word 导出结果进行基础格式美化；
15. 通过项目评估脚本对主要功能进行一键验收。

---

## 3. 已完成模块

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
| 模块十二 | README 与项目说明文档完善 | 已完成 |
| 模块十三 | 结果导出工具 | 已完成 |
| 模块十四 | Streamlit 前端导出与下载 | 已完成 |
| 模块十五 | Word 导出格式美化 | 已完成 |
| 模块十六 | 项目最终验收与文档同步 | 已完成 |

---

## 4. 核心工作流

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
  ↓
导出 Markdown / Word
  ↓
前端下载结果文件
```

在此基础上，系统封装出五类主要学术任务：

```text
1. 基础 RAG 问答
2. 单篇论文精读
3. 多篇论文对比
4. 文献综述框架生成
5. 学术写作检查
```

所有任务统一由：

```text
app/tools/workflow_tools.py
```

中的 `AcademicResearchWorkflow` 进行调度。

---

## 5. 技术栈

| 类型 | 技术 |
|---|---|
| 编程语言 | Python |
| 文档解析 | pypdf, python-docx |
| 文本切分 | 自定义 chunk 切分工具 |
| 向量数据库 | Chroma |
| Embedding | Chroma 默认 embedding / sentence-transformers |
| 大模型接口 | OpenAI-compatible API |
| 环境变量管理 | python-dotenv |
| 前端界面 | Streamlit |
| 结果导出 | Markdown, python-docx |
| 项目评估 | 自定义 evaluate_project.py |
| 版本管理 | Git + GitHub |

---

## 6. 项目目录结构

```text
academic-research-agent/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main_test.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── document_tools.py
│   │   ├── rag_tools.py
│   │   ├── paper_tools.py
│   │   ├── compare_tools.py
│   │   ├── review_tools.py
│   │   ├── writing_tools.py
│   │   ├── workflow_tools.py
│   │   └── export_tools.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vector_service.py
│   │   └── llm_service.py
│   └── database/
│       ├── __init__.py
│       └── db.py
├── data/
│   ├── raw_docs/
│   │   └── .gitkeep
│   └── demo_docs/
│       └── .gitkeep
├── storage/
│   ├── chroma/
│   │   └── .gitkeep
│   └── sqlite/
│       └── .gitkeep
├── frontend/
│   └── streamlit_app.py
├── outputs/
│   ├── reports/
│   │   └── .gitkeep
│   └── cards/
│       └── .gitkeep
├── evaluate_project.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

说明：

- `app/tools/`：存放各类学术任务工具；
- `app/services/`：存放向量数据库服务和大模型服务；
- `frontend/`：存放 Streamlit 前端；
- `data/demo_docs/`：存放示例文档；
- `data/raw_docs/`：存放用户自己的论文或文档；
- `storage/chroma/`：存放 Chroma 向量索引；
- `outputs/reports/`：存放导出的 Markdown / Word 结果文件；
- `evaluate_project.py`：项目级一键验收脚本。

---

## 7. 环境配置

### 7.1 创建虚拟环境

在项目根目录执行：

```powershell
python -m venv .venv
```

### 7.2 激活虚拟环境

Windows PowerShell：

```powershell
.\.venv\Scripts\activate
```

### 7.3 安装依赖

```powershell
pip install -r requirements.txt
```

若使用 Streamlit 前端，需确保 `requirements.txt` 中包含：

```text
streamlit
```

若使用 Word 导出功能，需确保包含：

```text
python-docx
```

---

## 8. 大模型 API 配置

项目通过 `.env` 文件读取 LLM 配置。

在项目根目录创建：

```text
.env
```

可参考 `.env.example` 填写：

```env
LLM_PROVIDER=api
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-pro
```

说明：

- `.env` 文件包含真实 API Key，不应提交到 GitHub；
- `.env.example` 只保留示例字段；
- 若暂时不调用真实模型，可以将 `LLM_PROVIDER` 设置为 `mock`；
- 项目当前支持 OpenAI-compatible API 风格的大模型服务。

---

## 9. 文档数据放置

默认文档目录为：

```text
data/demo_docs/
```

也可以将自己的论文或研究资料放入：

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

注意事项：

1. PDF 尽量使用非扫描版 PDF；
2. 当前版本暂不支持 OCR；
3. 某些 PDF 解析时可能出现非致命 warning，例如 `startxref` 或 `MediaBox` 提示；
4. 只要文本可以成功提取，这些 warning 通常不影响系统运行。

---

## 10. 命令行测试

开发阶段可以运行：

```powershell
python -m app.main_test
```

该脚本用于测试文档解析、文本切分、向量检索、RAG 问答、单篇精读、多篇对比、文献综述、写作检查和结果导出等功能。

其中结果导出测试会生成 Markdown 和 Word 文件，默认保存到：

```text
outputs/reports/
```

---

## 11. 启动 Streamlit 前端

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

该操作会读取指定文档目录中的文件，切分文本并写入 Chroma 向量数据库。

---

## 12. 主要功能说明

### 12.1 基础 RAG 问答

用户输入问题后，系统会从向量数据库中检索相关 chunk，并调用 LLM 生成回答，同时返回依据来源和不确定性说明。

示例问题：

```text
人工智能如何影响企业创新韧性？
```

输出内容包括：

```text
1. 回答
2. 依据来源
3. 不确定之处
```

---

### 12.2 单篇论文精读

系统可围绕指定论文生成结构化精读卡片。

完整精读包含九个维度：

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

单篇精读工具使用混合检索策略，包括：

```text
1. 向量检索；
2. 关键词检索；
3. 页码结构偏好；
4. 检索结果去重合并。
```

该设计用于提高论文结论、变量测量、研究方法和局限性等结构化内容的定位效果。

---

### 12.3 多篇论文对比

系统支持对多篇论文进行横向比较。

默认比较维度包括：

```text
1. 研究问题
2. 数据与方法
3. 主要结论
4. 理论基础
5. 核心变量
```

多篇论文对比工具采用双路检索融合：

```text
PaperReadingTool 的混合检索
+
CompareTool 的中英文向量检索
```

该设计用于兼顾中文论文和英文论文的检索效果。

---

### 12.4 文献综述框架生成

系统可以基于多篇论文的结构化摘要生成文献综述框架。

输出内容包括：

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

该模块的来源主要是前置模块生成的结构化摘要，因此来源显示可能包括：

```text
来源类型=summary
摘要维度=research_question
```

---

### 12.5 学术写作检查

系统可对用户输入的论文段落进行检查。

支持的检查重点包括：

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

输出内容包括：

```text
1. 总体判断
2. 主要问题清单
3. 逐项修改建议
4. 可保留的优点
5. 需要补充文献或证据的位置
6. 局部示范修改
7. 不确定之处
```

---

## 13. 结果导出与下载

系统支持将各类 workflow 结果导出为本地文件。

支持导出的任务结果包括：

```text
1. 基础 RAG 问答结果
2. 单篇论文精读结果
3. 多篇论文对比结果
4. 文献综述框架结果
5. 学术写作检查结果
```

当前支持两种导出格式：

```text
Markdown：.md
Word：.docx
```

导出文件默认保存至：

```text
outputs/reports/
```

在 Streamlit 前端中，用户可以在任务结果生成后点击：

```text
生成 Markdown 文件
生成 Word 文件
下载 Markdown
下载 Word
```

---

## 14. Word 导出格式美化

Word 导出功能已经支持基础格式美化，包括：

```text
1. 标题层级识别；
2. Markdown 加粗文本识别；
3. 项目符号列表；
4. 编号列表；
5. 关键小节标题识别；
6. 正文字体、字号和段落间距设置；
7. 文档页边距设置；
8. 导出时间显示。
```

例如，模型输出中的：

```text
**作用机制**
```

在 Word 文件中会转换为加粗文本，而不是保留 Markdown 星号。

同时，类似下面的内容：

```text
1. 提高信息处理效率
2. 优化资源配置
3. 增强风险识别能力
```

会被识别为 Word 编号列表。

---

## 15. 统一工作流入口

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

统一 workflow 的作用是将前端、评估脚本和后续 API 接口都连接到同一个任务调度入口，避免不同模块之间重复调用逻辑。

---

## 16. 项目评估脚本

项目提供一键评估脚本：

```powershell
python evaluate_project.py
```

该脚本会自动执行以下检查：

```text
1. 文档解析成功率检查
2. 文本切分可用性检查
3. 向量索引可用性检查
4. 检索命中率检查
5. RAG 问答可用性检查
6. 单篇精读可用性检查
7. 多篇对比可用性检查
8. 写作检查可用性检查
9. 结果导出可用性检查
```

当前项目验收目标为：

```text
总通过项：9/9 = 100.00%
项目评估结果：通过
```

注意：

```text
evaluate_project.py 会清空并重建当前 Chroma 向量索引。
```

这是预期行为，用于保证评估过程基于统一的文档输入和索引状态。

---

## 17. 项目当前状态

当前项目已经完成 v1.0 阶段性闭环。

已具备：

```text
1. 后端文档处理能力；
2. 向量检索与 RAG 问答能力；
3. 多类学术研究任务工具；
4. 统一 workflow 调度能力；
5. Streamlit 前端交互能力；
6. Markdown / Word 结果导出能力；
7. 前端下载能力；
8. Word 基础格式美化能力；
9. 项目级自动验收能力；
10. GitHub 远程版本归档。
```

可以将当前版本定义为：

```text
Academic Research Workflow Agent v1.0
```

---

## 18. 当前局限

当前版本仍存在以下局限：

1. 暂不支持扫描版 PDF 的 OCR；
2. 前端暂未提供文件上传功能，需要用户手动将文档放入 `data/demo_docs/` 或 `data/raw_docs/`；
3. 文献综述框架质量依赖输入论文数量、论文质量和主题相关度；
4. 多篇论文对比目前主要面向结构化摘要，不等同于完整系统性文献综述；
5. 写作检查只依据用户输入文本，不会自动验证参考文献真实性；
6. 当前没有任务历史记录功能；
7. 当前没有用户登录、权限管理和在线部署功能；
8. Word 导出为基础格式美化，不是完整排版系统；
9. 当前评估脚本主要验证功能可用性，不等同于严格的软件工程单元测试。

---

## 19. 后续扩展方向

后续可继续扩展以下方向：

```text
1. 前端文件上传与自动索引；
2. 任务历史记录与 SQLite 存储；
3. 批量论文阅读卡片生成；
4. 批量文献综述材料整理；
5. 结果导出为 Excel；
6. 更复杂的 Word 报告模板；
7. 引用链追踪与原文页码回溯；
8. 更细粒度的论文结构识别；
9. FastAPI 后端接口；
10. 服务器部署或云端部署；
11. 多模型 Provider 支持；
12. 更严格的测试体系和 CI/CD；
13. 用户级配置管理；
14. 多项目文献库管理。
```

优先级较高的下一步是：

```text
前端文件上传与自动索引
```

该功能可以将当前使用流程从：

```text
手动复制文件到 data/raw_docs
↓
手动重建索引
↓
再执行任务
```

优化为：

```text
前端上传 PDF / DOCX
↓
自动保存文件
↓
自动解析并写入向量库
↓
立即执行 RAG、精读、对比和综述任务
```

---

## 20. Git 提交记录参考

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
Update project README documentation
Implement result export tool
Integrate export downloads into Streamlit interface
Improve Word export formatting
Update final evaluation and documentation
```

---

## 21. 使用注意事项

使用本项目时需要注意：

1. 不要提交 `.env`；
2. 不要提交真实 API Key；
3. 不要提交大型论文原文数据；
4. 不要提交 `storage/chroma/` 中的向量索引文件；
5. 不要提交 `outputs/reports/` 中的临时导出文件；
6. 使用真实 API 时可能产生调用费用；
7. 长文档精读、文献综述和多篇论文对比会消耗更多 API 调用次数；
8. 运行评估脚本前需确认当前索引可以被覆盖；
9. GitHub push 失败时，多数情况下是网络连接问题，本地 commit 不会丢失。

---

## 22. License

本项目当前用于学习、研究和课程项目展示。正式开源前可进一步补充许可证说明。