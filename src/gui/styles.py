# -*- coding: utf-8 -*-
"""
Claude Config Backup - UI Theme System v3.0
Fresh Garden Aesthetic

设计理念：
- 清新自然：森林绿主色调，搭配薄荷绿和暖色调
- 舒适阅读：柔和的色彩对比，减少视觉疲劳
- 现代简洁：圆角卡片式设计，层次分明
"""

# ============================================
# 颜色系统 - 森林花园调色板
# ============================================

# 主色调 - 森林绿
PRIMARY = "#2d6a4f"
PRIMARY_LIGHT = "#40916c"
PRIMARY_LIGHTER = "#52b788"
PRIMARY_PALE = "#d8f3dc"
PRIMARY_GLOW = "rgba(45, 106, 79, 0.12)"

# 语义色
SUCCESS = "#2d6a4f"
SUCCESS_LIGHT = "#52b788"
ERROR = "#c44536"
ERROR_LIGHT = "#e07a5f"
WARNING = "#d4a373"
INFO = "#457b9d"

# 背景色 - 温暖米白
BG_BASE = "#faf8f5"
BG_SURFACE = "#ffffff"
BG_ELEVATED = "#f4f1eb"
BG_HOVER = "#ebe7df"

# 文字色
TEXT_PRIMARY = "#1b3a2f"
TEXT_SECONDARY = "#4a6c5c"
TEXT_MUTED = "#7a9988"

# 边框
BORDER_DEFAULT = "#e2ddd5"
BORDER_LIGHT = "#ebe7df"
BORDER_FOCUS = "#40916c"

# 点缀色
ACCENT_WARM = "#e07a5f"
ACCENT_GOLD = "#d4a373"
ACCENT_SKY = "#89c2d9"

# ============================================
# 尺寸系统
# ============================================

INPUT_HEIGHT = "44px"
BUTTON_HEIGHT = "44px"

RADIUS_SM = "8px"
RADIUS_MD = "12px"
RADIUS_LG = "18px"

# ============================================
# 全局样式
# ============================================

