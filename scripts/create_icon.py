# -*- coding: utf-8 -*-
"""生成应用图标"""

from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QPen, QPainterPath, QIcon
from PyQt5.QtCore import Qt
import os

def create_icon():
    """创建应用图标"""
    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 绘制圆角矩形背景
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#00d4ff"))
    gradient.setColorAt(1, QColor("#0099cc"))

    from PyQt5.QtGui import QBrush
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor("#00d4ff"), 4))
    painter.drawRoundedRect(20, 20, size - 40, size - 40, 50, 50)

    # 绘制 C 字母
    painter.setPen(QPen(QColor("#0d1117"), 20, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    path = QPainterPath()
    path.moveTo(160, 70)
    path.cubicTo(80, 70, 80, 186, 160, 186)
    painter.drawPath(path)

    painter.end()
    return pixmap

if __name__ == "__main__":
    # 创建图标
    pixmap = create_icon()

    # 保存为 PNG
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(script_dir), "assets")

    png_path = os.path.join(assets_dir, "icon.png")
    pixmap.save(png_path, "PNG")
    print(f"图标已保存到: {png_path}")

    # 保存为 ICO (需要 Pillow)
    try:
        from PIL import Image
        ico_path = os.path.join(assets_dir, "icon.ico")

        # PyQt5 的 pixmap 不能直接转 PIL，所以先保存 PNG 再转 ICO
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print(f"ICO 图标已保存到: {ico_path}")
    except ImportError:
        print("Pillow 未安装，跳过 ICO 生成")
        print("运行: pip install Pillow")