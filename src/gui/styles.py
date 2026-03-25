# -*- coding: utf-8 -*-
"""
Claude Config Backup - UI Theme System v2.0
Cyberpunk Terminal Aesthetic

设计理念：
- 终端黑客风格：深色背景、霓虹边框、等宽字体
- 清晰的信息层级：每个区块有明确的视觉边界
- 精致的交互反馈：悬停、焦点、激活状态
"""

# ============================================
# 颜色系统
# ============================================

# 主色调 - 霓虹青
PRIMARY = "#00f0ff"
PRIMARY_DIM = "#00b8c4"
PRIMARY_GLOW = "rgba(0, 240, 255, 0.15)"
PRIMARY_SUBTLE = "rgba(0, 240, 255, 0.05)"

# 语义色
SUCCESS = "#00ff9d"
SUCCESS_DIM = "#00cc7d"
ERROR = "#ff3366"
ERROR_DIM = "#cc2952"
WARNING = "#ffcc00"
INFO = "#00f0ff"

# 背景色 - 深邃黑
BG_BASE = "#0a0e14"
BG_SURFACE = "#111820"
BG_ELEVATED = "#1a222d"
BG_HOVER = "#232d3b"

# 文字色
TEXT_PRIMARY = "#e6edf3"
TEXT_SECONDARY = "#7d8590"
TEXT_MUTED = "#484f58"

# 边框
BORDER_DEFAULT = "#2d3640"
BORDER_MUTED = "#1e252d"
BORDER_GLOW = "rgba(0, 240, 255, 0.4)"

# ============================================
# 尺寸系统
# ============================================

INPUT_HEIGHT = "46px"
BUTTON_HEIGHT = "46px"

RADIUS_SM = "6px"
RADIUS_MD = "10px"
RADIUS_LG = "14px"

# ============================================
# 全局样式
# ============================================

