# -*- coding: utf-8 -*-
"""登录对话框"""

import webbrowser
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from auth.github_oauth import GitHubOAuth
from auth.token_manager import TokenManager
from utils.config import get_config
from utils.logger import logger


class LoginThread(QThread):
    """登录线程"""
    success = pyqtSignal(str, dict)
    error = pyqtSignal(str)

    def __init__(self, oauth: GitHubOAuth):
        super().__init__()
        self.oauth = oauth

    def run(self):
        try:
            # 获取授权码
            code = self.oauth.start_callback_server(timeout=300)
            if not code:
                self.error.emit("授权超时")
                return

            # 换取 token
            token = self.oauth.exchange_code(code)

            # 获取用户信息
            user_info = self.oauth.get_user_info(token)

            self.success.emit(token, user_info)

        except Exception as e:
            self.error.emit(str(e))


class LoginDialog(QDialog):
    """登录对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.token = None
        self.user_info = None

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("GitHub 登录")
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout(self)

        # 说明
        info_label = QLabel(
            "点击下方按钮将打开浏览器进行 GitHub 授权。\n\n"
            "授权后将自动创建私有仓库用于存储备份。"
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 不确定进度
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # 状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # 按钮
        btn_layout = QHBoxLayout()

        self.login_btn = QPushButton("GitHub 登录")
        self.login_btn.clicked.connect(self._start_login)
        btn_layout.addWidget(self.login_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _start_login(self):
        """开始登录流程"""
        config = get_config()

        client_id = config.get("github.client_id")
        client_secret = config.get("github.client_secret")
        redirect_port = config.get("github.redirect_port", 18080)

        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "配置错误",
                "请先配置 GitHub Client ID 和 Secret"
            )
            return

        self.oauth = GitHubOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_port=redirect_port
        )

        # 打开浏览器
        auth_url = self.oauth.get_authorization_url()
        webbrowser.open(auth_url)

        # 启动登录线程
        self.progress.setVisible(True)
        self.login_btn.setEnabled(False)
        self.status_label.setText("等待授权...")

        self.login_thread = LoginThread(self.oauth)
        self.login_thread.success.connect(self._on_login_success)
        self.login_thread.error.connect(self._on_login_error)
        self.login_thread.start()

    def _on_login_success(self, token: str, user_info: dict):
        """登录成功"""
        self.progress.setVisible(False)
        self.status_label.setText(f"登录成功：{user_info['login']}")

        # 保存 token 和用户信息
        token_manager = TokenManager()
        token_manager.save_token(token)
        token_manager.save_user_info(user_info)

        self.token = token
        self.user_info = user_info

        QMessageBox.information(
            self,
            "登录成功",
            f"欢迎，{user_info['login']}！"
        )

        self.accept()

    def _on_login_error(self, error: str):
        """登录失败"""
        self.progress.setVisible(False)
        self.login_btn.setEnabled(True)
        self.status_label.setText("")

        QMessageBox.critical(self, "登录失败", error)

    def get_user_info(self) -> dict:
        """获取用户信息"""
        return self.user_info