MAIN_STYLE = f"""
/* ========== 全局基础 ========== */
* {{
    font-family: "Microsoft YaHei UI", "Segoe UI", "PingFang SC", sans-serif;
}}

QWidget {{
    font-size: 13px;
    color: {TEXT_PRIMARY};
    background-color: transparent;
}}

QMainWindow {{
    background-color: {BG_BASE};
}}

/* ========== 滚动区域 ========== */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* ========== 标签页 ========== */
QTabWidget {{
    background-color: transparent;
}}

QTabWidget::pane {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_LG};
    margin-top: -1px;
    padding: 24px;
}}

QTabBar {{
    background-color: transparent;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: {RADIUS_MD};
    border-top-right-radius: {RADIUS_MD};
    font-weight: 500;
    font-size: 13px;
    min-width: 100px;
    min-height: 18px;
    border: 1px solid transparent;
    border-bottom: none;
}}

QTabBar::tab:hover {{
    background-color: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
}}

QTabBar::tab:selected {{
    background-color: {BG_SURFACE};
    color: {PRIMARY};
    border: 1px solid {BORDER_DEFAULT};
    border-bottom: 3px solid {PRIMARY};
}}

/* ========== 分组框 ========== */
QGroupBox {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_LG};
    margin-top: 24px;
    padding: 28px 24px 24px 24px;
    font-weight: 600;
    font-size: 14px;
    color: {TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 20px;
    top: 2px;
    padding: 0 10px;
    background-color: {BG_SURFACE};
    color: {PRIMARY};
}}

/* ========== 标签 ========== */
QLabel {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
    padding: 0;
}}

/* ========== 输入框 ========== */
QLineEdit {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 0 16px;
    min-height: {INPUT_HEIGHT};
    height: {INPUT_HEIGHT};
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY_LIGHTER};
    selection-color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QLineEdit:hover {{
    border-color: {TEXT_MUTED};
    background-color: {BG_ELEVATED};
}}

QLineEdit:focus {{
    border: 2px solid {BORDER_FOCUS};
    padding: 0 15px;
    background-color: {BG_SURFACE};
}}

QLineEdit:disabled {{
    background-color: {BG_ELEVATED};
    color: {TEXT_MUTED};
    border-color: {BORDER_LIGHT};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

/* ========== 数字输入框 ========== */
QSpinBox {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 0 16px;
    min-height: {INPUT_HEIGHT};
    height: {INPUT_HEIGHT};
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QSpinBox:hover {{
    border-color: {TEXT_MUTED};
}}

QSpinBox:focus {{
    border: 2px solid {BORDER_FOCUS};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BG_ELEVATED};
    border: none;
    width: 28px;
    subcontrol-origin: border;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {PRIMARY_LIGHTER};
}}

/* ========== 文本编辑框 ========== */
QTextEdit {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 12px 16px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QTextEdit:hover {{
    border-color: {TEXT_MUTED};
}}

QTextEdit:focus {{
    border: 2px solid {BORDER_FOCUS};
}}

/* ========== 复选框 ========== */
QCheckBox {{
    spacing: 12px;
    min-height: 48px;
    padding: 12px 16px;
    color: {TEXT_PRIMARY};
    background-color: transparent;
    border-radius: {RADIUS_MD};
}}

QCheckBox:hover {{
    background-color: {BG_ELEVATED};
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 2px solid {BORDER_DEFAULT};
    background-color: {BG_SURFACE};
}}

QCheckBox::indicator:hover {{
    border-color: {PRIMARY_LIGHT};
}}

QCheckBox::indicator:checked {{
    background-color: {PRIMARY};
    border-color: {PRIMARY};
}}

QCheckBox::indicator:disabled {{
    background-color: {BG_ELEVATED};
    border-color: {BORDER_LIGHT};
}}

/* ========== 单选按钮 ========== */
QRadioButton {{
    spacing: 12px;
    min-height: 48px;
    padding: 12px 16px;
    color: {TEXT_PRIMARY};
    background-color: transparent;
    border-radius: {RADIUS_MD};
}}

QRadioButton:hover {{
    background-color: {BG_ELEVATED};
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid {BORDER_DEFAULT};
    background-color: {BG_SURFACE};
}}

QRadioButton::indicator:hover {{
    border-color: {PRIMARY_LIGHT};
}}

QRadioButton::indicator:checked {{
    border: 5px solid {PRIMARY};
    background-color: {BG_SURFACE};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 0 16px;
    min-height: {INPUT_HEIGHT};
    height: {INPUT_HEIGHT};
    color: {TEXT_PRIMARY};
    min-width: 140px;
}}

QComboBox:hover {{
    border-color: {TEXT_MUTED};
    background-color: {BG_ELEVATED};
}}

QComboBox:focus {{
    border-color: {BORDER_FOCUS};
}}

QComboBox::drop-down {{
    border: none;
    width: 36px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 8px;
    selection-background-color: {PRIMARY_PALE};
    selection-color: {PRIMARY};
    outline: none;
}}

/* ========== 列表 ========== */
QListWidget {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 8px;
    outline: none;
}}

QListWidget::item {{
    background-color: transparent;
    border-radius: {RADIUS_SM};
    padding: 12px 16px;
    margin: 2px 0;
    min-height: 18px;
}}

QListWidget::item:hover {{
    background-color: {BG_ELEVATED};
}}

QListWidget::item:selected {{
    background-color: {PRIMARY_PALE};
    border: 1px solid {PRIMARY_LIGHT};
    color: {PRIMARY};
}}

/* ========== 按钮 ========== */
QPushButton {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 0 24px;
    min-height: {BUTTON_HEIGHT};
    height: {BUTTON_HEIGHT};
    color: {TEXT_PRIMARY};
    font-weight: 500;
    font-size: 13px;
    min-width: 110px;
}}

QPushButton:hover {{
    background-color: {BG_ELEVATED};
    border-color: {TEXT_MUTED};
}}

QPushButton:pressed {{
    background-color: {PRIMARY_LIGHTER};
    color: {BG_BASE};
    border-color: {PRIMARY_LIGHTER};
}}

QPushButton:disabled {{
    background-color: {BG_ELEVATED};
    color: {TEXT_MUTED};
    border-color: {BORDER_LIGHT};
}}

/* 主要按钮 */
QPushButton[primary="true"] {{
    background-color: {PRIMARY};
    border-color: {PRIMARY};
    color: white;
}}

QPushButton[primary="true"]:hover {{
    background-color: {PRIMARY_LIGHT};
    border-color: {PRIMARY_LIGHT};
}}

QPushButton[primary="true"]:pressed {{
    background-color: {PRIMARY_LIGHTER};
}}

/* 次要按钮 */
QPushButton[secondary="true"] {{
    background-color: transparent;
    border-color: {BORDER_DEFAULT};
    color: {TEXT_SECONDARY};
}}

QPushButton[secondary="true"]:hover {{
    border-color: {PRIMARY};
    color: {PRIMARY};
    background-color: {PRIMARY_PALE};
}}

/* 成功按钮 */
QPushButton[success="true"] {{
    background-color: transparent;
    border-color: {SUCCESS};
    color: {SUCCESS};
}}

QPushButton[success="true"]:hover {{
    background-color: {PRIMARY_PALE};
}}

/* 危险按钮 */
QPushButton[danger="true"] {{
    background-color: transparent;
    border-color: {ERROR};
    color: {ERROR};
}}

QPushButton[danger="true"]:hover {{
    background-color: rgba(196, 69, 54, 0.08);
}}

/* ========== 进度条 ========== */
QProgressBar {{
    background-color: {BG_ELEVATED};
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY_LIGHT}, stop:1 {PRIMARY_LIGHTER});
    border-radius: 6px;
}}

/* ========== 滚动条 ========== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 4px 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {BORDER_DEFAULT};
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    margin: 2px 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: {BORDER_DEFAULT};
    border-radius: 4px;
    min-width: 40px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {TEXT_MUTED};
}}

/* ========== 消息框 ========== */
QMessageBox {{
    background-color: {BG_SURFACE};
}}

QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
    min-width: 220px;
}}

QMessageBox QPushButton {{
    min-width: 90px;
}}

/* ========== 工具提示 ========== */
QToolTip {{
    background-color: {BG_SURFACE};
    border: 1px solid {PRIMARY_LIGHT};
    border-radius: {RADIUS_SM};
    padding: 8px 14px;
    color: {TEXT_PRIMARY};
}}

/* ========== 菜单 ========== */
QMenu {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 8px;
}}

QMenu::item {{
    background-color: transparent;
    border-radius: {RADIUS_SM};
    padding: 10px 18px;
    margin: 2px 0;
}}

QMenu::item:selected {{
    background-color: {PRIMARY_PALE};
    color: {PRIMARY};
}}

QMenu::separator {{
    height: 1px;
    background-color: {BORDER_DEFAULT};
    margin: 4px 8px;
}}

/* ========== 空状态样式 ========== */
QLabel#emptyIcon {{
    font-size: 48px;
    color: {TEXT_MUTED};
}}

QLabel#emptyTitle {{
    font-size: 17px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel#emptyDesc {{
    font-size: 14px;
    color: {TEXT_SECONDARY};
}}
"""

