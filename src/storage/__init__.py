# -*- coding: utf-8 -*-
"""Storage module for backup providers"""

from storage.base import StorageBase
from storage.github_storage import GitHubStorage

__all__ = ['StorageBase', 'GitHubStorage']