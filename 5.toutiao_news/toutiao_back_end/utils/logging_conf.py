import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# 业务 logger 白名单：模块名前缀，命中其一即视为业务日志
BUSINESS_LOGGER_PREFIXES = (
    "app",
    "utils",
    "routers",
    "crud",
    "models",
    "schemas",
)


class BusinessFilter(logging.Filter):
    """
    仅放行 logger name 命中白名单的日志记录。
    """

    def filter(self, record: logging.LogRecord) -> bool:
        name = record.name
        return any(
            name == prefix or name.startswith(prefix + ".")
            for prefix in BUSINESS_LOGGER_PREFIXES
        )


class DailyFileHandler(logging.FileHandler):
    """
    按当天日期自动切换文件的 Handler。
    文件命名: {YYYY_MM_DD}.log
    每次 emit 时检查日期，跨天则切换文件并触发清理逻辑。
    """

    def __init__(
        self,
        directory: Path,
        retention_days: int = 30,
        encoding: str = "utf-8",
        delay: bool = False,
    ):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self._current_date: Optional[str] = None
        self._on_rollover: Optional[callable] = None
        # 先让基类初始化底层 stream
        super().__init__(self._current_filepath(), mode="a", encoding=encoding, delay=delay)
        self._current_date = datetime.now().strftime("%Y_%m_%d")

    def set_rollover_callback(self, callback):
        """注册跨天时调用的回调（用于清理过期文件）"""
        self._on_rollover = callback

    def _current_filepath(self) -> str:
        date_str = datetime.now().strftime("%Y_%m_%d")
        return str(self.directory / f"{date_str}.log")

    def emit(self, record: logging.LogRecord) -> None:
        today = datetime.now().strftime("%Y_%m_%d")
        if today != self._current_date:
            # 跨天了：关旧、开新
            self._close()
            self._current_date = today
            self.baseFilename = str(self.directory / f"{today}.log")
            self._open()
            # 触发跨天回调（清理过期文件）
            if self._on_rollover is not None:
                try:
                    self._on_rollover()
                except Exception:
                    pass
        super().emit(record)

    def close(self) -> None:
        try:
            super().close()
        except Exception:
            pass


def _clean_old_logs(directory: Path, retention_days: int) -> None:
    """删除 mtime 早于 (今天 - retention_days) 的日志文件"""
    if retention_days <= 0:
        return
    if not directory.exists():
        return
    threshold = datetime.now() - timedelta(days=retention_days)
    for file in directory.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if mtime < threshold:
                file.unlink(missing_ok=True)
        except Exception:
            # 单个文件清理失败不影响整体
            pass


def setup_logging(log_dir: str = "logs", retention_days: int = 30) -> None:
    """
    初始化项目日志系统:
    - 控制台: root logger, INFO 及以上
    - 业务 success_log: {log_dir}/success_log/{YYYY_MM_DD}.log, DEBUG 及以上
    - 业务 error_log:   {log_dir}/error_log/{YYYY_MM_DD}.log,   ERROR 及以上
    - 仅白名单 logger (app / utils / routers / crud / models / schemas) 写入文件
    - 自动清理 retention_days 天前的日志
    """
    base = Path(log_dir)
    success_dir = base / "success_log"
    error_dir = base / "error_log"
    success_dir.mkdir(parents=True, exist_ok=True)
    error_dir.mkdir(parents=True, exist_ok=True)

    # 启动时先清一次过期文件（兜底）
    _clean_old_logs(success_dir, retention_days)
    _clean_old_logs(error_dir, retention_days)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # 1) 控制台 handler：绑到 root logger，输出所有 INFO+
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # 清掉已有的 handler，避免重复输出
    for h in list(root.handlers):
        root.removeHandler(h)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # 2) 业务 logger：起一个名为 "app" 的子 logger，propagate=False
    #    sqlalchemy / uvicorn / fastapi 不挂在 app 下，不会进入文件
    business_logger = logging.getLogger("app")
    business_logger.setLevel(logging.DEBUG)
    business_logger.propagate = False
    # 清理可能已有的旧 handler
    for h in list(business_logger.handlers):
        business_logger.removeHandler(h)

    success_handler = DailyFileHandler(success_dir, retention_days=retention_days)
    success_handler.setLevel(logging.DEBUG)
    success_handler.addFilter(BusinessFilter())
    success_handler.setFormatter(formatter)
    success_handler.set_rollover_callback(
        lambda: (_clean_old_logs(success_dir, retention_days),
                 _clean_old_logs(error_dir, retention_days))
    )
    business_logger.addHandler(success_handler)

    error_handler = DailyFileHandler(error_dir, retention_days=retention_days)
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(BusinessFilter())
    error_handler.setFormatter(formatter)
    error_handler.set_rollover_callback(
        lambda: (_clean_old_logs(success_dir, retention_days),
                 _clean_old_logs(error_dir, retention_days))
    )
    business_logger.addHandler(error_handler)