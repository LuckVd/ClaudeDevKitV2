"""文件监控模块测试"""

import tempfile
import threading
import time
from pathlib import Path

import pytest

from voice_coder.config import CorpusConfig
from voice_coder.extractor import IncrementalExtractor
from voice_coder.watcher import DebouncedUpdater


class TestIncrementalExtractor:
    """测试增量提取器"""

    def test_initial_scan(self, tmp_path: Path):
        """测试初始扫描"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("class MyClass: pass")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = IncrementalExtractor(config)
        hotwords = extractor.initial_scan()

        assert "MyClass" in hotwords

    def test_update_files_add(self, tmp_path: Path):
        """测试增量添加文件"""
        # 初始扫描
        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = IncrementalExtractor(config)
        extractor.initial_scan()

        # 添加新文件
        new_file = tmp_path / "new.py"
        new_file.write_text("class NewClass: pass")

        hotwords = extractor.update_files({new_file})
        assert "NewClass" in hotwords

    def test_update_files_modify(self, tmp_path: Path):
        """测试增量修改文件"""
        # 初始扫描
        test_file = tmp_path / "test.py"
        test_file.write_text("class OldClass: pass")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = IncrementalExtractor(config)
        extractor.initial_scan()

        assert "OldClass" in extractor._term_counter

        # 修改文件
        test_file.write_text("class NewClass: pass")
        hotwords = extractor.update_files({test_file})

        # OldClass 应该被移除
        assert "OldClass" not in hotwords
        assert "NewClass" in hotwords

    def test_update_files_delete(self, tmp_path: Path):
        """测试增量删除文件"""
        # 初始扫描
        test_file = tmp_path / "test.py"
        test_file.write_text("class MyClass: pass")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = IncrementalExtractor(config)
        extractor.initial_scan()

        assert "MyClass" in extractor._term_counter

        # 删除文件
        test_file.unlink()
        hotwords = extractor.update_files({test_file})

        # MyClass 应该被移除
        assert "MyClass" not in hotwords

    def test_exclude_directories(self, tmp_path: Path):
        """测试排除目录"""
        # 创建排除目录中的文件
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        excluded_file = node_modules / "test.py"
        excluded_file.write_text("class Excluded: pass")

        config = CorpusConfig(
            paths=[tmp_path],
            extensions=[".py"],
            exclude=["node_modules"],
        )
        extractor = IncrementalExtractor(config)
        hotwords = extractor.initial_scan()

        assert "Excluded" not in hotwords


class TestDebouncedUpdater:
    """测试防抖更新器"""

    def test_debounce_delays_callback(self, tmp_path: Path):
        """测试防抖延迟回调"""
        callback_called = threading.Event()
        received_files = []

        def callback(files):
            received_files.extend(files)
            callback_called.set()

        updater = DebouncedUpdater(delay=0.5, callback=callback)

        # 触发多个文件变化
        updater.on_file_change(Path("/tmp/file1.py"))
        updater.on_file_change(Path("/tmp/file2.py"))

        # 短时间内不应该触发回调
        assert not callback_called.is_set()

        # 等待延迟时间
        callback_called.wait(timeout=1.0)

        # 回调应该被触发，且包含所有文件
        assert callback_called.is_set()
        assert len(received_files) == 2

        updater.stop()

    def test_debounce_cancels_previous_timer(self):
        """测试防抖取消之前的定时器"""
        call_count = [0]

        def callback(files):
            call_count[0] += 1

        updater = DebouncedUpdater(delay=0.3, callback=callback)

        # 连续触发多次
        for i in range(5):
            updater.on_file_change(Path(f"/tmp/file{i}.py"))
            time.sleep(0.1)

        # 等待延迟
        time.sleep(0.5)

        # 只应该调用一次
        assert call_count[0] == 1

        updater.stop()
