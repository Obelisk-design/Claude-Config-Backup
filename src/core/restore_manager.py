# -*- coding: utf-8 -*-
"""恢复管理器"""

import json
import hashlib
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.exceptions import RestoreError, CorruptedFileError, VersionMismatchError
from utils.logger import logger

# Claude 配置目录
CLAUDE_DIR = Path.home() / ".claude"
# 缓存目录
CACHE_DIR = Path.home() / ".claude-backup" / "cache"
# 回滚目录
ROLLBACK_DIR = Path.home() / ".claude-backup" / "rollback"


class RestoreManager:
    """恢复管理器"""

    # 支持的备份格式版本
    SUPPORTED_VERSIONS = ["1.0"]

    def __init__(self, claude_dir: Path = None, cache_dir: Path = None, rollback_dir: Path = None):
        """初始化恢复管理器

        Args:
            claude_dir: Claude 配置目录，默认为 ~/.claude
            cache_dir: 缓存目录，默认为 ~/.claude-backup/cache
            rollback_dir: 回滚目录，默认为 ~/.claude-backup/rollback
        """
        self.claude_dir = claude_dir or CLAUDE_DIR
        self.cache_dir = cache_dir or CACHE_DIR
        self.rollback_dir = rollback_dir or ROLLBACK_DIR

        # 确保目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rollback_dir.mkdir(parents=True, exist_ok=True)

    def validate_backup(self, backup_path: Path) -> bool:
        """验证备份文件结构

        Args:
            backup_path: 备份文件路径 (.ccb 文件)

        Returns:
            bool: 是否有效

        Raises:
            RestoreError: 备份文件不存在
            CorruptedFileError: 备份文件损坏
        """
        backup_path = Path(backup_path)

        # 检查文件是否存在
        if not backup_path.exists():
            raise RestoreError(f"Backup file not found: {backup_path}")

        # 检查是否为 ZIP 文件
        if not zipfile.is_zipfile(backup_path):
            raise CorruptedFileError(str(backup_path))

        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # 检查必需文件
                required_files = ['manifest.json', 'checksum.json']
                namelist = zf.namelist()

                for required in required_files:
                    if required not in namelist:
                        raise CorruptedFileError(str(backup_path))

                # 验证 manifest.json 格式
                try:
                    manifest_content = zf.read('manifest.json').decode('utf-8')
                    manifest = json.loads(manifest_content)

                    # 检查版本兼容性
                    version = manifest.get('version', '1.0')
                    if version not in self.SUPPORTED_VERSIONS:
                        raise VersionMismatchError(
                            expected='/'.join(self.SUPPORTED_VERSIONS),
                            actual=version
                        )
                except json.JSONDecodeError:
                    raise CorruptedFileError(str(backup_path))

                # 验证 checksum.json 格式
                try:
                    checksum_content = zf.read('checksum.json').decode('utf-8')
                    json.loads(checksum_content)
                except json.JSONDecodeError:
                    raise CorruptedFileError(str(backup_path))

                # 检查 data 目录是否存在
                has_data = any(name.startswith('data/') for name in namelist)
                if not has_data:
                    logger.warning(f"No data directory found in backup: {backup_path}")

            logger.info(f"Backup validation passed: {backup_path}")
            return True

        except zipfile.BadZipFile:
            raise CorruptedFileError(str(backup_path))
        except (RestoreError, CorruptedFileError, VersionMismatchError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating backup: {e}")
            raise RestoreError(f"Failed to validate backup: {e}")

    def extract_manifest(self, backup_path: Path) -> Dict[str, Any]:
        """提取备份文件的 manifest 信息

        Args:
            backup_path: 备份文件路径

        Returns:
            Dict: manifest 内容

        Raises:
            RestoreError: 提取失败
            CorruptedFileError: 文件损坏
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise RestoreError(f"Backup file not found: {backup_path}")

        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                if 'manifest.json' not in zf.namelist():
                    raise CorruptedFileError(str(backup_path))

                manifest_content = zf.read('manifest.json').decode('utf-8')
                manifest = json.loads(manifest_content)
                logger.debug(f"Extracted manifest from {backup_path}")
                return manifest

        except json.JSONDecodeError:
            raise CorruptedFileError(str(backup_path))
        except zipfile.BadZipFile:
            raise CorruptedFileError(str(backup_path))
        except (RestoreError, CorruptedFileError):
            raise
        except Exception as e:
            logger.error(f"Failed to extract manifest: {e}")
            raise RestoreError(f"Failed to extract manifest: {e}")

    def _calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """计算文件哈希值

        Args:
            file_path: 文件路径
            algorithm: 哈希算法

        Returns:
            str: 文件哈希值
        """
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def create_rollback(self, name: str = None) -> Optional[str]:
        """创建回滚点

        Args:
            name: 回滚点名称，默认使用时间戳

        Returns:
            str: 回滚点ID，失败返回 None
        """
        if not self.claude_dir.exists():
            logger.warning(f"Claude directory does not exist: {self.claude_dir}")
            return None

        # 生成回滚点ID
        rollback_id = name or datetime.now().strftime("%Y%m%d_%H%M%S")
        rollback_path = self.rollback_dir / rollback_id

        try:
            # 创建回滚目录
            rollback_path.mkdir(parents=True, exist_ok=True)

            # 复制当前配置到回滚目录
            copied_count = 0
            for item in self.claude_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, rollback_path / item.name)
                    copied_count += 1
                elif item.is_dir():
                    dest = rollback_path / item.name
                    shutil.copytree(item, dest)
                    copied_count += 1

            # 创建回滚元数据
            metadata = {
                "id": rollback_id,
                "created_at": datetime.now().isoformat(),
                "source_dir": str(self.claude_dir),
                "items_count": copied_count
            }
            with open(rollback_path / ".rollback_meta.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Created rollback point: {rollback_id}")
            return rollback_id

        except Exception as e:
            logger.error(f"Failed to create rollback point: {e}")
            # 清理失败的回滚目录
            if rollback_path.exists():
                shutil.rmtree(rollback_path, ignore_errors=True)
            return None

    def list_rollback_points(self) -> List[Dict[str, Any]]:
        """列出所有回滚点

        Returns:
            List[Dict]: 回滚点列表，每个元素包含 id, created_at, items_count 等
        """
        rollback_points = []

        if not self.rollback_dir.exists():
            return rollback_points

        for rollback_dir in self.rollback_dir.iterdir():
            if not rollback_dir.is_dir():
                continue

            meta_file = rollback_dir / ".rollback_meta.json"
            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    rollback_points.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to read rollback metadata: {e}")
                    # 尝试从目录名推断信息
                    rollback_points.append({
                        "id": rollback_dir.name,
                        "created_at": None,
                        "items_count": None
                    })
            else:
                # 没有元数据文件，使用目录信息
                rollback_points.append({
                    "id": rollback_dir.name,
                    "created_at": None,
                    "items_count": None
                })

        # 按创建时间倒序排列
        rollback_points.sort(
            key=lambda x: x.get('created_at') or '',
            reverse=True
        )

        return rollback_points

    def restore(
        self,
        backup_path: Path,
        modules: List[str] = None,
        skip_existing: bool = False,
        create_rollback: bool = True
    ) -> Dict[str, Any]:
        """恢复配置

        Args:
            backup_path: 备份文件路径
            modules: 要恢复的模块列表，None 表示全部
            skip_existing: 是否跳过已存在的文件
            create_rollback: 是否创建回滚点

        Returns:
            Dict: 恢复结果，包含 success, restored_files, skipped_files, errors
        """
        backup_path = Path(backup_path)
        result = {
            "success": False,
            "restored_files": [],
            "skipped_files": [],
            "errors": [],
            "rollback_id": None
        }

        try:
            # 1. 验证备份文件
            self.validate_backup(backup_path)

            # 2. 创建回滚点
            rollback_id = None
            if create_rollback:
                rollback_id = self.create_rollback()
                result["rollback_id"] = rollback_id

            # 3. 提取 manifest
            manifest = self.extract_manifest(backup_path)

            # 4. 解压并恢复文件
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # 获取 data 目录下的文件列表
                data_files = [f for f in zf.namelist() if f.startswith('data/')]

                for file_path in data_files:
                    # 跳过目录
                    if file_path.endswith('/'):
                        continue

                    # 解析模块路径: data/{module_id}/{rel_path}
                    parts = file_path[len('data/'):].split('/', 1)
                    if len(parts) < 2:
                        continue

                    module_id = parts[0]
                    rel_path = parts[1]

                    # 检查是否在指定模块列表中
                    if modules and module_id not in modules:
                        continue

                    # 目标路径
                    target_path = self.claude_dir / rel_path

                    # 检查是否跳过已存在文件
                    if skip_existing and target_path.exists():
                        result["skipped_files"].append(rel_path)
                        logger.debug(f"Skipped existing file: {rel_path}")
                        continue

                    try:
                        # 确保目标目录存在
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # 解压文件
                        content = zf.read(file_path)
                        with open(target_path, 'wb') as f:
                            f.write(content)

                        result["restored_files"].append(rel_path)
                        logger.debug(f"Restored file: {rel_path}")

                    except Exception as e:
                        error_msg = f"Failed to restore {rel_path}: {e}"
                        result["errors"].append(error_msg)
                        logger.error(error_msg)

            # 设置成功标志
            result["success"] = len(result["restored_files"]) > 0

            logger.info(
                f"Restore completed: {len(result['restored_files'])} files restored, "
                f"{len(result['skipped_files'])} skipped, {len(result['errors'])} errors"
            )

        except (RestoreError, CorruptedFileError, VersionMismatchError) as e:
            result["errors"].append(str(e))
            logger.error(f"Restore failed: {e}")

            # 尝试回滚
            if result.get("rollback_id"):
                self._perform_rollback(result["rollback_id"])

        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")
            logger.error(f"Unexpected restore error: {e}")

            # 尝试回滚
            if result.get("rollback_id"):
                self._perform_rollback(result["rollback_id"])

        return result

    def _perform_rollback(self, rollback_id: str) -> bool:
        """执行回滚

        Args:
            rollback_id: 回滚点ID

        Returns:
            bool: 是否成功
        """
        rollback_path = self.rollback_dir / rollback_id

        if not rollback_path.exists():
            logger.error(f"Rollback point not found: {rollback_id}")
            return False

        try:
            # 清空当前配置目录
            if self.claude_dir.exists():
                for item in self.claude_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)

            # 从回滚点恢复
            for item in rollback_path.iterdir():
                if item.name == '.rollback_meta.json':
                    continue
                if item.is_file():
                    shutil.copy2(item, self.claude_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, self.claude_dir / item.name)

            logger.info(f"Rollback completed from: {rollback_id}")
            return True

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def delete_rollback_point(self, rollback_id: str) -> bool:
        """删除回滚点

        Args:
            rollback_id: 回滚点ID

        Returns:
            bool: 是否成功
        """
        rollback_path = self.rollback_dir / rollback_id

        if not rollback_path.exists():
            logger.warning(f"Rollback point not found: {rollback_id}")
            return False

        try:
            shutil.rmtree(rollback_path)
            logger.info(f"Deleted rollback point: {rollback_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete rollback point: {e}")
            return False