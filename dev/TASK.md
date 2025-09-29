### **命令行财务数据分析应用 - 开发任务清单 (cutword 修订版)**

#### **阶段一：项目初始化与基础框架搭建 (Phase 1: Project Initialization & Basic Framework)** ✅ **已完成**

本阶段的目标是建立项目的基础结构，包括目录、虚拟环境、核心依赖以及命令行程序的入口。

  * **1.1. 创建项目目录结构** ✅

      * 创建一个主文件夹，例如 `fin_analyzer_cli`。
      * 在主文件夹内，创建主程序文件 `je_analyzer.py`。
      * 创建一个 `test-data` 目录用于存放测试用的 Excel 文件。

  * **1.2. 初始化 `uv` 虚拟环境** ✅

      * 在项目根目录下，执行以下命令创建一个名为 `.venv` 的虚拟环境。
        ```bash
        uv venv
        ```
      * 激活虚拟环境。
          * **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
          * **macOS/Linux:** `source .venv/bin/activate`

  * **1.3. 安装核心依赖** ✅

      * 使用 `uv add` 安装项目所需的核心库。我们将从 `pandas` 和 `openpyxl` (用于支持 Excel) 开始。推荐使用 `click` 作为命令行解析工具，因为它比 `argparse` 更现代、更灵活。
        ```bash
        uv add pandas openpyxl click python-calamine
        ```

  * **1.4. 创建程序主入口和 CLI 框架** ✅

      * 编辑 `je_analyzer.py` 文件。
      * 使用 `click` 库设置基本的命令行结构，包括主命令组和两个子命令 `get` 和 `overview`。
      * 定义全局选项：`<input_file>`, `--account-code`, `--exact-match`, `--start-date`, `--end-date`, `--account-book`, `--query`。此时，函数体可以暂时为空或只打印接收到的参数，以验证框架是否正常工作。

#### **阶段二：核心数据处理逻辑 (Phase 2: Core Data Processing Logic)**

