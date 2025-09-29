# 安装指南

## 使用 uvx 直接运行

推荐使用 `uvx` 直接运行，无需安装：

```bash
# 从 GitHub 运行
uvx run git+https://github.com/PyBalance/je-analyzer --help

# 或者从本地路径运行
uvx run /path/to/je-analyzer --help

# 实际使用示例
uvx run git+https://github.com/PyBalance/je-analyzer -a 1002 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx overview
```

## 使用 uv 安装

### 从 GitHub 安装

```bash
# 安装最新版本
uv pip install git+https://github.com/PyBalance/je-analyzer

# 或者安装特定版本/分支
uv pip install git+https://github.com/PyBalance/je-analyzer@main
```

### 从本地源码安装

```bash
# 克隆仓库
git clone https://github.com/PyBalance/je-analyzer.git
cd je-analyzer

# 安装到当前环境
uv pip install -e .

# 或者使用 uvx 直接运行本地代码
uvx run . --help
```

## 验证安装

```bash
# 检查是否安装成功
je-analyzer --help

# 或者
uvx run je-analyzer --help
```

## 使用示例

安装后可以直接使用 `je-analyzer` 命令：

```bash
# 生成概览报告
je-analyzer -a 1002 -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx overview

# 获取特定条件的记录
je-analyzer -a 6601 -q "借方金额 != 0" -s 2024-01-01 -e 2024-12-31 -b "示例账套" data.xlsx get --top 10
```