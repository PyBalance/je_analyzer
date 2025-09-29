#!/usr/bin/env python3
"""
命令行财务数据分析应用 - 主程序文件
Journal Entries Analyzer CLI Application
"""

import click
import sys
import os
import pandas as pd
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_data(file_path):
    """
    加载并预处理Excel数据

    Args:
        file_path (str): Excel文件路径

    Returns:
        pd.DataFrame: 处理后的数据框
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        click.echo(f"错误：文件不存在 - {file_path}", err=True)
        sys.exit(1)

    # 检查文件扩展名
    if not file_path.lower().endswith(('.xlsx', '.xls')):
        click.echo(f"错误：不支持的文件格式，请使用Excel文件 (.xlsx 或 .xls) - {file_path}", err=True)
        sys.exit(1)

    try:
        # 使用calamine引擎读取大型Excel文件，将所有数据作为字符串类型
        df = pd.read_excel(file_path, engine='calamine', dtype=str)

        # 检查数据是否为空
        if df.empty:
            click.echo(f"错误：Excel文件为空 - {file_path}", err=True)
            sys.exit(1)

        # 清理列名，去除首尾空格
        df.columns = df.columns.str.strip()

        # 检查必需列
        required_columns = ['科目编码', '日期', '账套名称']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            click.echo(f"错误：Excel文件缺少必需列 - {', '.join(missing_columns)}", err=True)
            click.echo(f"可用列：{', '.join(df.columns.tolist())}", err=True)
            sys.exit(1)

        # 进行特定的类型转换
        conversion_errors = []

        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            invalid_dates = df['日期'].isna().sum()
            if invalid_dates > 0:
                conversion_errors.append(f"日期列有 {invalid_dates:,} 个无效日期值")

        if '借方金额' in df.columns:
            df['借方金额'] = pd.to_numeric(df['借方金额'], errors='coerce')
            invalid_debits = df['借方金额'].isna().sum()
            if invalid_debits > 0:
                conversion_errors.append(f"借方金额列有 {invalid_debits:,} 个无效数值")

        if '贷方金额' in df.columns:
            df['贷方金额'] = pd.to_numeric(df['贷方金额'], errors='coerce')
            invalid_credits = df['贷方金额'].isna().sum()
            if invalid_credits > 0:
                conversion_errors.append(f"贷方金额列有 {invalid_credits:,} 个无效数值")

        if '借正贷负' in df.columns:
            df['借正贷负'] = pd.to_numeric(df['借正贷负'], errors='coerce')

        # 输出转换警告
        if conversion_errors:
            click.echo("警告：数据类型转换发现问题", err=True)
            for error in conversion_errors:
                click.echo(f"   - {error}", err=True)

        click.echo(f"成功加载文件：{file_path} ({len(df):,} 条记录)", err=True)
        return df

    except FileNotFoundError:
        click.echo(f"错误：文件未找到 - {file_path}", err=True)
        sys.exit(1)
    except PermissionError:
        click.echo(f"错误：没有权限读取文件 - {file_path}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"错误：文件格式错误 - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误：读取文件时发生未知错误 - {file_path}", err=True)
        click.echo(f"详细信息：{e}", err=True)
        sys.exit(1)


def filter_data(df, account_code, start_date, end_date, account_book, exact_match=False):
    """
    基础数据筛选

    Args:
        df (pd.DataFrame): 原始数据
        account_code (str): 科目编码
        start_date (str): 开始日期
        end_date (str): 结束日期
        account_book (str): 账套名称
        exact_match (bool): 是否使用精确匹配

    Returns:
        pd.DataFrame: 筛选后的数据
    """
    try:
        # 验证输入参数
        if not account_code or not account_code.strip():
            click.echo("错误：科目编码不能为空", err=True)
            sys.exit(1)

        if not start_date or not end_date:
            click.echo("错误：开始日期和结束日期不能为空", err=True)
            sys.exit(1)

        if not account_book or not account_book.strip():
            click.echo("错误：账套名称不能为空", err=True)
            sys.exit(1)

        # 转换日期字符串为datetime对象
        try:
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
        except ValueError as e:
            click.echo(f"错误：日期格式无效，请使用 YYYY-MM-DD 格式", err=True)
            click.echo(f"开始日期：{start_date}，结束日期：{end_date}", err=True)
            sys.exit(1)

        # 检查日期范围合理性
        if start_dt > end_dt:
            click.echo(f"错误：开始日期不能晚于结束日期", err=True)
            click.echo(f"开始日期：{start_dt.date()}，结束日期：{end_dt.date()}", err=True)
            sys.exit(1)

        # 科目编码筛选
        if '科目编码' in df.columns:
            if exact_match:
                # 精确匹配
                filtered_df = df[df['科目编码'] == str(account_code)]
            else:
                # 前缀匹配
                filtered_df = df[df['科目编码'].str.startswith(str(account_code))]
        else:
            click.echo("错误：数据中缺少'科目编码'列", err=True)
            sys.exit(1)

        # 日期范围筛选
        if '日期' in filtered_df.columns:
            date_mask = (filtered_df['日期'] >= start_dt) & (filtered_df['日期'] <= end_dt)
            filtered_df = filtered_df[date_mask]
        else:
            click.echo("错误：数据中缺少'日期'列", err=True)
            sys.exit(1)

        # 账套筛选
        if '账套名称' in filtered_df.columns:
            if account_book.lower() == 'all':
                # 包含所有账套
                pass
            elif ',' in account_book:
                # 多个账套
                account_books = [book.strip() for book in account_book.split(',')]
                # 检查账套是否存在
                existing_books = set(filtered_df['账套名称'].unique())
                invalid_books = [book for book in account_books if book not in existing_books]
                if invalid_books:
                    click.echo(f"警告：以下账套不存在于数据中：{', '.join(invalid_books)}", err=True)
                    click.echo(f"可用账套：{', '.join(sorted(existing_books))}", err=True)
                filtered_df = filtered_df[filtered_df['账套名称'].isin(account_books)]
            else:
                # 单个账套
                if account_book not in filtered_df['账套名称'].unique():
                    click.echo(f"警告：账套 '{account_book}' 不存在于数据中", err=True)
                    click.echo(f"可用账套：{', '.join(sorted(filtered_df['账套名称'].unique()))}", err=True)
                filtered_df = filtered_df[filtered_df['账套名称'] == account_book]
        else:
            click.echo("错误：数据中缺少'账套名称'列", err=True)
            sys.exit(1)

        return filtered_df

    except Exception as e:
        click.echo(f"错误：数据筛选过程中发生错误 - {e}", err=True)
        sys.exit(1)


def apply_top_n_filter(df, top_n, top_type):
    """
    应用Top N筛选，按指定条件排序并返回前N条记录

    Args:
        df (pd.DataFrame): 筛选后的数据
        top_n (int): 返回的记录数，如果为None或<=0则返回所有记录
        top_type (str): 排序依据，可选值:
            - 'debit': 按借方金额降序排序
            - 'credit': 按贷方金额降序排序
            - 'both': 按借方或贷方金额的绝对值最大值排序

    Returns:
        pd.DataFrame: 排序后的前N条记录，或原始数据框（如果top_n无效）

    注意:
        如果指定的排序列不存在，会尝试使用其他可用的金额列
    """
    if top_n is None or top_n <= 0:
        return df

    if len(df) == 0:
        return df

    # 复制数据以避免修改原始数据
    result_df = df.copy()

    if top_type == 'debit':
        # 按借方金额降序排序
        if '借方金额' in result_df.columns:
            result_df = result_df.sort_values('借方金额', ascending=False)
    elif top_type == 'credit':
        # 按贷方金额降序排序
        if '贷方金额' in result_df.columns:
            result_df = result_df.sort_values('贷方金额', ascending=False)
    elif top_type == 'both':
        # 按借方或贷方金额的绝对值最大值排序
        if '借方金额' in result_df.columns and '贷方金额' in result_df.columns:
            result_df['max_amount'] = result_df[['借方金额', '贷方金额']].abs().max(axis=1)
            result_df = result_df.sort_values('max_amount', ascending=False)
            result_df = result_df.drop(columns=['max_amount'])
        elif '借方金额' in result_df.columns:
            result_df = result_df.sort_values('借方金额', ascending=False)
        elif '贷方金额' in result_df.columns:
            result_df = result_df.sort_values('贷方金额', ascending=False)

    # 返回前N条记录
    return result_df.head(top_n)


def select_columns(df, columns_config):
    """
    根据配置选择输出列，支持多种模式

    Args:
        df (pd.DataFrame): 输入数据
        columns_config (str): 列配置模式，支持:
            - 'all': 返回数据框中的所有列
            - 'default': 返回预设的常用列，自动移除全空的列
            - 逗号分隔的列名: 自定义列选择（如："日期,摘要,借方金额"）

    Returns:
        pd.DataFrame: 包含选定列的数据框

    特殊逻辑:
        • default模式会自动检查客户名称、供应商名称、项目名称三列
        • 如果这些列的所有值都为空，则会从输出中移除
        • 自定义列模式下会显示警告哪些列不存在
    """
    if columns_config == 'all':
        # 返回所有列
        return df

    elif columns_config == 'default':
        # 默认列
        default_columns = [
            '账套名称', '科目编码', '科目全称', '摘要',
            '凭证唯一号', '凭证行号', '借方金额', '贷方金额',
            '日期', '客户名称', '供应商名称', '项目名称'
        ]

        # 选择存在的列
        available_columns = [col for col in default_columns if col in df.columns]

        # 特殊逻辑：检查客户名称、供应商名称、项目名称是否全为空
        columns_to_remove = []
        for col in ['客户名称', '供应商名称', '项目名称']:
            if col in available_columns and df[col].isnull().all():
                columns_to_remove.append(col)

        final_columns = [col for col in available_columns if col not in columns_to_remove]
        return df[final_columns]

    else:
        # 自定义列（逗号分隔）
        custom_columns = [col.strip() for col in columns_config.split(',')]
        available_columns = [col for col in custom_columns if col in df.columns]
        missing_columns = set(custom_columns) - set(available_columns)

        if missing_columns:
            click.echo(f"警告：以下列不存在于数据中：{', '.join(missing_columns)}", err=True)

        return df[available_columns] if available_columns else df


def calculate_statistics(df):
    """
    计算基本统计信息

    Args:
        df (pd.DataFrame): 数据

    Returns:
        dict: 统计信息
    """
    stats = {
        'total_records': len(df),
        'debit_distribution': {},
        'credit_distribution': {}
    }

    # 计算借方金额分布
    if '借方金额' in df.columns:
        debit_data = df['借方金额'].dropna()
        if len(debit_data) > 0:
            stats['debit_distribution'] = {
                'average': debit_data.mean(),
                'mode': debit_data.mode().iloc[0] if not debit_data.mode().empty else None,
                'mode_frequency': debit_data.value_counts().iloc[0] if not debit_data.value_counts().empty else 0
            }

    # 计算贷方金额分布
    if '贷方金额' in df.columns:
        credit_data = df['贷方金额'].dropna()
        if len(credit_data) > 0:
            stats['credit_distribution'] = {
                'average': credit_data.mean(),
                'mode': credit_data.mode().iloc[0] if not credit_data.mode().empty else None,
                'mode_frequency': credit_data.value_counts().iloc[0] if not credit_data.value_counts().empty else 0
            }

    return stats


def analyze_summary_word_frequency(df, top_n=10):
    """
    分析摘要列词频

    Args:
        df (pd.DataFrame): 数据
        top_n (int): 返回前N个高频词

    Returns:
        list: 高频词列表 [(word, count), ...]
    """
    if '摘要' not in df.columns:
        return []

    # 使用简单的分词方案
    click.echo("提示：使用简单分词进行词频分析", err=True)
    return simple_word_frequency(df, top_n)


def simple_word_frequency(df, top_n=10):
    """
    简单的词频分析（不使用cutword）

    Args:
        df (pd.DataFrame): 数据
        top_n (int): 返回前N个高频词

    Returns:
        list: 高频词列表 [(word, count), ...]
    """
    import re

    # 合并所有摘要文本
    all_text = ' '.join(df['摘要'].fillna('').astype(str))

    # 使用正则表达式进行简单的中文分词
    # 匹配中文字符、数字和常见词汇
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', all_text)

    # 过滤常见无意义词汇
    stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '现在', '可以', '但是', '还是', '因为', '什么', '如果', '所以', '对于', '关于', '根据', '通过', '进行', '实现', '完成', '工作', '项目', '技术', '开发', '设计', '系统', '管理', '服务', '产品', '业务', '市场', '客户', '用户', '公司', '企业', '部门', '团队', '人员', '时间', '费用', '成本', '价格', '收入', '支出', '资金', '银行', '转账', '收款', '付款'}

    # 统计词频
    word_freq = {}
    for word in words:
        if len(word.strip()) > 1 and word.strip() not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # 返回前N个高频词
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]


def format_overview_report(stats, word_freq):
    """
    格式化概览报告

    Args:
        stats (dict): 统计信息
        word_freq (list): 词频列表

    Returns:
        str: 格式化的报告
    """
    report = []

    # 基本统计
    report.append("=" * 60)
    report.append("财务数据分析概览报告")
    report.append("=" * 60)
    report.append("")

    # 总记录数
    report.append(f"📊 基本统计")
    report.append(f"   总记录数: {stats['total_records']:,}")
    report.append("")

    # 借方金额分布
    if stats['debit_distribution']:
        report.append(f"💰 借方金额分布")
        report.append(f"   平均值: {stats['debit_distribution']['average']:,.2f}")
        if stats['debit_distribution']['mode'] is not None:
            report.append(f"   众数: {stats['debit_distribution']['mode']:,.2f}")
            report.append(f"   众数频率: {stats['debit_distribution']['mode_frequency']:,}")
        report.append("")

    # 贷方金额分布
    if stats['credit_distribution']:
        report.append(f"💳 贷方金额分布")
        report.append(f"   平均值: {stats['credit_distribution']['average']:,.2f}")
        if stats['credit_distribution']['mode'] is not None:
            report.append(f"   众数: {stats['credit_distribution']['mode']:,.2f}")
            report.append(f"   众数频率: {stats['credit_distribution']['mode_frequency']:,}")
        report.append("")

    # 摘要词频分析
    if word_freq:
        report.append(f"📝 摘要词频分析 (Top {len(word_freq)})")
        for i, (word, count) in enumerate(word_freq, 1):
            report.append(f"   {i:2d}. {word}: {count:,}")
        report.append("")

    report.append("=" * 60)

    return "\n".join(report)


@click.group()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-a', '--account-code', required=True,
              help='会计科目编码 (例如: 1002, 6601.01)')
@click.option('--exact-match', is_flag=True,
              help='使用精确匹配科目编码 (默认为前缀匹配)')
@click.option('-s', '--start-date', required=True,
              help='分析期间开始日期 (格式: YYYY-MM-DD)')
@click.option('-e', '--end-date', required=True,
              help='分析期间结束日期 (格式: YYYY-MM-DD)')
@click.option('-b', '--account-book', required=True,
              help='账套名称 (支持: "账套A", "账套A,账套B", "all")')
@click.option('-q', '--query',
              help='Pandas查询字符串，用于额外筛选 (例如: "借方金额 > 10000")')
@click.pass_context
def cli(ctx, input_file, account_code, exact_match, start_date, end_date, account_book, query):
    """
    财务数据分析命令行工具 (Journal Entries Analyzer)

    快速分析和筛选财务日记账数据，支持多种筛选条件和统计分析。

    使用示例:
      uv run python je_analyzer.py data.xlsx overview -a 1002 -s 2024-01-01 -e 2024-12-31 -b "主账套"
      uv run python je_analyzer.py data.xlsx get --top 10 -a 6601 -s 2024-01-01 -e 2024-12-31 -b "主账套"

    INPUT_FILE: 包含会计分录数据的源文件路径 (.xlsx 或 .xls)
    """
    ctx.ensure_object(dict)
    ctx.obj['input_file'] = input_file
    ctx.obj['account_code'] = account_code
    ctx.obj['exact_match'] = exact_match
    ctx.obj['start_date'] = start_date
    ctx.obj['end_date'] = end_date
    ctx.obj['account_book'] = account_book
    ctx.obj['query'] = query


@cli.command()
@click.pass_context
def overview(ctx):
    """
    生成财务数据分析概览报告

    输出包含以下内容的统计报告:
    • 基本统计信息 (总记录数)
    • 借方金额分布 (平均值、众数、众数频率)
    • 贷方金额分布 (平均值、众数、众数频率)
    • 摘要词频分析 (高频词汇统计)

    示例:
      je_analyzer.py data.xlsx overview -a 1002 -s 2024-01-01 -e 2024-12-31 -b "主账套"
    """
    # 加载数据
    df = load_data(ctx.obj['input_file'])

    # 基础筛选
    filtered_df = filter_data(
        df,
        ctx.obj['account_code'],
        ctx.obj['start_date'],
        ctx.obj['end_date'],
        ctx.obj['account_book'],
        ctx.obj['exact_match']
    )

    # 高级筛选
    if ctx.obj['query']:
        try:
            filtered_df = filtered_df.query(ctx.obj['query'])
        except Exception as e:
            click.echo(f"错误：查询语法错误 - {e}", err=True)
            sys.exit(1)

    if len(filtered_df) == 0:
        click.echo("没有找到符合条件的记录", err=True)
        return

    # 计算统计信息
    stats = calculate_statistics(filtered_df)

    # 分析摘要词频
    word_freq = analyze_summary_word_frequency(filtered_df)

    # 生成并输出报告
    report = format_overview_report(stats, word_freq)
    click.echo(report)


@cli.command()
@click.option('--top', type=int, help='返回Top N条记录 (按金额排序)')
@click.option('--top-type', type=click.Choice(['debit', 'credit', 'both']), default='both',
              help='Top N排序依据: debit=借方金额, credit=贷方金额, both=最大金额')
@click.option('--columns', default='default',
              help='输出列控制: all=所有列, default=预设列, "col1,col2"=自定义列')
@click.pass_context
def get(ctx, top, top_type, columns):
    """
    获取并输出筛选后的原始数据行

    输出格式为制表符分隔，便于复制到其他程序或进一步处理。

    列选择说明:
    • all: 输出Excel文件中的所有列
    • default: 输出预设的常用列 (自动移除空列)
    • 自定义: 指定列名，用逗号分隔 (如: "日期,摘要,借方金额")

    示例:
      je_analyzer.py data.xlsx get --top 10 -a 1002 -s 2024-01-01 -e 2024-12-31 -b "主账套"
      je_analyzer.py data.xlsx get --top 5 --top-type debit --columns "日期,摘要,借方金额"
    """
    # 加载数据
    df = load_data(ctx.obj['input_file'])

    # 基础筛选
    filtered_df = filter_data(
        df,
        ctx.obj['account_code'],
        ctx.obj['start_date'],
        ctx.obj['end_date'],
        ctx.obj['account_book'],
        ctx.obj['exact_match']
    )

    # 高级筛选
    if ctx.obj['query']:
        try:
            filtered_df = filtered_df.query(ctx.obj['query'])
        except Exception as e:
            click.echo(f"错误：查询语法错误 - {e}", err=True)
            sys.exit(1)

    # 应用Top N筛选
    result_df = apply_top_n_filter(filtered_df, top, top_type)

    # 选择输出列
    result_df = select_columns(result_df, columns)

    # 输出结果（制表符分隔）
    if len(result_df) > 0:
        result_df.to_csv(sys.stdout, sep='\t', index=False, encoding='utf-8')
    else:
        click.echo("没有找到符合条件的记录", err=True)


if __name__ == '__main__':
    cli()