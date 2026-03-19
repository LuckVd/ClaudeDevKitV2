"""文件监控模块"""

import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from voice_coder.config import CorpusConfig
from voice_coder.extractor import IncrementalExtractor


class DebouncedUpdater:
    """
    防抖更新器

    收集文件变化事件，延迟后统一处理
    """

    def __init__(
        self,
        delay: float = 10.0,
        callback: Callable[[set[Path]], None] | None = None,
    ):
        """
        初始化防抖更新器

        Args:
            delay: 防抖延迟时间（秒）
            callback: 更新回调函数
        """
        self.delay = delay
        self.callback = callback
        self._timer: threading.Timer | None = None
        self._pending_files: set[Path] = set()
        self._lock = threading.Lock()

    def on_file_change(self, file_path: Path) -> None:
        """
        文件变化时调用

        Args:
            file_path: 变化的文件路径
        """
        with self._lock:
            self._pending_files.add(file_path)

            # 取消之前的定时器
            if self._timer is not None:
                self._timer.cancel()

            # 设置新的定时器
            self._timer = threading.Timer(self.delay, self._do_update)
            self._timer.start()

    def _do_update(self) -> None:
        """执行更新"""
        with self._lock:
            if self.callback and self._pending_files:
                self.callback(self._pending_files.copy())
            self._pending_files.clear()
            self._timer = None

    def stop(self) -> None:
        """停止防抖器"""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None


class CorpusEventHandler(FileSystemEventHandler):
    """
    语料库事件处理器

    处理文件系统事件，过滤并转发给防抖更新器
    """

    def __init__(
        self,
        config: CorpusConfig,
        updater: DebouncedUpdater,
    ):
        """
        初始化事件处理器

        Args:
            config: 语料库配置
            updater: 防抖更新器
        """
        super().__init__()
        self.config = config
        self.updater = updater

    def on_modified(self, event: FileSystemEvent) -> None:
        """文件修改事件"""
        if not event.is_directory:
            path = Path(event.src_path)
            if self._should_watch(path):
                self.updater.on_file_change(path)

    def on_created(self, event: FileSystemEvent) -> None:
        """文件创建事件"""
        if not event.is_directory:
            path = Path(event.src_path)
            if self._should_watch(path):
                self.updater.on_file_change(path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        """文件删除事件"""
        if not event.is_directory:
            path = Path(event.src_path)
            if self._should_watch(path):
                self.updater.on_file_change(path)

    def _should_watch(self, file_path: Path) -> bool:
        """检查文件是否应该被监控"""
        # 检查扩展名
        if file_path.suffix not in self.config.extensions:
            return False

        # 检查是否在排除目录中
        if any(excluded in file_path.parts for excluded in self.config.exclude):
            return False

        return True


class FileWatcher:
    """
    文件监控器

    监控语料库目录，文件变化时触发回调
    """

    def __init__(
        self,
        config: CorpusConfig,
        on_update: Callable[[dict[str, float]], None],
        debounce_delay: float = 10.0,
    ):
        """
        初始化文件监控器

        Args:
            config: 语料库配置
            on_update: 热词更新回调
            debounce_delay: 防抖延迟时间（秒）
        """
        self.config = config
        self.on_update = on_update
        self.debounce_delay = debounce_delay

        self._extractor = IncrementalExtractor(config)
        self._observer: Observer | None = None
        self._debouncer: DebouncedUpdater | None = None

    def start(self) -> dict[str, float]:
        """
        启动监控

        Returns:
            初始热词字典
        """
        # 初始扫描
        initial_hotwords = self._extractor.initial_scan()

        # 设置防抖更新器
        self._debouncer = DebouncedUpdater(
            delay=self.debounce_delay,
            callback=self._on_files_changed,
        )

        # 设置文件系统观察者
        self._observer = Observer()
        handler = CorpusEventHandler(self.config, self._debouncer)

        for base_path in self.config.paths:
            if base_path.exists():
                self._observer.schedule(handler, str(base_path), recursive=True)

        self._observer.start()
        return initial_hotwords

    def stop(self) -> None:
        """停止监控"""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._observer = None

        if self._debouncer is not None:
            self._debouncer.stop()
            self._debouncer = None

    def _on_files_changed(self, file_paths: set[Path]) -> None:
        """文件变化回调"""
        # 增量更新热词
        new_hotwords = self._extractor.update_files(file_paths)

        # 调用用户回调
        if self.on_update:
            self.on_update(new_hotwords)
