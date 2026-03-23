# 通知
import threading
from datetime import datetime
from pathlib import Path

import requests
from core.logger import mlog
from core.common import cfg

# ── 推送报告收集器 ─────────────────────────────────────────────────────────────
_report: list[str] = []
_report_lock = threading.Lock()

# notify 专属日志文件（与主日志分开，控制台不显示内容）
_notify_log: Path = cfg.log_dir / f"notify-{datetime.now().strftime('%Y-%m-%d')}.log"


def report(content: str) -> None:
    """收集报告段：追加到推送列表并写入 notify 日志，主日志仅记录指针。"""
    with _report_lock:
        _report.append(content)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(_notify_log, "a", encoding="utf-8") as f:
        f.write(f"[{ts}]\n{content}\n\n")
    mlog.info(f"[notify] 报告已写入 → {_notify_log.name}")


# ── 格式工具 ───────────────────────────────────────────────────────────────────

def notify_wrapper(content: str, title: str | None = None) -> str:
    """给每个任务通知生成带标题分隔线的纯文本段落。"""
    frt = "=" * 10
    header = f"{frt}{title}{frt}" if title else frt * 3
    footer = frt * 3
    return f"{header}\n{content.strip()}\n{footer}"


def _to_code_block(text: str) -> str:
    """推送前包入代码围栏，避免 Server酱 解析 [] 等 Markdown 语法。"""
    return f"```\n{text}\n```"


def push_wechat(send_key: str) -> None:
    """将本次会话收集到的任务报告推送到 Server 酱。"""
    if not _report:
        mlog.warning("推送内容为空，跳过")
        return
    content = "\n\n".join(_to_code_block(item) for item in _report)
    url = f"https://sctapi.ftqq.com/{send_key}.send"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    params = {"title": "自动化任务报告", "desp": content}
    try:
        requests.post(url, json=params, headers=headers, timeout=10)
        mlog.info("Server 酱推送成功")
    except Exception as e:
        mlog.error(f"Server 酱推送失败: {e}")
