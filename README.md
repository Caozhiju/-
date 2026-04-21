# 国际中文教育论文助手

## 项目简介
基于 LangChain 和 LangGraph 构建的国际中文教育专业论文智能助手，支持论文写作、润色、审稿，并能学习用户写作风格生成个性化论文。

## 功能特性

### 三大核心功能
1. **论文写作** - 智能生成国际中文教育领域论文
2. **论文润色** - 优化论文表达与学术规范性
3. **论文审稿** - 检查论文内容与结构问题

### 风格学习能力
- 支持导入用户已有的论文（PDF/文本格式）
- 分析用户写作风格（用词习惯、句式结构、论证逻辑）
- 基于用户风格生成个性化论文
- 采用向量存储实现风格特征持久化

### 长文本生成支持
- 支持万字以上论文一次性生成
- max_completion_tokens: 32768
- 智能分章节生成，避免内容安全检查失败
- 自动清洗生成内容，移除敏感词和特殊字符

## 本地运行

### 运行流程
```bash
bash scripts/local_run.sh -m flow
```

### 运行节点
```bash
bash scripts/local_run.sh -m node -n node_name
```

### 启动HTTP服务
```bash
bash scripts/http_run.sh -m http -p 5000
```

### 启动 Streamlit 聊天界面（推荐）
```bash
bash scripts/run_streamlit.sh
```
启动后，在浏览器中打开：**http://localhost:8501**

#### Streamlit 界面功能
- 🎨 **美观的聊天界面** - 类似 ChatGPT 的交互体验
- 📝 **一键切换功能** - 智能对话 / 论文写作 / 润色 / 审稿 / 风格学习
- 📤 **文件上传** - 直接上传 PDF 或 TXT 学习写作风格
- 💬 **多轮对话** - 自动记住上下文，支持持续交流
- 📊 **对话统计** - 实时显示对话轮次和状态

## 技术栈
- Python 3.12
- LangChain 1.0
- LangGraph
- Qwen 3.5 Plus (qwen-3-5-plus-260215)
- coze-coding-dev-sdk (LLM, Knowledge, Fetch)
- Streamlit (Web 界面)

## 配置说明
- `config/agent_llm_config.json` - 模型配置文件
  - model: qwen-3-5-plus-260215
  - max_completion_tokens: 32768
  - timeout: 1200s
  - temperature: 0.7

## 工具列表
- `paper_import_tool` - 导入论文文本
- `pdf_clean_import_tool` - 导入PDF并清洗内容
- `style_analyzer_tool` - 分析写作风格
- `personalized_paper_generator_tool` - 个性化论文生成
- `safe_paper_generator` - 安全论文生成（自动清洗）

## 使用说明

### 🚀 快速开始（推荐使用 Streamlit）

1. **启动聊天界面**
   ```bash
   bash scripts/run_streamlit.sh
   ```

2. **打开浏览器**
   访问：http://localhost:8501

3. **开始使用**
   - 选择功能模式（智能对话 / 论文写作 / 润色 / 审稿）
   - 在侧边栏上传论文学习风格（可选）
   - 输入你的需求，开始对话

### 📚 功能详解

#### 1. 智能对话模式
- 直接输入任何问题
- 支持多轮对话
- 记住上下文

#### 2. 论文写作模式
- 输入论文主题
- 指定字数和要求
- 自动生成万字长论文

#### 3. 风格学习（重要！）
- 上传 1-3 篇你的已发表论文（PDF/TXT）
- 系统自动分析你的写作风格
- 之后的生成会模仿你的风格

#### 4. 论文润色
- 发送论文草稿
- 系统优化表达和学术规范性

#### 5. 论文审稿
- 发送完整论文
- 系统检查内容和结构问题

### 第一次使用：导入论文学习风格

#### 方法1：使用 Streamlit 界面（推荐）
1. 启动 Streamlit：`bash scripts/run_streamlit.sh`
2. 在侧边栏点击"上传论文"
3. 选择你的 PDF 或 TXT 文件
4. 点击"学习风格"按钮
5. 系统自动分析并存储风格特征

#### 方法2：使用命令行工具
1. 准备你的PDF论文文件
2. 使用 `pdf_clean_import_tool` 导入论文
3. 系统自动分析并存储风格特征

### 生成个性化论文
1. 选择主题和要求
2. 使用 Streamlit 的"论文写作"模式
3. 系统会检索你的风格示例，生成符合你风格的论文

### 审稿与润色
1. 上传论文草稿
2. 选择审稿或润色功能
3. 获取专业的修改建议

## 注意事项
- PDF导入时会自动清洗特殊字符和敏感内容
- 生成长论文建议分章节进行，避免超时
- 风格学习需要至少导入1篇论文，建议3-5篇效果更佳