本阶段专注于实现程序的核心——数据的加载、清洗和筛选。

  * **2.1. 实现数据加载与预处理模块**

      * 创建一个函数 `load_data(file_path)`。
      * 该函数使用 Pandas 读取 Excel 文件（.xlsx），推荐使用 `calamine` 引擎处理大型文件。
      * **关键步骤**：
          1. 读取数据后，立即对 DataFrame 的所有列名进行清洗，去除首尾可能存在的空格。例如：`df.columns = df.columns.str.strip()`。
          2. 将所有数据先作为字符串类型处理
          3. 进行以下类型转换：
              * `日期` 列：转换为 Pandas datetime 类型
              * `借方金额` 列：转换为 float 类型
              * `贷方金额` 列：转换为 float 类型
              * `借正贷负` 列：转换为 float 类型
              * 其他列保持为字符串类型
      * 移除之前的错误类型转换代码。

  * **2.2. 实现基础筛选功能**

      * 创建一个函数 `filter_data(df, account_code, start_date, end_date, account_book, exact_match=False)`。
      * 该函数接收一个 DataFrame 和全局选项作为参数。
      * 根据 `科目编码`、`日期` (\>= start\_date) 和 `日期` (\<= end\_date) 对 DataFrame 进行筛选，并返回筛选后的结果。
      * **科目编码筛选**: 如果 `exact_match` 为 True，则要求科目编码完全相等；否则使用前缀匹配（startswith）。
      * 处理 `account_book` 参数：
          * 如果值为 `"all"`，则包含所有账套
          * 如果包含逗号，则按多个账套筛选
          * 否则按单个账套名称筛选

  * **2.3. 实现高级筛选 (`--query`) 功能**

      * 在主逻辑中，检查用户是否传入了 `--query` 参数。
      * 如果传入，则在**基础筛选后**的 DataFrame 上调用 `df.query(query_string)` 方法，应用高级筛选逻辑。
      * **注意**：要提醒用户，在 query 字符串中如果列名包含空格（如 `' 借方金额 '`），需要用反引号 `` ` `` 包裹。

#### **阶段三：实现 `get` 命令 (Phase 3: Implementation of the `get` Command)**

本阶段将完整实现 `get` 子命令的所有功能。

  * **3.1. 实现 `get` 子命令的专属选项**

      * 使用 `click` 为 `get` 命令添加 `--top`, `--top-type`, `--columns` 选项，并设置好默认值。
      * 确保全局选项 `--account-book` 在 `get` 命令中可用。

  * **3.2. 实现 Top N 功能 (`--top`)**

      * 在 `get` 命令的处理逻辑中，检查 `--top` 参数。
      * 如果提供了此参数：
          * 根据 `--top-type` 的值 (`debit`, `credit`, `both`) 对数据进行排序。
          * 对于 `both` 类型，可以创建一个临时列，其值为 `借方金额` 和 `贷方金额` 的最大值或绝对值的最大值，然后按该列排序。
          * 使用 `.head(N)` 选取前 N 条记录。

  * **3.3. 实现列输出控制功能 (`--columns`)**

      * 根据 `--columns` 参数的值进行处理：
          * `all`: 不做任何列选择，返回所有列。
          * `"col1,col2,..."`: 解析逗号分隔的字符串，并使用 `df[['col1', 'col2']]` 的形式选择指定的列。
          * `default`: 定义一个包含默认列名的列表。

  * **3.4. 实现 `default` 模式的特殊逻辑**

      * 当 `--columns` 为 `default` 时，在选择了预设的列之后，检查 `客户名称`, `供应商名称`, `项目名称` 这三列。
      * 对于其中任意一列，如果其所有值都为空 (`.isnull().all()`)，则从最终要输出的 DataFrame 中移除该列。

  * **3.5. 格式化 `get` 命令的输出**

      * 将最终处理好的 DataFrame 转换为制表符分隔（Tab-separated）的字符串。
      * 使用 `df.to_csv(sys.stdout, sep='\t', index=False)` 是一个高效的实现方式。
      * 确保标准输出 (`stdout`) 能够正确处理文本编码（如 UTF-8）。

#### **阶段四：实现 `overview` 命令 (Phase 4: Implementation of the `overview` Command)**

本阶段专注于 `overview` 命令，生成统计报告。

  * **4.1. 实现 `overview` 子命令的基础框架**

      * 在 `overview` 的处理函数中，调用前序阶段完成的数据加载和筛选逻辑，得到最终用于分析的数据集。

  * **4.2. 计算并格式化统计数据**

      * **基本统计**: 获取 `len(df)` 得到总行数。
      * **金额分布**:
          * 分别针对 `借方金额` 和 `贷方金额` 列计算 `.mean()` (平均值) 和 `.mode()` (众数)。
          * 计算众数的出现频率。
          * 将这些结果存入一个字典或自定义类中，以便后续格式化输出。

  * **4.3. 安装 `cutword` 并实现摘要词频分析**

      * 添加中文分词库 `cutword`。
        ```bash
        uv add cutword
        ```
      * 将 `摘要` 列的所有文本合并成一个长字符串。
      * 使用 `cutword` 库进行分词。
      * 统计词频，并筛选出频率最高的 N 个词（例如 Top 10）。（注意：可能需要一个停用词列表来排除无意义的词）。

  * **4.4. 格式化 `overview` 命令的输出**

      * 设计一个清晰、人类可读的报告格式。
      * 逐项打印计算出的所有统计指标，配上清晰的标题和描述。

#### **阶段五：健壮性、测试与文档 (Phase 5: Robustness, Testing & Documentation)**

本阶段是收尾工作，确保程序稳定、易用且有据可查。

  * **5.1. 完善错误处理机制**

      * 使用 `try...except` 块来捕获常见错误：
          * `FileNotFoundError`: 输入文件不存在。
          * `ValueError`: 日期格式不正确。
          * `KeyError`: 在 `--columns` 或 `--query` 中使用了不存在的列名。
          * Pandas 查询语法错误。
      * 为用户提供友好、明确的错误提示信息。

  * **5.2. 优化命令行帮助信息**

      * 利用 `click` 的 `help` 参数，为每个命令和选项添加清晰的说明文字，解释其作用和用法。

  * **5.3. 编写代码文档 (Docstrings)**

      * 为项目中的主要函数（如 `load_data`, `filter_data` 等）编写标准的 Python docstrings，解释函数的用途、参数和返回值。

  * **5.4. 创建项目 `README.md`**

      * 编写一个详细的 `README.md` 文件，包括：
          * 项目简介。
          * 安装步骤（如何创建 `uv` 环境、安装依赖）。
          * 详细的使用说明和所有命令、选项的解释。
          * 复制设计文档中的使用示例，并确保它们可以正确运行。

  * **5.5. 进行端到端测试**

      * 准备几个不同内容的测试数据 Excel 文件。
      * 复制测试数据文件到 `test-data` 文件夹。
      * 使用 `calamine` 引擎读取大型 Excel 文件进行测试。
      * 手动执行所有命令组合，特别是边缘情况：
          * 查询结果为空。
          * Top N 的 N 值大于总行数。
          * 包含特殊字符的摘要。
          * 日期范围不包含任何数据。
          * 单个账套、多个账套、所有账套的筛选功能。
      * 验证输出格式是否符合设计文档要求。