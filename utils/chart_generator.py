# -*- coding: utf-8 -*-
"""
好易易GEO - 数据可视化模块
使用ASCII图形实现图表生成，不依赖外部可视化库
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter


class ASCIIGraphics:
    """ASCII图形生成器"""
    
    # 配色方案（使用终端颜色代码）
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
    }
    
    # 无颜色版本（纯ASCII）
    CHARS = {
        'bar': '█',
        'bar_light': '▓',
        'bar_medium': '░',
        'line': '─',
        'vertical': '│',
        'corner': '┼',
        'top_left': '┌',
        'top_right': '┐',
        'bottom_left': '└',
        'bottom_right': '┘',
        'bullet': '•',
        'star': '★',
        'dot': '●',
        'triangle_up': '▲',
        'triangle_down': '▼',
    }


def generate_bar_chart(
    data: Dict[str, int],
    title: str = "数据分布",
    width: int = 60,
    height: int = 15,
    show_values: bool = True,
    color: bool = False
) -> str:
    """
    生成ASCII柱状图
    
    Args:
        data: 字典，键为标签，值为数据
        title: 图表标题
        width: 图表宽度
        height: 图表高度
        show_values: 是否显示数值
        color: 是否使用颜色
    
    Returns:
        ASCII图表字符串
    """
    if not data:
        return "暂无数据"
    
    # 按值排序
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0][:10] for item in sorted_data]  # 限制标签长度
    values = [item[1] for item in sorted_data]
    
    # 计算比例
    max_value = max(values) if values else 1
    max_bar_height = height - 3  # 留出标签和标题空间
    
    # 构建图表
    lines = []
    
    # 标题
    title_padding = (width - len(title)) // 2
    lines.append('┌' + '─' * width + '┐')
    lines.append('│' + ' ' * title_padding + title + ' ' * (width - title_padding - len(title)) + '│')
    lines.append('├' + '─' * width + '┤')
    
    # Y轴刻度和网格
    y_axis_chars = []
    for i in range(max_bar_height, 0, -1):
        y_val = int((i / max_bar_height) * max_value)
        y_str = f"{y_val:>4}"
        
        row = y_str + ' │'
        for val in values:
            bar_height = int((val / max_value) * max_bar_height)
            if bar_height >= i:
                row += ' █ '
            else:
                row += '   '
        row += ' │'
        y_axis_chars.append(row)
    
    lines.extend(y_axis_chars)
    
    # X轴
    x_axis = '────┼' + '───┼' * (len(labels) - 1) + '───┤'
    lines.append(x_axis)
    
    # 标签
    label_row = '    └' + '───┴' * (len(labels) - 1) + '───┘'
    lines.append(label_row)
    
    # 显示具体数值
    if show_values:
        value_row = '     '
        for v in values:
            value_row += f'{v:>3} '
        lines.append(value_row)
    
    # 标签行（对齐到数值下方）
    label_line = '       '
    for label in labels:
        label_line += f'{label:^3}'
    lines.append(label_line)
    
    return '\n'.join(lines)


def generate_horizontal_bar_chart(
    data: Dict[str, int],
    title: str = "数据分布",
    width: int = 50,
    show_values: bool = True
) -> str:
    """
    生成水平柱状图
    
    Args:
        data: 字典，键为标签，值为数据
        title: 图表标题
        width: 柱状图宽度（不含标签）
        show_values: 是否显示数值
    
    Returns:
        ASCII图表字符串
    """
    if not data:
        return "暂无数据"
    
    # 按值排序
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    max_value = max(v for _, v in sorted_data) if sorted_data else 1
    max_label_len = max(len(str(k)) for k, _ in sorted_data) if sorted_data else 0
    
    lines = []
    
    # 标题
    lines.append(f'\n{title}')
    lines.append('=' * (max_label_len + width + 15))
    
    for label, value in sorted_data:
        # 计算柱状条长度
        bar_len = int((value / max_value) * width) if max_value > 0 else 0
        
        # 构建行
        bar = '█' * bar_len
        if show_values:
            row = f'{label:>{max_label_len}} │{bar} │ {value}'
        else:
            row = f'{label:>{max_label_len}} │{bar} │'
        lines.append(row)
    
    lines.append('=' * (max_label_len + width + 15))
    
    return '\n'.join(lines)


def generate_radar_chart(
    data: Dict[str, float],
    title: str = "多维度对比",
    max_value: float = 100,
    size: int = 5
) -> str:
    """
    生成ASCII雷达图（简化版）
    
    Args:
        data: 字典，键为维度名，值为数据（0-100）
        title: 图表标题
        max_value: 最大值
        size: 雷达图大小级别（3-7）
    
    Returns:
        ASCII雷达图字符串
    """
    if not data:
        return "暂无数据"
    
    dimensions = list(data.keys())
    values = list(data.values())
    n = len(dimensions)
    
    if n < 3:
        return "雷达图需要至少3个维度"
    
    # 构建同心多边形
    lines = []
    lines.append(f'\n{title}')
    lines.append('─' * 50)
    
    # 简化的雷达图表示
    # 使用字符来模拟雷达图
    center = size
    grid_chars = {
        3: '  ▲  ',
        4: '  ◆  ',
        5: '  ⬠  ',
        6: '  ⬡  ',
        7: '  ✦  '
    }
    
    # 绘制网格线
    for level in range(size, 0, -1):
        row = ' ' * (level * 2)
        level_chars = []
        for i in range(n):
            angle_pos = (360 / n) * i
            # 简化为8个方向
            if angle_pos in [0, 45, 90, 135, 180, 225, 270, 315]:
                level_chars.append('●')
            else:
                level_chars.append('○')
        row += ' '.join(level_chars)
        lines.append(row)
    
    # 绘制数据点
    data_row = '  '
    for val in values:
        ratio = val / max_value
        if ratio >= 0.8:
            data_row += '★'
        elif ratio >= 0.5:
            data_row += '◆'
        elif ratio >= 0.2:
            data_row += '○'
        else:
            data_row += '·'
        data_row += '  '
    lines.append(data_row)
    
    # 维度标签
    label_row = '  '
    for dim in dimensions:
        label_row += f'{dim[:6]:^6}'
    lines.append(label_row)
    
    lines.append('─' * 50)
    
    return '\n'.join(lines)


def generate_pie_chart(
    data: Dict[str, int],
    title: str = "占比分布",
    show_percentage: bool = True
) -> str:
    """
    生成ASCII饼图（简化版）
    
    Args:
        data: 字典，键为标签，值为数据
        title: 图表标题
        show_percentage: 是否显示百分比
    
    Returns:
        ASCII饼图字符串
    """
    if not data:
        return "暂无数据"
    
    total = sum(data.values())
    if total == 0:
        return "数据总和为0"
    
    # 定义饼图字符（使用渐变字符表示不同区域）
    pie_chars = ['●', '○', '◐', '◑', '◔', '◕']
    
    lines = []
    lines.append(f'\n{title}')
    lines.append('═' * 40)
    
    # 计算每个类别的占比
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    # 绘制饼图（使用圆环表示）
    radius = 5
    
    # 外圈
    for row in range(-radius, radius + 1):
        line = ''
        for col in range(-radius, radius + 1):
            dist = (row**2 + col**2) ** 0.5
            if dist <= radius:
                line += '●'
            elif dist <= radius + 0.5:
                line += '○'
            else:
                line += ' '
        lines.append(line)
    
    # 图例
    lines.append('')
    for i, (label, value) in enumerate(sorted_data):
        percentage = (value / total) * 100
        if show_percentage:
            lines.append(f'  {pie_chars[i % len(pie_chars)]} {label}: {value} ({percentage:.1f}%)')
        else:
            lines.append(f'  {pie_chars[i % len(pie_chars)]} {label}: {value}')
    
    lines.append('═' * 40)
    
    return '\n'.join(lines)


def generate_donut_chart(
    data: Dict[str, int],
    title: str = "占比分布",
    show_percentage: bool = True
) -> str:
    """
    生成ASCII环形图
    
    Args:
        data: 字典，键为标签，值为数据
        title: 图表标题
        show_percentage: 是否显示百分比
    
    Returns:
        ASCII环形图字符串
    """
    if not data:
        return "暂无数据"
    
    total = sum(data.values())
    if total == 0:
        return "数据总和为0"
    
    lines = []
    lines.append(f'\n{title}')
    lines.append('═' * 40)
    
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    
    # 简化的环形图
    radius = 6
    
    for row in range(-radius, radius + 1):
        line = ''
        for col in range(-radius, radius + 1):
            dist = (row**2 + col**2) ** 0.5
            if radius * 0.5 <= dist <= radius:
                # 环形区域
                angle = abs((row, col))
                line += '█'
            elif dist < radius * 0.5:
                line += ' '
            else:
                line += ' '
        lines.append(line)
    
    # 图例
    lines.append('')
    chars = ['●', '○', '◆', '◇', '★', '☆']
    for i, (label, value) in enumerate(sorted_data):
        percentage = (value / total) * 100
        if show_percentage:
            lines.append(f'  {chars[i % len(chars)]} {label}: {value} ({percentage:.1f}%)')
        else:
            lines.append(f'  {chars[i % len(chars)]} {label}: {value}')
    
    lines.append('═' * 40)
    
    return '\n'.join(lines)


def generate_line_chart(
    data: List[Tuple[str, float]],
    title: str = "趋势变化",
    width: int = 50,
    height: int = 10
) -> str:
    """
    生成ASCII折线图
    
    Args:
        data: 数据列表，每项为(标签, 数值)元组
        title: 图表标题
        width: 图表宽度
        height: 图表高度
    
    Returns:
        ASCII折线图字符串
    """
    if not data or len(data) < 2:
        return "数据不足，无法生成折线图"
    
    labels = [str(item[0]) for item in data]
    values = [item[1] for item in data]
    
    max_value = max(values)
    min_value = min(values)
    value_range = max_value - min_value if max_value != min_value else 1
    
    lines = []
    lines.append(f'\n{title}')
    lines.append('─' * (width + 15))
    
    # 绘制Y轴
    for i in range(height, 0, -1):
        y_val = min_value + (value_range * i / height)
        y_str = f'{y_val:>6.1f} │'
        
        row = y_str
        for val in values:
            normalized_y = int(((val - min_value) / value_range) * (height - 1)) + 1
            if normalized_y == i:
                row += ' ● '
            elif abs(normalized_y - i) <= 1 and i == 1:
                row += ' ● '
            else:
                row += '   '
        
        # 绘制连接线
        row += ' │'
        lines.append(row)
    
    # X轴
    x_axis = '       └' + '───┴' * (len(values) - 1) + '───┘'
    lines.append(x_axis)
    
    # X轴标签
    label_line = '        '
    for label in labels:
        label_line += f'{label[:3]:^3}'
    lines.append(label_line)
    
    lines.append('─' * (width + 15))
    
    return '\n'.join(lines)


def generate_comparison_chart(
    brand_data: Dict[str, float],
    competitor_data: Dict[str, Dict[str, float]],
    title: str = "品牌对比分析"
) -> str:
    """
    生成品牌对比图表
    
    Args:
        brand_data: 本品牌数据 {指标名: 数值}
        competitor_data: 竞品数据 {竞品名: {指标名: 数值}}
        title: 图表标题
    
    Returns:
        ASCII对比图字符串
    """
    if not brand_data:
        return "暂无品牌数据"
    
    lines = []
    lines.append(f'\n{title}')
    lines.append('═' * 60)
    
    metrics = list(brand_data.keys())
    
    # 绘制每个指标的对比
    for metric in metrics:
        lines.append(f'\n【{metric}】')
        
        brand_value = brand_data.get(metric, 0)
        max_value = brand_value
        
        # 收集竞品数据
        all_values = [(metric, brand_value)]  # 本品牌
        for comp_name, comp_metrics in competitor_data.items():
            comp_value = comp_metrics.get(metric, 0)
            all_values.append((comp_name, comp_value))
            max_value = max(max_value, comp_value)
        
        # 按值排序
        all_values.sort(key=lambda x: x[1], reverse=True)
        
        # 绘制条形图
        bar_width = 30
        for name, value in all_values:
            bar_len = int((value / max_value) * bar_width) if max_value > 0 else 0
            is_brand = (name == metric)
            bar_char = '█' if is_brand else '▓'
            bar = bar_char * bar_len
            lines.append(f'  {name[:10]:<10} │{bar} {value:.1f}')
    
    lines.append('\n' + '═' * 60)
    lines.append('  注：█ 表示本品牌，▓ 表示竞品')
    
    return '\n'.join(lines)


def generate_table(
    headers: List[str],
    rows: List[List[str]],
    title: str = "",
    align: str = "lcr"  # l=左对齐, c=居中, r=右对齐
) -> str:
    """
    生成ASCII表格
    
    Args:
        headers: 表头列表
        rows: 数据行列表
        title: 表格标题
        align: 对齐方式字符串（如"lcr"表示左、中、右）
    
    Returns:
        ASCII表格字符串
    """
    if not headers:
        return "暂无表头数据"
    
    # 计算每列宽度
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 确保至少有2个字符宽度
    col_widths = [max(w, 2) for w in col_widths]
    
    lines = []
    
    # 标题
    if title:
        lines.append(f'\n{title}')
        lines.append('─' * (sum(col_widths) + len(col_widths) * 3 + 1))
    
    # 表头
    header_row = '│'
    for i, h in enumerate(headers):
        width = col_widths[i]
        align_char = align[i] if i < len(align) else 'l'
        if align_char == 'c':
            padding = (width - len(h)) // 2
            header_row += f' {h:^{width}} │'
        elif align_char == 'r':
            header_row += f' {h:>{width}} │'
        else:
            header_row += f' {h:<{width}} │'
    lines.append(header_row)
    
    # 分隔线
    sep = '├' + '┼'.join('─' * (w + 2) for w in col_widths) + '┤'
    lines.append(sep)
    
    # 数据行
    for row in rows:
        data_row = '│'
        for i, cell in enumerate(row):
            width = col_widths[i]
            cell_str = str(cell)
            align_char = align[i] if i < len(align) else 'l'
            if align_char == 'c':
                data_row += f' {cell_str:^{width}} │'
            elif align_char == 'r':
                data_row += f' {cell_str:>{width}} │'
            else:
                data_row += f' {cell_str:<{width}} │'
        lines.append(data_row)
    
    # 底部边框
    bottom = '└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘'
    lines.append(bottom)
    
    return '\n'.join(lines)


def generate_emoji_rating(
    score: float,
    max_score: float = 100,
    emoji_count: int = 5
) -> str:
    """
    生成表情评分
    
    Args:
        score: 得分
        max_score: 满分
        emoji_count: 表情数量
    
    Returns:
        评分字符串（如 ⭐⭐⭐⭐☆）
    """
    ratio = score / max_score
    filled = int(ratio * emoji_count)
    empty = emoji_count - filled
    
    return '⭐' * filled + '☆' * empty


def generate_progress_bar(
    current: float,
    total: float,
    width: int = 30,
    prefix: str = "",
    suffix: str = ""
) -> str:
    """
    生成进度条
    
    Args:
        current: 当前值
        total: 总值
        width: 进度条宽度
        prefix: 前缀文字
        suffix: 后缀文字
    
    Returns:
        进度条字符串
    """
    if total == 0:
        ratio = 0
    else:
        ratio = min(current / total, 1.0)
    
    filled = int(ratio * width)
    empty = width - filled
    
    bar = '█' * filled + '░' * empty
    percentage = int(ratio * 100)
    
    return f'{prefix}[{bar}] {percentage}%{suffix}'


# 便捷函数：生成平台提及图
def generate_platform_mentions_chart(platform_data: Dict[str, int]) -> str:
    """生成平台提及柱状图"""
    return generate_horizontal_bar_chart(
        platform_data,
        title="📊 AI平台提及分布",
        width=40
    )


# 便捷函数：生成竞品对比雷达图
def generate_competitor_radar(
    brand_metrics: Dict[str, float],
    competitor_metrics: Dict[str, float]
) -> str:
    """生成竞品对比雷达图"""
    # 合并所有指标
    all_metrics = {}
    for metric, value in brand_metrics.items():
        all_metrics[f"{metric}"] = value
    
    # 简化为表格对比
    lines = ['\n📡 竞品对比雷达\n', '═' * 40]
    
    for metric, brand_val in brand_metrics.items():
        comp_val = competitor_metrics.get(metric, 0)
        diff = brand_val - comp_val
        diff_str = f"+{diff:.1f}" if diff >= 0 else f"{diff:.1f}"
        
        brand_bar = '█' * int(brand_val / 10)
        comp_bar = '▓' * int(comp_val / 10)
        
        lines.append(f'{metric[:6]}:')
        lines.append(f'  本品牌 {brand_bar} {brand_val:.0f}')
        lines.append(f'  竞品   {comp_bar} {comp_val:.0f}')
        lines.append(f'  差距   {diff_str}')
    
    lines.append('═' * 40)
    return '\n'.join(lines)


# 便捷函数：生成情感分析饼图
def generate_sentiment_pie_chart(sentiment_data: Dict[str, int]) -> str:
    """生成情感分析饼图"""
    return generate_donut_chart(
        sentiment_data,
        title="💭 情感倾向分析",
        show_percentage=True
    )


if __name__ == '__main__':
    # 测试各种图表生成
    
    # 测试柱状图
    print("=" * 60)
    print("测试1: 平台提及柱状图")
    print(generate_bar_chart(
        {'小红书': 85, '知乎': 72, '微信公众号': 65, '抖音': 55, 'B站': 40},
        title="各平台提及量"
    ))
    
    print("\n" + "=" * 60)
    print("测试2: 水平柱状图")
    print(generate_horizontal_bar_chart(
        {'武商梦时代': 95, '武汉SKP': 90, '武商MALL': 78, '万象城': 72, '永旺': 65},
        title="商场GEO评分"
    ))
    
    print("\n" + "=" * 60)
    print("测试3: 情感分析环形图")
    print(generate_donut_chart(
        {'正面': 65, '中性': 25, '负面': 10},
        title="情感倾向分布"
    ))
    
    print("\n" + "=" * 60)
    print("测试4: 对比表格")
    print(generate_table(
        ['品牌', '可见度', '推荐度', '情感'],
        [
            ['武商梦时代', 95, 88, '优秀'],
            ['武汉SKP', 92, 90, '优秀'],
            ['武商MALL', 78, 75, '良好'],
        ],
        title="品牌健康度对比"
    ))
    
    print("\n" + "=" * 60)
    print("测试5: 进度条")
    print(generate_progress_bar(78, 100, prefix="GEO评分: "))
    
    print("\n" + "=" * 60)
    print("测试6: 评分表情")
    print(f"GEO评分: {generate_emoji_rating(85)} (85/100)")
