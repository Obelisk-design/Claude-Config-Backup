# -*- coding: utf-8 -*-
"""Storage base class for backup providers"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class StorageBase(ABC):
    """Abstract base class for storage providers"""

    @abstractmethod
    def upload(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to remote storage

        Args:
            local_path: Path to the local file
            remote_path: Path where the file should be stored remotely

        Returns:
            True if upload was successful

        Raises:
            BackupError: If upload fails
        """
        pass

    @abstractmethod
    def download(self, remote_path: str, local_path: str) -> bool:
        """Download a file from remote storage

        Args:
            remote_path: Path to the remote file
            local_path: Path where the file should be saved locally

        Returns:
            True if download was successful

        Raises:
            RestoreError: If download fails
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in remote storage

        Args:
            prefix: Optional prefix to filter files

        Returns:
            List of file paths in remote storage
        """
        pass

    @abstractmethod
    def delete(self, remote_path: str) -> bool:
        """Delete a file from remote storage

        Args:
            remote_path: Path to the remote file

        Returns:
            True if deletion was successful

        Raises:
            BackupError: If deletion fails
        """
        pass

    @abstractmethod
    def get_file_url(self, remote_path: str) -> Optional[str]:
        """Get the URL for a remote file

        Args:
            remote_path: Path to the remote file

        Returns:
            URL to access the file, or None if not available
        """
        pass