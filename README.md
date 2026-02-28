# 生活记录自动排版与分析工具

这个小工具可以把你的生活记录（动作、时长、心情、备注）自动整理为易读的日报样式，并输出分析建议。

## 你能得到什么
- 自动按日期排版成 Markdown 表格。
- 统计总时长、平均心情。
- 找出投入时间最多的动作。
- 给出“提升情绪动作/低情绪动作”的分析与建议。

## 使用方式
1. 准备一个 CSV 文件（字段固定如下）：
   - `timestamp`：ISO 时间，如 `2026-02-26T08:00:00`
   - `action`：动作名称
   - `duration_minutes`：时长（分钟，>0）
   - `mood`：心情分（1-5）
   - `note`：备注

2. 运行命令：

```bash
python life_analyzer.py --input sample_records.csv --output report.md
```

3. 打开 `report.md` 查看自动排版和分析。

## 示例数据
仓库内置了 `sample_records.csv`，可直接运行测试。
