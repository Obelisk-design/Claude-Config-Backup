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
            result = self.oauth.start_callback_server(timeout=300)
            if not result:
                self.error.emit("授权超时或被取消")
                return

            code, state = result

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

        # 优先使用配置中的密钥，如果未配置则使用默认的内置 OAuth App 凭证
        client_id = config.get("github.client_id") or "Iv23li4zWtSAxhLjjEJb"
        client_secret = config.get("github.client_secret") or "6502c846a2ddaf23946644c1e883017969caa0b3"
        redirect_port = config.get("github.redirect_port", 18080)

        # 校验端口是否被占用，提供友好提示
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', redirect_port))
        except OSError:
            QMessageBox.critical(self, "端口被占用", f"回调端口 {redirect_port} 已被占用。\n请在设置中更改端口或关闭占用该端口的程序。")
            return

        self.oauth = GitHubOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_port=redirect_port
        )

        # 启动登录线程
        self.progress.setVisible(True)
        self.login_btn.setEnabled(False)
        self.status_label.setText("等待授权...")

        self.login_thread = LoginThread(self.oauth)
        self.login_thread.success.connect(self._on_login_success)
        self.login_thread.error.connect(self._on_login_error)
        self.login_thread.finished.connect(self.login_thread.deleteLater) # 避免线程对象内存泄漏
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

        # 翻译常见的生硬错误为用户友好文案
        user_friendly_error = error
        if "bad verification code" in error.lower() or "code passed is incorrect" in error.lower():
            user_friendly_error = "授权码已失效或不正确，请重新点击登录进行授权。"
        elif "timed out" in error.lower():
            user_friendly_error = "等待浏览器授权超时，请重试并在浏览器中尽快确认。"
        elif "connection" in error.lower() or "network" in error.lower():
            user_friendly_error = "网络连接失败，请检查您的网络或代理设置。"
        elif "token" in error.lower():
            user_friendly_error = "获取访问令牌失败，可能是授权已被取消，请重试。"

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("登录失败")
        msg_box.setText("GitHub 授权过程中发生错误：")
        msg_box.setInformativeText(user_friendly_error)

        # 将原始错误信息放在详细信息里供折叠查看
        if user_friendly_error != error:
            msg_box.setDetailedText(f"原始错误信息:\n{error}")

        msg_box.setMinimumWidth(400)
        msg_box.setStyleSheet("QLabel{min-width: 300px;}") # 强制拉宽
        msg_box.exec_()

    def get_user_info(self) -> dict:
        """获取用户信息"""
        return self.user_info
