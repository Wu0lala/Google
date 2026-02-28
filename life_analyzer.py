#!/usr/bin/env python3
"""生活记录分析器

用法示例:
  python life_analyzer.py --input records.csv --output report.md
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Iterable


@dataclass
class Record:
    timestamp: datetime
    action: str
    duration_minutes: int
    mood: int
    note: str

    @property
    def day(self) -> str:
        return self.timestamp.strftime("%Y-%m-%d")


REQUIRED_COLUMNS = {"timestamp", "action", "duration_minutes", "mood", "note"}


def load_records(path: Path) -> list[Record]:
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV 缺少表头")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"缺少必要列: {', '.join(sorted(missing))}")

        records: list[Record] = []
        for idx, row in enumerate(reader, start=2):
            try:
                ts = datetime.fromisoformat(row["timestamp"])
                action = row["action"].strip()
                if not action:
                    raise ValueError("action 不能为空")
                duration = int(row["duration_minutes"])
                mood = int(row["mood"])
                note = row["note"].strip()
                if duration <= 0:
                    raise ValueError("duration_minutes 必须大于 0")
                if not 1 <= mood <= 5:
                    raise ValueError("mood 必须在 1 到 5 之间")
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"第 {idx} 行数据错误: {exc}") from exc

            records.append(
                Record(
                    timestamp=ts,
                    action=action,
                    duration_minutes=duration,
                    mood=mood,
                    note=note,
                )
            )

    if not records:
        raise ValueError("没有可分析的数据")

    return sorted(records, key=lambda r: r.timestamp)


def _group_by_day(records: Iterable[Record]) -> dict[str, list[Record]]:
    grouped: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        grouped[r.day].append(r)
    return dict(sorted(grouped.items()))


def _analysis_paragraph(records: list[Record]) -> str:
    total_minutes = sum(r.duration_minutes for r in records)
    avg_mood = mean(r.mood for r in records)

    action_minutes: Counter[str] = Counter()
    action_moods: defaultdict[str, list[int]] = defaultdict(list)
    for r in records:
        action_minutes[r.action] += r.duration_minutes
        action_moods[r.action].append(r.mood)

    top_actions = action_minutes.most_common(3)
    happiest_action = max(action_moods.items(), key=lambda kv: mean(kv[1]))
    lowest_action = min(action_moods.items(), key=lambda kv: mean(kv[1]))

    lines = [
        "## 总览分析",
        f"- 总记录条数：{len(records)} 条",
        f"- 累计投入时间：{total_minutes} 分钟（约 {total_minutes / 60:.1f} 小时）",
        f"- 平均心情评分：{avg_mood:.2f} / 5",
        "",
        "### 时间投入最多的动作",
    ]

    for i, (action, minutes) in enumerate(top_actions, start=1):
        lines.append(f"{i}. **{action}**：{minutes} 分钟")

    lines += [
        "",
        "### 情绪关联",
        f"- 最能提升情绪的动作：**{happiest_action[0]}**（平均心情 {mean(happiest_action[1]):.2f}）",
        f"- 情绪最低的动作：**{lowest_action[0]}**（平均心情 {mean(lowest_action[1]):.2f}）",
        "",
        "### 建议",
        f"- 维持高收益动作（如 {happiest_action[0]}）的稳定频率。",
        f"- 复盘低情绪动作（如 {lowest_action[0]}）：尝试缩短时长、换时间段或拆成更小任务。",
    ]

    return "\n".join(lines)


def render_markdown(records: list[Record]) -> str:
    grouped = _group_by_day(records)

    lines = [
        "# 生活记录自动排版报告",
        "",
        "说明：以下数据由 CSV 自动整理与分析。",
        "",
    ]

    for day, day_records in grouped.items():
        lines += [f"## {day}", "", "| 时间 | 动作 | 时长(分钟) | 心情(1-5) | 备注 |", "|---|---|---:|---:|---|"]
        for r in day_records:
            lines.append(
                f"| {r.timestamp.strftime('%H:%M')} | {r.action} | {r.duration_minutes} | {r.mood} | {r.note or '-'} |"
            )
        day_minutes = sum(r.duration_minutes for r in day_records)
        day_mood = mean(r.mood for r in day_records)
        lines += ["", f"- 当日总时长：{day_minutes} 分钟", f"- 当日平均心情：{day_mood:.2f}", ""]

    lines += ["---", "", _analysis_paragraph(records), ""]

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生活记录自动排版与分析")
    parser.add_argument("--input", required=True, type=Path, help="输入 CSV 文件")
    parser.add_argument("--output", required=True, type=Path, help="输出 Markdown 报告")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_records(args.input)
    report = render_markdown(records)
    args.output.write_text(report, encoding="utf-8")
    print(f"已生成报告: {args.output}")


if __name__ == "__main__":
    main()