# ============================================
# 组件特定样式
# ============================================

USER_BAR_STYLE = f"""
QFrame#userBar {{
    background-color: {BG_SURFACE};
    border-bottom: 1px solid {BORDER_DEFAULT};
    min-height: 68px;
}}

QLabel#appTitle {{
    font-size: 16px;
    font-weight: 600;
    color: {PRIMARY};
}}

QLabel#userLabel {{
    color: {TEXT_SECONDARY};
    font-size: 13px;
    padding: 0 8px;
}}

QPushButton#loginBtn {{
    background-color: {PRIMARY};
    border: none;
    color: white;
    font-weight: 500;
}}

QPushButton#loginBtn:hover {{
    background-color: {PRIMARY_LIGHT};
}}

QPushButton#logoutBtn {{
    background-color: transparent;
    border: 1px solid {BORDER_DEFAULT};
    color: {TEXT_SECONDARY};
}}

QPushButton#logoutBtn:hover {{
    border-color: {ERROR};
    color: {ERROR};
    background-color: rgba(196, 69, 54, 0.06);
}}
"""

STATUS_BAR_STYLE = f"""
QStatusBar {{
    background-color: {BG_SURFACE};
    border-top: 1px solid {BORDER_DEFAULT};
    color: {TEXT_MUTED};
    font-size: 12px;
    padding: 8px 20px;
    min-height: 30px;
}}
"""

AD_BAR_STYLE = f"""
QFrame#adBar {{
    background-color: {BG_ELEVATED};
    border-top: 1px solid {BORDER_DEFAULT};
    min-height: 48px;
}}

QLabel#adLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
"""

EMPTY_STATE_STYLE = f"""
QFrame#emptyState {{
    background-color: transparent;
}}

QLabel#emptyIcon {{
    font-size: 52px;
    color: {TEXT_MUTED};
}}

QLabel#emptyTitle {{
    font-size: 17px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel#emptyDesc {{
    font-size: 14px;
    color: {TEXT_SECONDARY};
}}
"""

# 侧边栏样式
SIDEBAR_STYLE = f"""
QFrame#sidebar {{
    background-color: {BG_SURFACE};
    border-right: 1px solid {BORDER_DEFAULT};
    min-width: 200px;
    max-width: 220px;
}}

QLabel#logoText {{
    font-size: 15px;
    font-weight: 600;
    color: {PRIMARY};
    padding: 16px 20px;
}}

QPushButton#navBtn {{
    background-color: transparent;
    border: none;
    border-radius: {RADIUS_SM};
    padding: 14px 20px;
    text-align: left;
    color: {TEXT_SECONDARY};
    font-size: 13px;
    font-weight: 500;
}}

QPushButton#navBtn:hover {{
    background-color: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
}}

QPushButton#navBtn:checked {{
    background-color: {PRIMARY_PALE};
    color: {PRIMARY};
    border-left: 3px solid {PRIMARY};
}}

QLabel#storageLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    padding: 8px 20px;
}}

QLabel#userLabel {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
    padding: 4px 20px;
}}
"""

# 卡片样式 - 用于设置页面等
CARD_STYLE = f"""
QFrame {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_LG};
}}
"""


def get_app_style():
    """获取应用主样式"""
    return MAIN_STYLE


def get_user_bar_style():
    """获取用户栏样式"""
    return USER_BAR_STYLE


def get_status_bar_style():
    """获取状态栏样式"""
    return STATUS_BAR_STYLE


def get_ad_bar_style():
    """获取广告栏样式"""
    return AD_BAR_STYLE


def get_empty_state_style():
    """获取空状态样式"""
    return EMPTY_STATE_STYLE


def get_sidebar_style():
    """获取侧边栏样式"""
    return SIDEBAR_STYLE


def get_card_style():
    """获取卡片样式"""
    return CARD_STYLE