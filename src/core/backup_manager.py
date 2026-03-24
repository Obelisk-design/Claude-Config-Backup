# -*- coding: utf-8 -*-
"""备份管理器"""

import json
import hashlib
import zipfile
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from core.module_loader import ModuleLoader, CLAUDE_DIR
from security.sensitive_filter import SensitiveFilter
from core.exceptions import BackupError
from utils.logger import logger


# 缓存目录
CACHE_DIR = Path.home() / ".claude-backup" / "cache"


class BackupManager:
    """备份管理器"""

    def __init__(self):
        self.module_loader = ModuleLoader()
        self.sensitive_filter = SensitiveFilter()
        self.app_version = self._get_app_version()

    def _get_app_version(self) -> str:
        """获取应用版本"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
            if config_path.exists():
                import yaml
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
                return config.get("app", {}).get("version", "1.0.0")
        except Exception:
            pass
        return "1.0.0"

    def _generate_backup_id(self) -> str:
        """生成备份ID，格式：YYYYMMDD_HHMMSS"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _collect_files(self, module_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """收集要备份的文件

        Args:
            module_ids: 模块ID列表

        Returns:
            字典，key为模块ID，value为文件信息列表
        """
        collected = {}

        for module_id in module_ids:
            module = self.module_loader.get_module_by_id(module_id)
            if not module:
                logger.warning(f"模块未找到: {module_id}")
                continue

            paths = self.module_loader.resolve_paths(module)
            files = []

            for path in paths:
                try:
                    stat = path.stat()
                    rel_path = path.relative_to(CLAUDE_DIR)
                    files.append({
                        "path": str(rel_path),
                        "full_path": str(path),
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                    })
                except Exception as e:
                    logger.warning(f"无法访问文件 {path}: {e}")

            collected[module_id] = files
            logger.debug(f"模块 {module_id} 收集到 {len(files)} 个文件")

        return collected

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件的SHA256哈希值"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希失败 {file_path}: {e}")
            return ""

    def _filter_sensitive_content(self, file_path: Path) -> Optional[Any]:
        """过滤文件中的敏感信息

        Args:
            file_path: 文件路径

        Returns:
            过滤后的内容，如果不是JSON文件则返回None
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 尝试解析为JSON
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    return self.sensitive_filter.filter(data)
            except json.JSONDecodeError:
                pass

            return None
        except Exception as e:
            logger.warning(f"读取文件失败 {file_path}: {e}")
            return None

    def _create_manifest(
        self,
        backup_id: str,
        username: str,
        description: str,
        modules: List[str],
        total_files: int,
        total_size: int
    ) -> Dict[str, Any]:
        """创建清单文件内容

        Args:
            backup_id: 备份ID
            username: 用户名
            description: 备份描述
            modules: 模块列表
            total_files: 总文件数
            total_size: 总大小

        Returns:
            清单字典
        """
        return {
            "version": "1.0",
            "app_version": self.app_version,
            "backup_id": backup_id,
            "created_at": datetime.now().isoformat(),
            "username": username,
            "description": description,
            "modules": modules,
            "total_files": total_files,
            "total_size": total_size,
            "platform": platform.system().lower(),
        }

    def _create_snapshot(
        self,
        backup_id: str,
        files_by_module: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """创建快照文件内容

        Args:
            backup_id: 备份ID
            files_by_module: 按模块分组的文件信息

        Returns:
            快照字典
        """
        modules_info = {}

        for module_id, files in files_by_module.items():
            files_info = []
            for file_info in files:
                full_path = Path(file_info["full_path"])
                file_hash = self._calculate_file_hash(full_path)
                files_info.append({
                    "path": file_info["path"],
                    "size": file_info["size"],
                    "hash": file_hash,
                    "mtime": file_info["mtime"],
                })
            modules_info[module_id] = {
                "files": files_info,
                "count": len(files_info),
            }

        return {
            "backup_id": backup_id,
            "modules": modules_info,
        }

    def _create_checksum(
        self,
        files_by_module: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, str]:
        """创建校验文件内容

        Args:
            files_by_module: 按模块分组的文件信息

        Returns:
            校验字典，key为文件路径，value为哈希值
        """
        checksums = {}

        for module_id, files in files_by_module.items():
            for file_info in files:
                full_path = Path(file_info["full_path"])
                file_hash = self._calculate_file_hash(full_path)
                if file_hash:
                    # 使用 data/{module_id}/{rel_path} 格式作为key
                    rel_path = file_info["path"]
                    archive_path = f"data/{module_id}/{rel_path}"
                    checksums[archive_path] = file_hash

        return checksums

    def get_preview(self, module_ids: List[str]) -> Dict[str, Any]:
        """获取备份预览信息

        Args:
            module_ids: 模块ID列表

        Returns:
            预览信息字典
        """
        files_by_module = self._collect_files(module_ids)

        total_files = 0
        total_size = 0
        modules_info = []

        for module_id, files in files_by_module.items():
            module = self.module_loader.get_module_by_id(module_id)
            module_size = sum(f["size"] for f in files)
            module_files = len(files)

            total_files += module_files
            total_size += module_size

            modules_info.append({
                "id": module_id,
                "name": module["name"] if module else module_id,
                "files": module_files,
                "size": module_size,
            })

        return {
            "modules": modules_info,
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    def create_backup(
        self,
        module_ids: List[str],
        description: str = "",
        username: str = "",
        include_sensitive: bool = False,
        output_path: Optional[Path] = None
    ) -> Tuple[str, Path]:
        """创建备份文件

        Args:
            module_ids: 要备份的模块ID列表
            description: 备份描述
            username: 用户名
            include_sensitive: 是否包含敏感信息
            output_path: 输出路径，默认使用缓存目录

        Returns:
            (backup_id, backup_file_path)

        Raises:
            BackupError: 备份失败时抛出
        """
        try:
            # 生成备份ID
            backup_id = self._generate_backup_id()

            # 收集文件
            files_by_module = self._collect_files(module_ids)

            if not files_by_module:
                raise BackupError("没有可备份的文件")

            # 计算统计信息
            total_files = sum(len(files) for files in files_by_module.values())
            total_size = sum(
                sum(f["size"] for f in files)
                for files in files_by_module.values()
            )

            # 创建清单
            manifest = self._create_manifest(
                backup_id=backup_id,
                username=username,
                description=description,
                modules=list(files_by_module.keys()),
                total_files=total_files,
                total_size=total_size
            )

            # 创建快照
            snapshot = self._create_snapshot(backup_id, files_by_module)

            # 创建校验
            checksums = self._create_checksum(files_by_module)

            # 确定输出路径
            if output_path is None:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                output_path = CACHE_DIR / f"{backup_id}.ccb"
            else:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建ZIP文件
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # 写入清单
                zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

                # 写入快照
                zf.writestr("snapshot.json", json.dumps(snapshot, indent=2, ensure_ascii=False))

                # 写入校验
                zf.writestr("checksum.json", json.dumps(checksums, indent=2, ensure_ascii=False))

                # 写入数据文件
                for module_id, files in files_by_module.items():
                    for file_info in files:
                        full_path = Path(file_info["full_path"])
                        rel_path = file_info["path"]
                        archive_path = f"data/{module_id}/{rel_path}"

                        # 处理敏感信息过滤
                        if not include_sensitive:
                            filtered_content = self._filter_sensitive_content(full_path)
                            if filtered_content is not None:
                                # 使用过滤后的内容
                                zf.writestr(
                                    archive_path,
                                    json.dumps(filtered_content, indent=2, ensure_ascii=False)
                                )
                                continue

                        # 直接复制文件
                        zf.write(full_path, archive_path)

            logger.info(f"备份创建成功: {output_path}, 文件数: {total_files}, 大小: {total_size} bytes")
            return backup_id, output_path

        except BackupError:
            raise
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            raise BackupError(f"创建备份失败: {e}")