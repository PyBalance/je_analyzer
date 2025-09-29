# 财务数据分析命令行工具 (Journal Entries Analyzer)

一个基于 Python 和 Pandas 的命令行工具，用于快速分析和筛选财务日记账数据。

## 功能特点

- **数据概览**: 生成统计报告，包括总记录数、借方/贷方金额分布、摘要词频分析
- **数据查询**: 灵活筛选和导出原始数据
- **Top N 查询**: 按金额排序获取前 N 条记录
- **高级筛选**: 支持复杂的 Pandas 查询语句
- **多账套支持**: 可分析单个、多个或全部账套
- **自定义输出**: 灵活控制输出列

## 安装和运行

### 推荐：使用 uvx 直接运行

无需安装，直接运行：

```bash
# 从 GitHub 运行
uvx run git+https://github.com/PyBalance/je-analyzer --help

# 从本地源码运行
uvx run /path/to/je-analyzer --help

# 实际使用示例
uvx run git+https://github.com/PyBalance/je-analyzer -a 1002 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx overview
```

### 传统安装方式

```bash
# 使用 uv 安装
uv pip install git+https://github.com/yourusername/je-analyzer

# 或者从源码安装
git clone https://github.com/yourusername/je-analyzer.git
cd je-analyzer
uv pip install -e .
```

安装后可直接使用：

```bash
je-analyzer -a 1002 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx overview
```

## 使用方法

### 命令格式

```bash
uv run python je_analyzer.py [OPTIONS] INPUT_FILE COMMAND [ARGS]...
```

**注意**: 所有选项 (`-a`, `-s`, `-e`, `-b`, `-q`) 必须放在输入文件和子命令之前。

### 全局选项

| 选项 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `-a, --account-code` | ✅ | 会计科目编码 | `-a "1002"` |
| `--exact-match` | ❌ | 精确匹配科目编码（默认前缀匹配） | `--exact-match` |
| `-s, --start-date` | ✅ | 开始日期 (YYYY-MM-DD) | `-s "2024-01-01"` |
| `-e, --end-date` | ✅ | 结束日期 (YYYY-MM-DD) | `-e "2024-12-31"` |
| `-b, --account-book` | ✅ | 账套名称 | `-b "示例账套"` |
| `-q, --query` | ❌ | Pandas 查询字符串 | `-q "借方金额 != 0"` |

### 账套名称格式

- 单个账套: `-b "示例账套"`
- 多个账套: `-b "示例账套A,示例账套B"`
- 全部账套: `-b "all"`

## 子命令

### 1. overview - 生成概览报告

生成包含统计信息的数据分析报告。

**语法**:
```bash
uv run python je_analyzer.py -a <CODE> -s <START> -e <END> -b <BOOK> <input_file> overview
```

**示例**:

#### 基本概览
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a 1002 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx overview
```

**输出示例**:
```
============================================================
财务数据分析概览报告
============================================================

📊 基本统计
   总记录数: 6,067

💰 借方金额分布
   平均值: 143,707.93
   众数: 0.00
   众数频率: 5,279

💳 贷方金额分布
   平均值: 141,242.14
   众数: 0.00
   众数频率: 788

📝 摘要词频分析 (Top 10)
    1. 执行: 2,962
    2. 工程合同: 2,648
    3. 01: 2,603
    4. 手续费: 1,788
    5. 2024: 1,268
    6. 全款: 1,229
    7. 23: 871
    8. 内部: 856
    9. 2023: 789
   10. 02: 663

============================================================
```

#### 精确匹配科目编码
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a 1002 --exact-match -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx overview
```

#### 分析全部账套
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a 1002 -s 2024-01-01 -e 2024-12-31 -b "all" data.xlsx overview
```

### 2. get - 获取原始数据

获取并输出筛选后的原始数据行。

**语法**:
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a <CODE> -s <START> -e <END> -b <BOOK> <input_file> get [OPTIONS]
```

**get 选项**:

| 选项 | 说明 | 示例 |
|------|------|------|
| `--top N` | 返回 Top N 条记录 | `--top 5` |
| `--top-type TYPE` | 排序类型: `debit`, `credit`, `both` | `--top-type debit` |
| `--columns CONFIG` | 输出列配置 | `--columns "日期,摘要,借方金额"` |

