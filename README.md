# Academic Research Workflow Agent

## 1. 项目简介

Academic Research Workflow Agent 是一个面向研究生学术研究场景的论文阅读与写作辅助系统。项目基于 RAG（Retrieval-Augmented Generation，检索增强生成）框架，将文档解析、文本切分、向量检索、真实大模型调用、学术任务工具、Streamlit 前端交互和 Markdown / Word 结果导出整合为一个统一工作流。

本项目的定位不是替代研究者完成论文写作，而是辅助研究者完成论文阅读、文献整理、论文对比、综述框架生成、学术写作检查和结果归档等重复性、结构化工作。

当前版本已经形成完整的 v1.0 闭环：

```text
文档上传
→ 自动索引
→ RAG 问答
→ 单篇论文精读
→ 批量论文精读
→ 多篇论文对比
→ 文献综述框架生成
→ 学术写作检查
→ Markdown / Word 导出
→ Streamlit 前端下载
→ evaluate_project.py 自动验收
```

---

## 2. 当前版本状态

```text
项目名称：Academic Research Workflow Agent
当前版本：v1.0
项目状态：已完成
最终模块：模块二十二
最终验收：evaluate_project.py 9/9 通过
前端入口：Streamlit
主要用途：学术论文阅读、文献比较、综述准备与写作检查
```

最近一次项目评估结果：

```text
文档解析成功率：4/4 = 100.00% | 通过
文本切分可用性：453/453 | 通过
向量索引可用性：453/453 | 通过
检索命中率：5/5 = 100.00% | 通过
RAG 问答可用性：通过
单篇精读可用性：通过
多篇对比可用性：通过
写作检查可用性：通过
结果导出可用性：通过
总通过项：9/9 = 100.00%
项目评估结果：通过
```

---

## 3. 核心功能概览

本项目目前支持以下功能：

1. 读取和解析 `.txt`、`.md`、`.pdf`、`.docx` 文档；
2. 支持前端上传文档并自动保存至 `data/raw_docs/`；
3. 支持上传后自动重建 Chroma 向量索引；
4. 将长文档切分为可检索的文本 chunk；
5. 将文本片段写入 Chroma 向量数据库；
6. 基于向量检索实现 RAG 问答；
7. 生成单篇论文精读卡片；
8. 支持 quick / full 两种单篇精读模式；
9. 支持英文论文结构性检索优化；
10. 支持 PDF 表格型 chunk 与变量表检索增强；
11. 支持批量论文精读；
12. 支持批量论文精读前端多选与导出；
13. 支持多篇论文横向对比；
14. 支持基于多篇论文生成文献综述框架；
15. 支持学术写作检查；
16. 支持统一 workflow 调度；
17. 支持 Streamlit 前端交互；
18. 支持 Markdown 导出；
19. 支持 Word 导出；
20. 支持 Word 导出基础格式美化；
21. 支持 Streamlit 前端下载导出文件；
22. 支持项目级一键验收。

---

## 4. 已完成模块

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
| 模块十六 | 项目阶段性最终验收与文档同步 | 已完成 |
| 模块十七 | 前端文件上传与自动索引 | 已完成 |
| 模块十八 | 单篇论文精读检索质量优化 | 已完成 |
| 模块十九 | PDF 表格与变量表抽取质量优化 | 已完成 |
| 模块二十 A | 后端批量论文精读工具 | 已完成 |
| 模块二十 B | Streamlit 前端批量论文精读入口 | 已完成 |
| 模块二十一 | 批量精读导出结构优化 | 已完成 |
| 模块二十二 | 最终验收、README 更新与项目总结 | 已完成 |

---

## 5. 核心工作流

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

前端使用流程如下：

```text
启动 Streamlit
  ↓
上传 PDF / DOCX / TXT / MD 文档
  ↓
自动保存到 data/raw_docs/
  ↓
自动重建 Chroma 索引
  ↓
选择任务类型
  ↓
生成学术任务结果
  ↓
导出并下载 Markdown / Word
```

---

## 6. 技术栈

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

## 7. 项目目录结构

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
│   │   ├── batch_paper_tools.py
│   │   ├── compare_tools.py
│   │   ├── review_tools.py
│   │   ├── writing_tools.py
│   │   ├── workflow_tools.py
│   │   └── export_tools.py
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

说明：

- `app/tools/`：存放各类学术任务工具；
- `app/services/`：存放向量数据库服务和大模型服务；
- `frontend/`：存放 Streamlit 前端；
- `data/raw_docs/`：存放用户上传或手动放入的论文文档；
- `storage/chroma/`：存放 Chroma 向量索引；
- `outputs/reports/`：存放导出的 Markdown / Word 结果文件；
- `evaluate_project.py`：项目级一键验收脚本。

---

## 8. 环境配置

### 8.1 创建虚拟环境

```powershell
python -m venv .venv
```

### 8.2 激活虚拟环境

Windows PowerShell：

```powershell
.\.venv\Scripts\activate
```

### 8.3 安装依赖

```powershell
pip install -r requirements.txt
```

---

