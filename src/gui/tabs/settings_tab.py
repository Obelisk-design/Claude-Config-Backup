# -*- coding: utf-8 -*-
"""设置 Tab"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QGroupBox,
    QMessageBox, QRadioButton, QLabel, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
import webbrowser

from utils.config import get_config
from utils.logger import logger


class SettingsTab(QWidget):
    """设置 Tab 页面"""

    def __init__(self):
        super().__init__()
        self.config = get_config()
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        """初始化 UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1a222d;
                width: 10px;
                border-radius: 5px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #3d4a5c;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00f0ff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        # 滚动内容
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(0, 0, 8, 0)  # 右边留出滚动条空间
        layout.setSpacing(20)

        # GitHub 配置
        github_group = QGroupBox("GitHub OAuth 配置")
        github_layout = QFormLayout(github_group)
        github_layout.setSpacing(16)
        github_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.client_id = QLineEdit()
        self.client_id.setPlaceholderText("GitHub OAuth Client ID")
        self.client_id.setMinimumHeight(36)
        github_layout.addRow("Client ID：", self.client_id)

        self.client_secret = QLineEdit()
        self.client_secret.setEchoMode(QLineEdit.Password)
        self.client_secret.setPlaceholderText("GitHub OAuth Client Secret")
        self.client_secret.setMinimumHeight(36)
        github_layout.addRow("Client Secret：", self.client_secret)

        self.redirect_port = QSpinBox()
        self.redirect_port.setRange(1024, 65535)
        self.redirect_port.setValue(18080)
        self.redirect_port.setMinimumHeight(36)
        github_layout.addRow("回调端口：", self.redirect_port)

        # 帮助按钮
        help_btn = QPushButton("📖 帮助创建 OAuth 应用")
        help_btn.clicked.connect(self._open_github_oauth_help)
        github_layout.addRow("", help_btn)

        layout.addWidget(github_group)

        # SSH 服务器配置
        ssh_group = QGroupBox("SSH 服务器配置")
        ssh_layout = QFormLayout(ssh_group)
        ssh_layout.setSpacing(16)
        ssh_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.ssh_host = QLineEdit()
        self.ssh_host.setPlaceholderText("服务器 IP 地址")
        self.ssh_host.setMinimumHeight(36)
        ssh_layout.addRow("服务器地址：", self.ssh_host)

        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        self.ssh_port.setValue(22)
        self.ssh_port.setMinimumHeight(36)
        ssh_layout.addRow("SSH 端口：", self.ssh_port)

        self.ssh_user = QLineEdit()
        self.ssh_user.setPlaceholderText("用户名")
        self.ssh_user.setMinimumHeight(36)
        ssh_layout.addRow("用户名：", self.ssh_user)

        self.ssh_password = QLineEdit()
        self.ssh_password.setEchoMode(QLineEdit.Password)
        self.ssh_password.setPlaceholderText("密码")
        self.ssh_password.setMinimumHeight(36)
        ssh_layout.addRow("密码：", self.ssh_password)

        test_btn = QPushButton("🔗 测试连接")
        test_btn.clicked.connect(self._test_ssh_connection)
        ssh_layout.addRow("", test_btn)

        layout.addWidget(ssh_group)

        # 存储类型
        storage_group = QGroupBox("存储类型")
        storage_layout = QVBoxLayout(storage_group)
        storage_layout.setSpacing(8)

        self.github_radio = QRadioButton("☁️ GitHub 私有仓库（推荐）")
        self.github_radio.setChecked(True)
        storage_layout.addWidget(self.github_radio)

        self.ssh_radio = QRadioButton("🖥️ SSH 服务器上传")
        storage_layout.addWidget(self.ssh_radio)

        self.local_radio = QRadioButton("📁 仅本地存储")
        storage_layout.addWidget(self.local_radio)

        layout.addWidget(storage_group)

        # 保存按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("✓ 保存设置")
        save_btn.setProperty("primary", True)
        save_btn.setMinimumWidth(160)
        save_btn.setMinimumHeight(44)
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def _load_settings(self):
        """加载设置"""
        self.client_id.setText(self.config.get("github.client_id", ""))
        self.client_secret.setText(self.config.get("github.client_secret", ""))
        self.redirect_port.setValue(self.config.get("github.redirect_port", 18080))
        self.ssh_host.setText(self.config.get("ssh.host", ""))
        self.ssh_port.setValue(self.config.get("ssh.port", 22))
        self.ssh_user.setText(self.config.get("ssh.user", ""))

    def _save_settings(self):
        """保存设置"""
        self.config.set("github.client_id", self.client_id.text())
        self.config.set("github.client_secret", self.client_secret.text())
        self.config.set("github.redirect_port", self.redirect_port.value())
        self.config.set("ssh.host", self.ssh_host.text())
        self.config.set("ssh.port", self.ssh_port.value())
        self.config.set("ssh.user", self.ssh_user.text())
        self.config.save()

        QMessageBox.information(self, "成功", "设置已保存")
        logger.info("用户设置已保存")

    def _test_ssh_connection(self):
        """测试 SSH 连接"""
        host = self.ssh_host.text()
        user = self.ssh_user.text()

        if not host or not user:
            QMessageBox.warning(self, "提示", "请填写服务器地址和用户名")
            return

        QMessageBox.information(self, "提示", "连接测试功能开发中...")

    def _open_github_oauth_help(self):
        """打开 GitHub OAuth 创建帮助"""
        help_text = """<h3>创建 GitHub OAuth 应用</h3>
<ol>
<li>点击"打开设置页面"按钮</li>
<li>点击右上角 <b>New OAuth App</b> 按钮</li>
<li>填写以下信息：
    <ul>
    <li><b>Application name</b>: Claude Config Backup</li>
    <li><b>Homepage URL</b>: http://localhost:18080</li>
    <li><b>Authorization callback URL</b>: http://localhost:18080/callback</li>
    </ul>
</li>
<li>点击 <b>Register application</b></li>
<li>复制 <b>Client ID</b> 填写到上方输入框</li>
<li>点击 <b>Generate a new client secret</b></li>
<li>复制生成的 <b>Client Secret</b> 填写到上方输入框</li>
<li>点击本页面的 <b>保存设置</b> 按钮</li>
</ol>
<p style="color: #ff3366;"><b>注意：</b>Client Secret 只显示一次，请务必复制保存！</p>"""

        msg = QMessageBox(self)
        msg.setWindowTitle("创建 OAuth 应用指南")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.addButton("打开设置页面", QMessageBox.AcceptRole)
        msg.addButton("取消", QMessageBox.RejectRole)

        if msg.exec_() == 0:
            webbrowser.open("https://github.com/settings/developers")
            QMessageBox.information(
                self, "提示",
                "已打开 GitHub 设置页面\n请按照上述步骤创建 OAuth 应用"
            )