**列配置选项**:
- `all`: 输出所有列
- `default`: 输出预设列（自动移除空列）
- 自定义列名: 用逗号分隔，如 `"日期,摘要,借方金额"`

**示例**:

#### 获取 Top 5 条记录
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a 6601 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx get --top 5
```

#### 按借方金额排序
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a 6601 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx get --top 3 --top-type debit
```

#### 自定义输出列
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a 6601 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx get --top 3 --columns "日期,摘要,借方金额,贷方金额"
```

#### 使用高级查询
```bash
uvx run git+https://github.com/PyBalance/je-analyzer -a 1002 -q "借方金额 != 0" -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx get --top 5
```

## 查询语法

### 基本查询

```bash
# 借方金额不等于0的记录
-q "借方金额 != 0"

# 贷方金额不等于0的记录
-q "贷方金额 != 0"

# 借方金额大于0的记录
-q "借方金额 > 0"

# 贷方金额等于0的记录
-q "贷方金额 == 0"

# 金额在 10 万到 50 万之间的记录
-q "借方金额 >= 100000 and 借方金额 <= 500000"

# 金额大于 100 万的记录
-q "借方金额 > 1000000"
```

### 文本搜索

```bash
# 摘要包含"手续费"的记录
-q "摘要.str.contains('手续费')"

# 摘要以"调整"开头的记录
-q "摘要.str.startswith('调整')"

# 摘要以"结转"结尾的记录
-q "摘要.str.endswith('结转')"
```

### 复合查询

```bash
# 金额大于 100 万且摘要包含"银行"的记录
-q "借方金额 > 1000000 and 摘要.str.contains('银行')"

# 金额大于 50 万或贷方金额大于 50 万的记录
-q "借方金额 > 500000 or 贷方金额 > 500000"

# 借方金额不等于0且贷方金额等于0的记录
-q "借方金额 != 0 and 贷方金额 == 0"

# 借方金额大于0或贷方金额大于0的记录
-q "借方金额 > 0 or 贷方金额 > 0"

# 借方金额不等于0且摘要包含"手续费"的记录
-q "借方金额 != 0 and 摘要.str.contains('手续费')"
```

### 实际应用场景

```bash
# 找出有实际发生额的记录（借方或贷方不为0）
-q "借方金额 != 0 or 贷方金额 != 0"

# 找出只有借方金额的记录
-q "借方金额 != 0 and 贷方金额 == 0"

# 找出只有贷方金额的记录
-q "借方金额 == 0 and 贷方金额 != 0"

# 找出金额在特定范围的记录
-q "借方金额 >= 1000 and 借方金额 <= 10000"
```

**注意**: 当查询字符串中包含空格的列名时，需要使用反引号包裹，如 `借方金额`。

## 输出格式

- **get 命令**: 使用制表符 (\t) 分隔的表格格式，便于复制到 Excel 或其他程序
- **overview 命令**: 人类可读的格式化报告

## 技术要求

- Python 3.x
- uv (包管理工具)
- pandas
- calamine (Excel 读取引擎)
- click (命令行解析)

## 常见问题

### 1. 命令格式错误

**错误**: `Missing option '-a' / '--account-code'`

**解决**: 确保所有选项放在输入文件和子命令之前：

```bash
# 错误格式
uvx run git+https://github.com/PyBalance/je-analyzer data.xlsx overview -a "1002"

# 正确格式
uvx run git+https://github.com/PyBalance/je-analyzer -a "1002" data.xlsx overview
```

### 2. 账套名称不存在

**错误**: `警告：账套 'xxx' 不存在于数据中`

**解决**: 检查可用的账套名称，确保名称完全匹配。

### 3. 查询语法错误

**错误**: `查询语法错误`

**解决**: 检查 Pandas 查询语法，特别是包含空格的列名需要使用反引号。

## 项目结构

```
je_analyzer/
├── src/
│   └── je_analyzer/
│       ├── __init__.py   # 包初始化文件
│       ├── main.py      # 主程序文件
│       └── __main__.py   # 模块入口点
├── dev/
│   └── DESIGN.md          # 设计文档
├── test-data/
│   └── sample_data.xlsx  # 测试数据文件
├── pyproject.toml        # 项目配置文件
├── LICENSE               # 许可证文件
├── README.md             # 文档
└── INSTALL.md            # 安装指南
```

## 许可证

[请添加许可证信息]