MAIN_STYLE = f"""
/* ========== 全局基础 ========== */
* {{
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", "Consolas", monospace;
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
    padding: 20px;
}}

QTabBar {{
    background-color: transparent;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    padding: 14px 28px;
    margin-right: 2px;
    border-top-left-radius: {RADIUS_MD};
    border-top-right-radius: {RADIUS_MD};
    font-weight: 600;
    font-size: 13px;
    min-width: 110px;
    min-height: 20px;
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
    border-bottom: 2px solid {PRIMARY};
}}

/* ========== 分组框 ========== */
QGroupBox {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_LG};
    margin-top: 28px;
    padding: 28px 24px 24px 24px;
    font-weight: 600;
    font-size: 14px;
    color: {TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 24px;
    top: 2px;
    padding: 0 12px;
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
    background-color: {BG_BASE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 0 16px;
    min-height: {INPUT_HEIGHT};
    height: {INPUT_HEIGHT};
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY};
    selection-color: {BG_BASE};
    font-size: 13px;
}}

QLineEdit:hover {{
    border-color: {TEXT_MUTED};
}}

QLineEdit:focus {{
    border: 2px solid {PRIMARY};
    padding: 0 15px;
    background-color: {BG_SURFACE};
}}

QLineEdit:disabled {{
    background-color: {BG_ELEVATED};
    color: {TEXT_MUTED};
    border-color: {BORDER_MUTED};
}}

QLineEdit::placeholder {{
    color: {TEXT_MUTED};
}}

/* ========== 数字输入框 ========== */
QSpinBox {{
    background-color: {BG_BASE};
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
    border: 2px solid {PRIMARY};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BG_ELEVATED};
    border: none;
    width: 30px;
    subcontrol-origin: border;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {PRIMARY};
}}

/* ========== 复选框 ========== */
QCheckBox {{
    spacing: 14px;
    min-height: 52px;
    padding: 14px 18px;
    color: {TEXT_PRIMARY};
    background-color: transparent;
    border-radius: {RADIUS_MD};
}}

QCheckBox:hover {{
    background-color: {BG_ELEVATED};
}}

QCheckBox::indicator {{
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid {BORDER_DEFAULT};
    background-color: {BG_BASE};
}}

QCheckBox::indicator:hover {{
    border-color: {PRIMARY};
}}

QCheckBox::indicator:checked {{
    background-color: {PRIMARY};
    border-color: {PRIMARY};
}}

QCheckBox::indicator:disabled {{
    background-color: {BG_ELEVATED};
    border-color: {BORDER_MUTED};
}}

/* ========== 单选按钮 ========== */
QRadioButton {{
    spacing: 14px;
    min-height: 52px;
    padding: 14px 18px;
    color: {TEXT_PRIMARY};
    background-color: transparent;
    border-radius: {RADIUS_MD};
}}

QRadioButton:hover {{
    background-color: {BG_ELEVATED};
}}

QRadioButton::indicator {{
    width: 22px;
    height: 22px;
    border-radius: 11px;
    border: 2px solid {BORDER_DEFAULT};
    background-color: {BG_BASE};
}}

QRadioButton::indicator:hover {{
    border-color: {PRIMARY};
}}

QRadioButton::indicator:checked {{
    border: 6px solid {PRIMARY};
    background-color: {BG_BASE};
}}

/* ========== 下拉框 ========== */
QComboBox {{
    background-color: {BG_BASE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 0 16px;
    min-height: {INPUT_HEIGHT};
    height: {INPUT_HEIGHT};
    color: {TEXT_PRIMARY};
    min-width: 150px;
}}

QComboBox:hover {{
    border-color: {TEXT_MUTED};
}}

QComboBox:focus {{
    border-color: {PRIMARY};
}}

QComboBox::drop-down {{
    border: none;
    width: 40px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 8px;
    selection-background-color: {BG_ELEVATED};
    selection-color: {PRIMARY};
    outline: none;
}}

/* ========== 列表 ========== */
QListWidget {{
    background-color: {BG_BASE};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 8px;
    outline: none;
}}

QListWidget::item {{
    background-color: transparent;
    border-radius: {RADIUS_SM};
    padding: 14px 18px;
    margin: 2px 0;
    min-height: 20px;
}}

QListWidget::item:hover {{
    background-color: {BG_ELEVATED};
}}

QListWidget::item:selected {{
    background-color: {BG_ELEVATED};
    border: 1px solid {PRIMARY};
    color: {PRIMARY};
}}

/* ========== 按钮 ========== */
QPushButton {{
    background-color: {BG_ELEVATED};
    border: 1px solid {BORDER_DEFAULT};
    border-radius: {RADIUS_MD};
    padding: 0 24px;
    min-height: {BUTTON_HEIGHT};
    height: {BUTTON_HEIGHT};
    color: {TEXT_PRIMARY};
    font-weight: 600;
    font-size: 13px;
    min-width: 120px;
}}

QPushButton:hover {{
    background-color: {BG_HOVER};
    border-color: {TEXT_MUTED};
}}

QPushButton:pressed {{
    background-color: {PRIMARY};
    color: {BG_BASE};
    border-color: {PRIMARY};
}}

QPushButton:disabled {{
    background-color: {BG_ELEVATED};
    color: {TEXT_MUTED};
    border-color: {BORDER_MUTED};
}}

/* 主要按钮 */
QPushButton[primary="true"] {{
    background-color: {PRIMARY};
    border-color: {PRIMARY};
    color: {BG_BASE};
}}

QPushButton[primary="true"]:hover {{
    background-color: {PRIMARY_DIM};
    border-color: {PRIMARY_DIM};
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
    background-color: {PRIMARY_SUBTLE};
}}

/* 成功按钮 */
QPushButton[success="true"] {{
    background-color: transparent;
    border-color: {SUCCESS};
    color: {SUCCESS};
}}

QPushButton[success="true"]:hover {{
    background-color: rgba(0, 255, 157, 0.12);
}}

/* 危险按钮 */
QPushButton[danger="true"] {{
    background-color: transparent;
    border-color: {ERROR};
    color: {ERROR};
}}

QPushButton[danger="true"]:hover {{
    background-color: rgba(255, 51, 102, 0.12);
}}

/* ========== 进度条 ========== */
QProgressBar {{
    background-color: {BG_ELEVATED};
    border: none;
    border-radius: 4px;
    height: 10px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {PRIMARY}, stop:1 {SUCCESS});
    border-radius: 4px;
}}

/* ========== 滚动条 - 隐藏 ========== */
QScrollBar:vertical {{
    background-color: transparent;
    width: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: transparent;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: transparent;
}}

/* ========== 消息框 ========== */
QMessageBox {{
    background-color: {BG_SURFACE};
}}

QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
    min-width: 200px;
}}

QMessageBox QPushButton {{
    min-width: 100px;
}}

/* ========== 工具提示 ========== */
QToolTip {{
    background-color: {BG_ELEVATED};
    border: 1px solid {PRIMARY};
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
    padding: 12px 20px;
    margin: 2px 0;
}}

QMenu::item:selected {{
    background-color: {BG_ELEVATED};
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
    font-size: 18px;
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
    min-height: 72px;
}}

QLabel#appTitle {{
    font-size: 17px;
    font-weight: 700;
    color: {PRIMARY};
    letter-spacing: 1px;
}}

QLabel#userLabel {{
    color: {TEXT_SECONDARY};
    font-size: 13px;
    padding: 0 8px;
}}

QPushButton#loginBtn {{
    background-color: transparent;
    border: 2px solid {PRIMARY};
    color: {PRIMARY};
    font-weight: 600;
}}

QPushButton#loginBtn:hover {{
    background-color: {PRIMARY_GLOW};
}}

QPushButton#logoutBtn {{
    background-color: transparent;
    border: 1px solid {BORDER_DEFAULT};
    color: {TEXT_SECONDARY};
}}

QPushButton#logoutBtn:hover {{
    border-color: {ERROR};
    color: {ERROR};
    background-color: rgba(255, 51, 102, 0.1);
}}
"""

STATUS_BAR_STYLE = f"""
QStatusBar {{
    background-color: {BG_SURFACE};
    border-top: 1px solid {BORDER_DEFAULT};
    color: {TEXT_MUTED};
    font-size: 12px;
    padding: 8px 20px;
    min-height: 32px;
}}
"""

AD_BAR_STYLE = f"""
QFrame#adBar {{
    background-color: {BG_ELEVATED};
    border-top: 1px solid {BORDER_DEFAULT};
    min-height: 52px;
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
    font-size: 56px;
    color: {TEXT_MUTED};
}}

QLabel#emptyTitle {{
    font-size: 18px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

QLabel#emptyDesc {{
    font-size: 14px;
    color: {TEXT_SECONDARY};
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


def get_card_style():
    """获取卡片样式"""
    return CARD_STYLE