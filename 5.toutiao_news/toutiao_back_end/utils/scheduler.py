import asyncio
import logging
from datetime import datetime, timedelta
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)


def _seconds_until(target_hour: int, target_minute: int) -> float:
    """
    计算距下一次 target_hour:target_minute 的秒数。
    若今天的目标时间已过，则返回距明天目标时间的秒数。
    """
    now = datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def daily_task_runner(
    task: Callable[[], Awaitable[None]],
    stop_event: asyncio.Event,
    hour: int = 0,
    minute: int = 0,
) -> None:
    """
    后台协程：每天在 hour:minute 触发一次 task。
    收到 stop_event 信号后优雅退出。
    """
    logger.info("[scheduler] 后台调度任务启动，下次执行 %02d:%02d", hour, minute)
    while not stop_event.is_set():
        # 等待到下一个目标时刻，或收到停止信号
        wait_seconds = _seconds_until(hour, minute)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=wait_seconds)
            # 如果是被 wait_for 正常超时，wait() 返回 True，但不会抛异常
            # 只有 stop_event 被 set 才会提前结束等待
            break
        except asyncio.TimeoutError:
            # 到点，执行任务
            try:
                logger.info("[scheduler] 开始执行定时任务: %s", task.__name__)
                await task()
                logger.info("[scheduler] 定时任务执行完成: %s", task.__name__)
            except Exception as e:
                logger.exception("[scheduler] 定时任务执行失败: %s, error=%s", task.__name__, e)
            # 执行完毕后 sleep 24h，避免在同一分钟内重复触发
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=24 * 60 * 60)
                break
            except asyncio.TimeoutError:
                continue

    logger.info("[scheduler] 后台调度任务已退出")