## 9. 大模型 API 配置

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
- 当前项目支持 OpenAI-compatible API 风格的大模型服务。

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
3. 批量论文精读
4. 多篇论文对比
5. 文献综述框架生成
6. 学术写作检查
```

首次使用可在侧边栏上传文档，并勾选：

```text
上传后自动重建索引
```

系统会自动将文件保存到 `data/raw_docs/`，并基于上传目录重建向量索引。

---

## 11. 文档上传与自动索引

前端侧边栏提供：

```text
上传文档并自动索引
```

支持上传：

```text
.txt
.md
.pdf
.docx
```

基本流程：

```text
选择上传文件
  ↓
保存到 data/raw_docs/
  ↓
自动重建索引
  ↓
刷新当前文档目录
  ↓
执行 RAG、精读、对比、综述等任务
```

注意：

1. PDF 尽量使用非扫描版 PDF；
2. 当前版本暂不支持 OCR；
3. 某些 PDF 解析时可能出现 `MediaBox`、`wrong pointing object` 等 warning；
4. 只要文档解析成功率和 chunk 构建正常，这类 warning 通常不影响系统运行。

---

## 12. 主要功能说明

### 12.1 基础 RAG 问答

用户输入问题后，系统会从向量数据库中检索相关 chunk，并调用 LLM 生成回答，同时返回依据来源和不确定性说明。

输出内容包括：

```text
1. 回答
2. 依据来源
3. 不确定之处
```

---

### 12.2 单篇论文精读

系统可围绕指定论文生成结构化精读卡片。

支持两种模式：

```text
quick：研究背景、研究问题、主要结论
full：完整 9 个维度
```

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

单篇精读工具使用混合检索策略：

```text
1. 向量检索；
2. 关键词检索；
3. 页码结构偏好；
4. 中英文检索词增强；
5. 表格型 chunk 检索；
6. 检索结果去重合并。
```

---

### 12.3 批量论文精读

系统支持一次选择多篇论文，批量生成精读卡片。

支持：

```text
quick：每篇论文生成 3 个维度
full：每篇论文生成 9 个维度
```

批量精读结果包括：

```text
1. 任务概况；
2. 每篇论文处理状态；
3. 每篇论文精读维度；
4. 问题；
5. 回答；
6. 依据来源；
7. 不确定之处。
```

批量精读结果支持 Markdown 和 Word 导出，导出文件会按论文与维度分层显示。

---

### 12.4 多篇论文对比

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

---

### 12.5 文献综述框架生成

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

---

### 12.6 学术写作检查

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

---

## 13. 结果导出与下载

系统支持将各类 workflow 结果导出为本地文件。

支持导出：

```text
1. 基础 RAG 问答结果
2. 单篇论文精读结果
3. 批量论文精读结果
4. 多篇论文对比结果
5. 文献综述框架结果
6. 学术写作检查结果
```

支持格式：

```text
Markdown：.md
Word：.docx
```

导出文件默认保存至：

```text
outputs/reports/
```

前端提供：

```text
生成 Markdown 文件
生成 Word 文件
下载 Markdown
下载 Word
```

---

## 14. Word 导出格式美化

Word 导出支持基础格式美化：

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

批量论文精读当前由：

```text
app/tools/batch_paper_tools.py
```

提供后端能力，并由：

```text
frontend/streamlit_app.py
```

接入前端。

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

注意：

```text
evaluate_project.py 会清空并重建当前 Chroma 向量索引。
```

这是预期行为，用于保证评估过程基于统一的文档输入和索引状态。

---

## 17. 当前局限

当前版本仍存在以下局限：

1. 暂不支持扫描版 PDF 的 OCR；
2. 暂不支持真正的 PDF 表格结构化抽取，只做表格型 chunk 检索增强；
3. 文献综述框架质量依赖输入论文数量、论文质量和主题相关度；
4. 多篇论文对比不等同于完整系统性文献综述；
5. 写作检查只依据用户输入文本，不会自动验证参考文献真实性；
6. 当前没有任务历史记录功能；
7. 当前没有用户登录、权限管理和在线部署功能；
8. Word 导出为基础格式美化，不是完整排版系统；
9. 当前评估脚本主要验证功能可用性，不等同于严格的软件工程单元测试。

---

## 18. 后续扩展方向

后续可作为 v1.1 / v2.0 扩展的方向包括：

```text
1. OCR 与扫描版 PDF 解析；
2. PDF 表格结构化抽取；
3. 任务历史记录与 SQLite 存储；
4. 批量文献综述材料整理；
5. Excel 导出；
6. 更复杂的 Word 报告模板；
7. 引用链追踪与原文页码回溯；
8. FastAPI 后端接口；
9. 服务器部署或云端部署；
10. 多模型 Provider 支持；
11. 更严格的测试体系和 CI/CD；
12. 多项目文献库管理。
```

这些方向不再纳入当前 v1.0 收口范围。

---

## 19. 使用注意事项

1. 不要提交 `.env`；
2. 不要提交真实 API Key；
3. 不要提交大型论文原文数据；
4. 不要提交 `storage/chroma/` 中的向量索引文件；
5. 不要提交 `outputs/reports/` 中的临时导出文件；
6. 使用真实 API 时可能产生调用费用；
7. full 精读、文献综述和多篇论文对比会消耗更多 API 调用次数；
8. 运行评估脚本前需确认当前索引可以被覆盖；
9. GitHub push 失败时，多数情况下是网络连接问题，本地 commit 不会丢失。

---

## 20. License

本项目当前用于学习、研究和课程项目展示。正式开源前可进一步补充许可证说明。
