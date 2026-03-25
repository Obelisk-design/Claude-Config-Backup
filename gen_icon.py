from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QPen, QPainterPath, QBrush
from PyQt5.QtCore import Qt
import os

size = 256
pixmap = QPixmap(size, size)
pixmap.fill(Qt.transparent)

painter = QPainter(pixmap)
painter.setRenderHint(QPainter.Antialiasing)

gradient = QLinearGradient(0, 0, size, size)
gradient.setColorAt(0, QColor('#00d4ff'))
gradient.setColorAt(1, QColor('#0099cc'))

painter.setBrush(QBrush(gradient))
painter.setPen(QPen(QColor('#00d4ff'), 4))
painter.drawRoundedRect(20, 20, size - 40, size - 40, 50, 50)

painter.setPen(QPen(QColor('#0d1117'), 20, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
path = QPainterPath()
path.moveTo(160, 70)
path.cubicTo(80, 70, 80, 186, 160, 186)
painter.drawPath(path)
painter.end()

assets_dir = 'd:/CodeSpace/claudeFi/assets'
os.makedirs(assets_dir, exist_ok=True)
pixmap.save(f'{assets_dir}/icon.png', 'PNG')
print('PNG icon saved')

# Convert to ICO using Pillow
from PIL import Image
img = Image.open(f'{assets_dir}/icon.png')
img.save(f'{assets_dir}/icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
print('ICO icon saved')