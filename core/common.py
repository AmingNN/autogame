from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, model_validator
import yaml


class SystemConfig(BaseModel):
    log_level: str = "INFO"
    webhook_port: int = 8000
    shutdown_on_complete: bool = True
    shutdown_delay_seconds: int = 60
    shutdown_timeout_hours: float = 1.5
    poll_interval_hours: float = 2.0
    server_chan_key: str = ""


class TaskConfig(BaseModel):
    enabled: bool = False
    interval_hours: float = 24.0
    # tasks/ 内的 module.function 路径，例如 "skyland_sign.skyland.start"
    # 留空表示无 Python 入口（纯 webhook 驱动任务，如 maa）
    entry: str = ""
    # "entry"：entry 函数开始执行时记录任务开始
    # "run"  ：轮询触发时即记录开始（entry 为空时自动使用此模式）
    start_on: Literal["entry", "run"] = "entry"
    # "entry"  ：entry 函数返回即视为完成
    # "webhook"：等待外部 webhook 回调才算完成
    done_on: Literal["entry", "webhook"] = "entry"

    @model_validator(mode="before")
    @classmethod
    def _compat_webhook_notify(cls, data: Any) -> Any:
        """兼容旧版 webhook_notify 字段。"""
        if isinstance(data, dict) and "webhook_notify" in data and "done_on" not in data:
            data = dict(data)
            data["done_on"] = "webhook" if data.pop("webhook_notify") else "entry"
        elif isinstance(data, dict):
            data.pop("webhook_notify", None)
        return data


class Config(BaseModel):
    # root 和 cfg_path 不能更改
    root: Path = Path(__file__).resolve().parent.parent
    cfg_path: Path = root / "config.yaml"
    log_dir: Path = root / "logs"
    db_path: Path = root / "state.json"

    system: SystemConfig = SystemConfig()
    tasks: dict[str, TaskConfig] = {}

    @model_validator(mode="before")
    @classmethod
    def _coerce_tasks(cls, data: Any) -> Any:
        if isinstance(data, dict) and "tasks" in data:
            raw = data["tasks"]
            if isinstance(raw, dict):
                data["tasks"] = {
                    k: TaskConfig(**v) if isinstance(v, dict) else v
                    for k, v in raw.items()
                }
        return data

    @classmethod
    def load(cls) -> "Config":
        defaults = cls()
        if not defaults.cfg_path.exists():
            return defaults
        with open(defaults.cfg_path, mode="r", encoding="utf-8") as f:
            file_data = yaml.safe_load(f) or {}
        # 通过构造器重新走完整的验证流程
        return cls(**file_data)


cfg = Config.load()

if __name__ == "__main__":
    from rich import print
    print(cfg)
