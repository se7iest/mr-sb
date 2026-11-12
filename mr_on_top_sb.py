import os
import sys
import time
import math
import random
import threading
from collections import deque

import requests

from PyQt6.QtCore import (
    Qt, QObject, pyqtSignal, QTimer, QPointF, QRectF, QRect, QPropertyAnimation,
    QEasingCurve
)
from PyQt6.QtGui import (
    QColor, QPainter, QPainterPath, QRadialGradient, QPen, QBrush, QFont,
    QCursor, QLinearGradient, QConicalGradient, QFontMetrics, QIcon, QPixmap
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTabWidget, QTextEdit, QInputDialog, QMessageBox, QFrame,
    QGraphicsOpacityEffect
)

PASSWORD = "mrontop"
VANITY = "discord.gg/mrontop"
CREDIT = "Made By @se7iest"
ICON_FILE = "icon.webp"


def icon_path():
    dirs = []
    if getattr(sys, "frozen", False):
        dirs.append(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))
        dirs.append(os.path.dirname(sys.executable))
    dirs.append(os.path.dirname(os.path.abspath(__file__)))
    dirs.append(os.getcwd())
    for d in dirs:
        cand = os.path.join(d, ICON_FILE)
        if os.path.exists(cand):
            return cand
    return None

P = {
    "void": "#030912",
    "deep": "#061024",
    "blue": "#2f7dff",
    "blue_soft": "#8fbcff",
    "cyan": "#4fd8ff",
    "white": "#ffffff",
    "text": "#e8f0ff",
    "muted": "#7688ab",
    "green": "#4ade80",
    "amber": "#f7c85a",
    "red": "#ff5d7a",
}

STYLE = f"""
QWidget {{
    background: transparent;
    color: {P['text']};
    font-family: 'Segoe UI', 'Consolas', sans-serif;
    font-size: 13px;
}}
#wbtn {{
    background: rgba(255,255,255,16);
    color: {P['blue_soft']};
    border: none;
    border-radius: 8px;
    font-size: 14px;
}}
#wbtn:hover {{ background: rgba(47,125,255,190); color: white; }}
#closebtn:hover {{ background: {P['red']}; color: white; }}

QLabel#field {{ color: {P['blue_soft']}; letter-spacing: 3px; font-size: 10px; font-weight: 700; }}
QLineEdit {{
    background: rgba(255,255,255,14);
    border: 1px solid rgba(47,125,255,80);
    border-radius: 10px;
    padding: 9px 12px;
    color: #f4f9ff;
    selection-background-color: {P['blue']};
}}
QLineEdit:hover {{ border: 1px solid rgba(143,188,255,150); }}
QLineEdit:focus {{ border: 1px solid {P['cyan']}; background: rgba(47,125,255,28); }}

QTabWidget::pane {{
    border: 1px solid rgba(47,125,255,65);
    border-radius: 14px;
    top: -1px;
    background: rgba(47,125,255,12);
}}
QTabBar::tab {{
    background: rgba(255,255,255,8);
    color: {P['muted']};
    padding: 10px 24px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 4px;
    letter-spacing: 3px;
    font-weight: 700;
    font-size: 11px;
}}
QTabBar::tab:selected {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(47,125,255,170), stop:0.5 rgba(79,216,255,130), stop:1 rgba(47,125,255,170));
    color: #ffffff;
    border: 1px solid rgba(79,216,255,150);
    border-bottom: none;
}}
QTabBar::tab:hover:!selected {{ color: {P['cyan']}; }}

QTextEdit {{
    background: rgba(3,7,16,200);
    border: 1px solid rgba(47,125,255,55);
    border-radius: 14px;
    color: #cfe6ff;
    padding: 12px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
}}
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px; }}
QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {P['blue']}, stop:1 {P['cyan']});
    border-radius: 4px; min-height: 30px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QPushButton#detonate {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {P['blue']}, stop:0.55 {P['cyan']}, stop:1 {P['blue']});
    color: white;
    border: 1px solid rgba(255,255,255,200);
    border-radius: 23px;
    padding: 11px 40px;
    letter-spacing: 6px;
    font-weight: 900;
    font-size: 13px;
}}
QPushButton#detonate:hover {{
    border: 1px solid {P['white']};
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #4f97ff, stop:0.55 #7fe3ff, stop:1 #4f97ff);
}}
QPushButton#detonate:pressed {{ background: {P['white']}; color: {P['deep']}; }}
QPushButton#detonate:disabled {{
    background: rgba(60,80,110,120);
    border-color: rgba(130,150,180,55);
    color: rgba(215,228,245,110);
}}
QPushButton#stop {{
    background: rgba(255,93,122,24);
    color: #ffb0bf;
    border: 1px solid rgba(255,93,122,170);
    border-radius: 23px;
    padding: 11px 34px;
    letter-spacing: 6px;
    font-weight: 900;
    font-size: 13px;
}}
QPushButton#stop:hover {{ background: rgba(255,93,122,110); color: white; }}
QPushButton#stop:disabled {{
    color: rgba(150,160,180,110);
    border-color: rgba(120,130,150,45);
    background: rgba(255,255,255,4);
}}
"""


class Signals(QObject):
    log = pyqtSignal(str, str)
    state = pyqtSignal(str)
    stats = pyqtSignal(int, int, int)


def spam_worker(signals, stop_event, token, channel_id, message, delay, stats):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    while not stop_event.is_set():
        try:
            response = requests.post(
                f"https://discord.com/api/v10/channels/{channel_id}/messages",
                headers=headers,
                json={"content": message},
            )
            if response.status_code == 200:
                stats["sent"] += 1
                signals.log.emit(f"Sent: {message}", "ok")
            else:
                stats["errors"] += 1
                signals.log.emit(f"Blocked {response.status_code} - {response.text}", "err")
        except Exception as e:
            stats["errors"] += 1
            signals.log.emit(f"Fault: {e}", "warn")
        stats["cycles"] += 1
        signals.stats.emit(stats["sent"], stats["errors"], stats["cycles"])
        if delay > 0:
            stop_event.wait(delay)


def rename_worker(signals, stop_event, token, gc_id, base_name, delay, stats):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    count = 1
    while not stop_event.is_set():
        try:
            new_name = f"{base_name} {count}"
            response = requests.patch(
                f"https://discord.com/api/v9/channels/{gc_id}",
                headers=headers,
                json={"name": new_name},
            )
            if response.status_code == 200:
                stats["sent"] += 1
                signals.log.emit(f"Renamed to: {new_name}", "ok")
                count += 1
            else:
                stats["errors"] += 1
                signals.log.emit(f"Blocked {response.status_code} - {response.text}", "err")
        except Exception as e:
            stats["errors"] += 1
            signals.log.emit(f"Fault: {e}", "warn")
        stats["cycles"] += 1
        signals.stats.emit(stats["sent"], stats["errors"], stats["cycles"])
        if delay > 0:
            stop_event.wait(delay)


class GlassFrame(QFrame):
    def __init__(self, parent=None, radius=22):
        super().__init__(parent)
        self.radius = radius
        self.t = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(45)

    def _tick(self):
        self.t = (self.t + 0.008) % 1.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        path = QPainterPath()
        path.addRoundedRect(r, self.radius, self.radius)

        fill = QLinearGradient(r.topLeft(), r.bottomRight())
        fill.setColorAt(0.0, QColor("#0a1730"))
        fill.setColorAt(0.5, QColor("#061024"))
        fill.setColorAt(1.0, QColor("#030912"))
        p.fillPath(path, QBrush(fill))

        ang = QConicalGradient(r.center(), self.t * 360)
        ang.setColorAt(0.00, QColor(P["blue"]))
        ang.setColorAt(0.25, QColor(P["cyan"]))
        ang.setColorAt(0.50, QColor(P["white"]))
        ang.setColorAt(0.75, QColor(P["blue_soft"]))
        ang.setColorAt(1.00, QColor(P["blue"]))
        p.setPen(QPen(QColor(47, 125, 255, 55), 7.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.setPen(QPen(QBrush(ang), 1.5))
        p.drawPath(path)

        p.setClipPath(path)
        head = self.t
        sweep = QLinearGradient(r.left(), 0, r.right(), 0)
        sweep.setColorAt(max(0.0, head - 0.15), QColor(255, 255, 255, 0))
        sweep.setColorAt(head, QColor(255, 255, 255, 90))
        sweep.setColorAt(min(1.0, head + 0.15), QColor(255, 255, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(sweep))
        p.drawRect(QRectF(r.left(), r.top(), r.width(), 1.6))
        p.end()


class AuroraBackdrop(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.t = 0.0
        self.motes = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)

    def _tick(self):
        self.t += 0.02
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return
        if len(self.motes) < 46:
            self.motes.append({
                "x": random.uniform(0, w), "y": random.uniform(0, h),
                "vx": random.uniform(-0.3, 0.3), "vy": random.uniform(-0.7, -0.15),
                "r": random.uniform(0.6, 2.4), "a": random.uniform(0.15, 0.65),
                "hue": random.choice([P["blue_soft"], P["cyan"], P["white"]]),
            })
        for m in self.motes:
            m["x"] += m["vx"]; m["y"] += m["vy"]
            if m["y"] < -10:
                m["y"] = h + 10; m["x"] = random.uniform(0, w)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w * 0.5, h * 0.46

        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#0a1730"))
        grad.setColorAt(0.55, QColor("#061024"))
        grad.setColorAt(1.0, QColor("#030912"))
        p.fillRect(self.rect(), QBrush(grad))

        b1 = QRadialGradient(QPointF(cx - w * 0.22 + math.sin(self.t) * 26, cy - 40), w * 0.5)
        b1.setColorAt(0.0, QColor(47, 125, 255, 62)); b1.setColorAt(1.0, QColor(47, 125, 255, 0))
        p.setBrush(QBrush(b1)); p.setPen(Qt.PenStyle.NoPen); p.drawRect(self.rect())

        b2 = QRadialGradient(QPointF(cx + w * 0.26, cy + math.cos(self.t * 0.8) * 36), w * 0.46)
        b2.setColorAt(0.0, QColor(79, 216, 255, 54)); b2.setColorAt(1.0, QColor(79, 216, 255, 0))
        p.setBrush(QBrush(b2)); p.drawRect(self.rect())

        p.save()
        p.translate(cx, cy)
        p.rotate(self.t * 18)
        for i, rr in enumerate((h * 0.30, h * 0.43, h * 0.56)):
            col = QColor(P["cyan"] if i == 1 else P["blue"])
            col.setAlpha(28 + i * 5)
            p.setPen(QPen(col, 1.1)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(0, 0), rr, rr)
            p.setPen(QPen(col, 1.0, Qt.PenStyle.DotLine))
            p.drawEllipse(QPointF(0, 0), rr * 0.86, rr * 0.86)
        p.rotate(-self.t * 36)
        for i in range(16):
            p.rotate(360 / 16)
            col = QColor(P["white"]); col.setAlpha(14)
            p.setPen(QPen(col, 1.0))
            p.drawLine(QPointF(0, h * 0.30), QPointF(0, h * 0.56))
        p.restore()

        p.setPen(Qt.PenStyle.NoPen)
        for m in self.motes:
            col = QColor(m["hue"]); col.setAlphaF(m["a"])
            p.setBrush(QBrush(col))
            p.drawEllipse(QPointF(m["x"], m["y"]), m["r"], m["r"])
        p.end()


class ParticleLayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.parts = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def burst(self, x, y, palette=None):
        palette = palette or [P["blue"], P["cyan"], P["blue_soft"], P["white"], "#bcd8ff"]
        for _ in range(80):
            a = random.uniform(0, math.tau)
            s = random.uniform(2, 10)
            self.parts.append({
                "x": x, "y": y,
                "vx": math.cos(a) * s, "vy": math.sin(a) * s - 1,
                "life": 1.0, "decay": random.uniform(0.015, 0.035),
                "r": random.uniform(1.5, 4.2), "c": random.choice(palette),
            })
        if not self.timer.isActive():
            self.timer.start(16)
        self.update()

    def _tick(self):
        alive = []
        for pt in self.parts:
            pt["x"] += pt["vx"]; pt["y"] += pt["vy"]
            pt["vx"] *= 0.95; pt["vy"] *= 0.95; pt["vy"] += 0.22
            pt["life"] -= pt["decay"]
            if pt["life"] > 0:
                alive.append(pt)
        self.parts = alive
        if self.parts:
            self.update()
        else:
            self.timer.stop()

    def paintEvent(self, event):
        if not self.parts:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for pt in self.parts:
            c = QColor(pt["c"]); c.setAlphaF(max(0.0, min(1.0, pt["life"])))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(c.red(), c.green(), c.blue(), int(55 * pt["life"]))))
            p.drawEllipse(QPointF(pt["x"], pt["y"]), pt["r"] * 2.3, pt["r"] * 2.3)
            p.setBrush(QBrush(c))
            p.drawEllipse(QPointF(pt["x"], pt["y"]), pt["r"], pt["r"])
        p.end()


class NeonTitle(QWidget):
    def __init__(self, text, size=40, parent=None):
        super().__init__(parent)
        self.text = text
        self.fsize = size
        self.phase = 0.0
        self.setMinimumHeight(int(size * 1.5))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(55)

    def _tick(self):
        self.phase += 0.075
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont("Impact", self.fsize)
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, self.fsize * 0.32)
        p.setFont(font)
        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance(self.text)
        x = (self.width() - tw) / 2
        y = (self.height() + fm.capHeight()) / 2
        pt = QPointF(x, y)

        pulse = 0.5 + 0.5 * math.sin(self.phase)
        for i in range(6, 0, -1):
            halo = QColor(P["blue"] if pulse > 0.5 else P["cyan"])
            halo.setAlpha(int((12 + 9 * pulse) * i / 6) + 3)
            p.setPen(QPen(halo, i * 2.3, Qt.PenStyle.SolidLine,
                          Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            p.drawText(pt, self.text)

        g = QLinearGradient(x, 0, x + tw, 0)
        shift = (math.sin(self.phase * 0.5) + 1) / 2
        g.setColorAt(0.0, QColor(P["blue_soft"]))
        g.setColorAt(max(0.0, min(1.0, 0.45 + (shift - 0.5) * 0.4)), QColor("#ffffff"))
        g.setColorAt(0.75, QColor(P["cyan"]))
        g.setColorAt(1.0, QColor(P["white"]))
        p.setPen(QPen(QBrush(g), 1.0))
        p.drawText(pt, self.text)
        p.end()


class StatusOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(18, 18)
        self.state = "idle"
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(70)

    def set_state(self, s):
        self.state = s
        self.update()

    def _tick(self):
        self.phase += 0.14
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        base = {"running": QColor(P["green"]), "sealed": QColor(P["red"])}.get(self.state, QColor(P["muted"]))
        pulse = 0.5 + 0.5 * math.sin(self.phase)
        halo = QRadialGradient(QPointF(9, 9), 9)
        c = QColor(base); c.setAlpha(int(40 + 130 * pulse))
        halo.setColorAt(0.0, c); halo.setColorAt(1.0, QColor(base.red(), base.green(), base.blue(), 0))
        p.setBrush(QBrush(halo)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(0, 0, 18, 18))
        p.setBrush(QBrush(base)); p.drawEllipse(QRectF(5.5, 5.5, 7, 7))
        p.end()


class StatBox(QFrame):
    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self._color = color
        self.target = 0.0
        self.current = 0.0
        self.setFixedHeight(68)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 9, 14, 9)
        lay.setSpacing(1)
        self.num = QLabel("0")
        self.num.setStyleSheet(f"color:{color}; font-size:23px; font-weight:900; font-family:'Consolas',monospace;")
        self.num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{P['muted']}; font-size:9px; letter-spacing:3px; font-weight:700;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.num)
        lay.addWidget(lbl)
        self.anim = QTimer(self)
        self.anim.timeout.connect(self._tick)

    def set_value(self, v):
        self.target = float(v)
        if not self.anim.isActive():
            self.anim.start(30)

    def _tick(self):
        if abs(self.current - self.target) < 0.5:
            self.current = self.target
            self.anim.stop()
        else:
            self.current += (self.target - self.current) * 0.24
        self.num.setText(str(int(round(self.current))))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath(); path.addRoundedRect(r, 13, 13)
        c0 = QColor(self._color)
        g0 = QLinearGradient(r.topLeft(), r.bottomLeft())
        g0.setColorAt(0.0, QColor(c0.red(), c0.green(), c0.blue(), 64))
        g0.setColorAt(1.0, QColor(c0.red(), c0.green(), c0.blue(), 8))
        p.fillPath(path, QBrush(g0))
        p.setPen(QPen(QColor(c0.red(), c0.green(), c0.blue(), 140), 1.2))
        p.drawPath(path)
        p.end()


class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.data = deque([0.0] * 90, maxlen=90)

    def push(self, v):
        self.data.append(float(v))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath(); path.addRoundedRect(r, 12, 12)
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor(47, 125, 255, 26))
        bg.setColorAt(1.0, QColor(47, 125, 255, 4))
        p.fillPath(path, QBrush(bg))
        p.setPen(QPen(QColor(47, 125, 255, 60), 1.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        n = len(self.data)
        mx = max(max(self.data), 1.0)
        pad = 8
        pts = [QPointF(pad + (w - 2 * pad) * (i / (n - 1)),
                       h - pad - (h - 2 * pad) * (v / mx))
               for i, v in enumerate(self.data)]
        line = QPainterPath(pts[0])
        for pt in pts[1:]:
            line.lineTo(pt)
        area = QPainterPath(line)
        area.lineTo(pad + (w - 2 * pad), h - pad)
        area.lineTo(pad, h - pad)
        area.closeSubpath()
        ag = QLinearGradient(0, 0, 0, h)
        ag.setColorAt(0.0, QColor(79, 216, 255, 120))
        ag.setColorAt(1.0, QColor(79, 216, 255, 0))
        p.fillPath(area, QBrush(ag))

        lg = QLinearGradient(pad, 0, w - pad, 0)
        lg.setColorAt(0.0, QColor(P["blue"]))
        lg.setColorAt(1.0, QColor(P["cyan"]))
        p.setPen(QPen(QBrush(lg), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.drawPath(line)

        p.setPen(Qt.PenStyle.NoPen)
        last = pts[-1]
        halo = QRadialGradient(last, 8)
        halo.setColorAt(0.0, QColor(255, 255, 255, 220))
        halo.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(QBrush(halo)); p.drawEllipse(last, 8, 8)
        p.setBrush(QBrush(QColor(P["white"]))); p.drawEllipse(last, 2.6, 2.6)
        p.end()


class RuneDivider(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(14)
        self.t = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)

    def _tick(self):
        self.t = (self.t + 0.012) % 1.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cy = h / 2
        line = QLinearGradient(0, 0, w, 0)
        line.setColorAt(0.0, QColor(47, 125, 255, 0))
        line.setColorAt(0.5, QColor(79, 216, 255, 170))
        line.setColorAt(1.0, QColor(47, 125, 255, 0))
        p.setPen(QPen(QBrush(line), 1.2))
        p.drawLine(QPointF(0, cy), QPointF(w, cy))
        x = self.t * w
        dot = QRadialGradient(QPointF(x, cy), 9)
        dot.setColorAt(0.0, QColor(255, 255, 255, 220))
        dot.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(dot))
        p.drawEllipse(QPointF(x, cy), 9, 9)
        p.end()


class Toast(QLabel):
    def __init__(self, parent, text, color):
        super().__init__(text, parent)
        self.setStyleSheet(
            f"background: rgba(6,16,36,238); color:{color}; "
            f"border:1px solid {color}; border-radius:12px; "
            f"padding:10px 18px; font-weight:700; letter-spacing:2px; font-size:11px;"
        )
        self.adjustSize()
        self.setFixedWidth(max(220, self.width() + 20))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)

    def pop(self, x, y):
        self.move(x, y)
        self.show()
        self.raise_()
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(200)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        QTimer.singleShot(1500, self._fade)

    def _fade(self):
        self.anim2 = QPropertyAnimation(self.effect, b"opacity")
        self.anim2.setDuration(380)
        self.anim2.setStartValue(1.0)
        self.anim2.setEndValue(0.0)
        self.anim2.finished.connect(self.deleteLater)
        self.anim2.start()


class BootOverlay(QWidget):
    done = pyqtSignal()

    LINES = [
        "> initializing mr clan core ...",
        "> forging link to discord nexus ...",
        f"> verifying {VANITY} ...",
        "> arming broadcast protocol ...",
        "MR CLAN",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.li = 0
        self.ci = 0
        self.shown = []
        self._finishing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.start(18)

    def _step(self):
        if self.li >= len(self.LINES):
            return
        line = self.LINES[self.li]
        self.ci += 1
        if self.ci > len(line):
            self.shown.append((line, self.li == len(self.LINES) - 1))
            self.li += 1
            self.ci = 0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(3, 9, 18, 246))
        font = QFont("Cascadia Code", 12)
        p.setFont(font)
        y = 46
        for text, hero in self.shown:
            if hero:
                p.setFont(QFont("Impact", 26))
                p.setPen(QPen(QColor(P["cyan"])))
                p.drawText(44, y + 12, text)
                p.setFont(font)
                y += 34
            else:
                p.setPen(QPen(QColor(P["blue_soft"])))
                p.drawText(44, y, text)
            y += 24
        if self.li < len(self.LINES):
            cur = self.LINES[self.li][:self.ci]
            if self.li == len(self.LINES) - 1:
                p.setFont(QFont("Impact", 26))
                p.setPen(QPen(QColor(P["cyan"])))
            else:
                p.setPen(QPen(QColor(P["muted"])))
            p.drawText(44, y, cur + "_")
            p.setFont(font)
        else:
            if not self._finishing:
                self._finishing = True
                self.timer.stop()
                QTimer.singleShot(280, self._finish)

    def _finish(self):
        self.done.emit()


class Field(QWidget):
    def __init__(self, label, placeholder="", password=False, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        cap = QLabel(label)
        cap.setObjectName("field")
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        if password:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        lay.addWidget(cap)
        lay.addWidget(self.edit)

    def text(self):
        return self.edit.text().strip()


class BotWindow(QWidget):
    EDGE = 9

    def __init__(self):
        super().__init__()
        self.stop_event = None
        self.stats = {"sent": 0, "errors": 0, "cycles": 0}
        self._last_cycles = 0
        self._drag = None
        self._resize_edge = None
        self._start_geo = None
        self._start_pos = None

        self.sig = Signals()
        self.sig.log.connect(self.append_log)
        self.sig.state.connect(self.set_state)
        self.sig.stats.connect(self.update_stats)

        self.setWindowTitle(f"MR CLAN // {VANITY}")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setMinimumSize(860, 560)
        self.resize(1020, 660)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        self.frame = GlassFrame(radius=22)
        root.addWidget(self.frame)

        self.backdrop = AuroraBackdrop(self.frame)
        self.backdrop.lower()

        lay = QVBoxLayout(self.frame)
        lay.setContentsMargins(26, 16, 26, 20)
        lay.setSpacing(10)

        lay.addLayout(self._titlebar())
        lay.addWidget(RuneDivider())

        main = QHBoxLayout()
        main.setSpacing(18)

        left = QWidget()
        left.setFixedWidth(430)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(10)

        hero = NeonTitle("MR CLAN", size=36)
        left_lay.addWidget(hero)
        sub = QLabel(VANITY.upper().replace("/", " / ") + "   ·   CONTROL TERMINAL")
        sub.setStyleSheet(f"color:{P['blue_soft']}; letter-spacing:5px; font-size:9px; font-weight:700;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_lay.addWidget(sub)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._spam_tab(), "BROADCAST")
        self.tabs.addTab(self._rename_tab(), "NAME CHANGER")
        left_lay.addWidget(self.tabs, 1)

        right = QVBoxLayout()
        right.setSpacing(12)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.stat_sent = StatBox("CAST", P["green"])
        self.stat_err = StatBox("FAULTS", P["red"])
        self.stat_cyc = StatBox("CYCLES", P["cyan"])
        for s in (self.stat_sent, self.stat_err, self.stat_cyc):
            stats_row.addWidget(s)
        right.addLayout(stats_row)

        self.spark = Sparkline()
        right.addWidget(self.spark)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        right.addWidget(self.log, 1)

        main.addWidget(left)
        main.addLayout(right, 1)
        lay.addLayout(main, 1)

        footer = QHBoxLayout()
        footer.setSpacing(10)
        self.orb = StatusOrb()
        footer.addWidget(self.orb)
        self.state_lbl = QLabel("STATUS // IDLE")
        self.state_lbl.setStyleSheet(f"color:{P['muted']}; letter-spacing:4px; font-size:11px; font-weight:700;")
        footer.addWidget(self.state_lbl)
        footer.addStretch()
        cred = QLabel(CREDIT)
        cred.setStyleSheet(f"color:{P['cyan']}; letter-spacing:1px; font-size:10px; font-weight:700;")
        footer.addWidget(cred)
        hint = QLabel("CTRL+ENTER")
        hint.setStyleSheet(f"color:{P['muted']}; letter-spacing:2px; font-size:10px;")
        footer.addWidget(hint)
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("stop")
        self.stop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop)
        footer.addWidget(self.stop_btn)
        lay.addLayout(footer)

        self.particles = ParticleLayer(self.frame)
        self.particles.raise_()

        self.boot = BootOverlay(self.frame)
        self.boot.done.connect(self._end_boot)
        self.boot.raise_()

    def _titlebar(self):
        bar = QHBoxLayout()
        logo = QLabel()
        pm = QPixmap(icon_path() or ICON_FILE)
        if not pm.isNull():
            logo.setPixmap(pm.scaled(26, 26, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))
            logo.setFixedSize(30, 30)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bar.addWidget(logo)
        t = QLabel("◆  M R   C L A N")
        t.setStyleSheet(f"color:{P['white']}; font-family:'Impact','Arial Black',sans-serif; font-size:15px; letter-spacing:4px;")
        bar.addWidget(t)
        v = QLabel(VANITY)
        v.setStyleSheet(f"color:{P['blue_soft']}; font-size:11px; letter-spacing:1px;")
        bar.addWidget(v)
        bar.addStretch()
        cred = QLabel(CREDIT)
        cred.setStyleSheet(f"color:{P['cyan']}; font-size:11px; font-weight:700; letter-spacing:1px;")
        bar.addWidget(cred)
        bar.addSpacing(10)
        self.pin_btn = QPushButton("⤢")
        self.pin_btn.setObjectName("wbtn")
        self.pin_btn.setCheckable(True)
        self.pin_btn.setFixedSize(32, 28)
        self.pin_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pin_btn.toggled.connect(self._toggle_top)
        bar.addWidget(self.pin_btn)
        mini = QPushButton("—")
        mini.setObjectName("wbtn")
        mini.setFixedSize(32, 28)
        mini.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        mini.clicked.connect(self.showMinimized)
        bar.addWidget(mini)
        close = QPushButton("✕")
        close.setObjectName("wbtn")
        close.setProperty("class", "closebtn")
        close.setFixedSize(32, 28)
        close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close.clicked.connect(self.close)
        bar.addWidget(close)
        return bar

    def _toggle_top(self, on):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, on)
        self.show()

    def _spam_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 18, 18, 16)
        lay.setSpacing(11)
        self.token_spam = Field("USER TOKEN", "your account token", password=True)
        self.channel_id = Field("CHANNEL ID", "123456789012345678")
        self.message = Field("MESSAGE", "MR CLAN " + VANITY)
        self.delay_spam = Field("DELAY (SECONDS)", "0 = max speed")
        for f in (self.token_spam, self.channel_id, self.message, self.delay_spam):
            lay.addWidget(f)
        btn = QPushButton("BROADCAST")
        btn.setObjectName("detonate")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.clicked.connect(lambda: self.start_spam())
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)
        lay.addStretch()
        return w

    def _rename_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(18, 18, 18, 16)
        lay.setSpacing(11)
        self.token_rename = Field("USER TOKEN", "your account token", password=True)
        self.gc_id = Field("GROUP CHAT ID", "123456789012345678")
        self.base_name = Field("BASE NAME", "mr clan")
        self.delay_rename = Field("DELAY (SECONDS)", "0 = max speed")
        for f in (self.token_rename, self.gc_id, self.base_name, self.delay_rename):
            lay.addWidget(f)
        btn = QPushButton("BROADCAST")
        btn.setObjectName("detonate")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.clicked.connect(lambda: self.start_rename())
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)
        lay.addStretch()
        return w

    def _end_boot(self):
        self.boot.hide()
        self.boot.deleteLater()
        self._toast("MR CLAN LINK ESTABLISHED", P["cyan"])
        self.append_log(f"Welcome to MR CLAN. {VANITY}", "sys")

    def _toast(self, text, color):
        t = Toast(self, text, color)
        g = self.frame.geometry()
        t.pop(g.right() - t.width() - 24, g.bottom() - t.height() - 70)

    def _tag(self, level):
        return {
            "ok": (P["green"], "✦"),
            "err": (P["red"], "✕"),
            "warn": (P["amber"], "!"),
            "sys": (P["blue_soft"], "▸"),
        }.get(level, (P["text"], "•"))

    def append_log(self, text, level="sys"):
        color, glyph = self._tag(level)
        ts = time.strftime("%H:%M:%S")
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.log.append(
            f'<span style="color:{P["muted"]}">[{ts}]</span> '
            f'<span style="color:{color}">{glyph} {safe}</span>'
        )
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_state(self, text):
        self.state_lbl.setText("STATUS // " + text)
        colors = {"RUNNING": P["green"], "STOPPED": P["red"]}
        self.state_lbl.setStyleSheet(
            f"color:{colors.get(text, P['muted'])}; letter-spacing:4px; font-size:11px; font-weight:700;"
        )
        self.orb.set_state(text.lower() if text in colors else "idle")

    def update_stats(self, sent, errors, cycles):
        self.stat_sent.set_value(sent)
        self.stat_err.set_value(errors)
        self.stat_cyc.set_value(cycles)
        delta = max(0, cycles - self._last_cycles)
        self._last_cycles = cycles
        self.spark.push(delta)

    def _parse_delay(self, field):
        raw = field.text() or "0"
        try:
            return float(raw)
        except ValueError:
            self.append_log(f"Invalid delay '{raw}' → 0", "warn")
            return 0.0

    def _launch(self, target):
        self.stats = {"sent": 0, "errors": 0, "cycles": 0}
        self._last_cycles = 0
        self.update_stats(0, 0, 0)
        self.stop_event = threading.Event()
        threading.Thread(target=target, args=(self.stop_event,), daemon=True).start()
        self.stop_btn.setEnabled(True)
        self.set_state("RUNNING")

    def start_spam(self):
        token = self.token_spam.text()
        channel_id = self.channel_id.text()
        message = self.message.text()
        if not token or not channel_id or not message:
            QMessageBox.warning(self, "Incomplete", "Token, Channel ID and Message are required.")
            return
        delay = self._parse_delay(self.delay_spam)
        self.append_log(f"Broadcasting → channel {channel_id} (delay {delay}s)", "sys")
        cx, cy = self.frame.width() * 0.27, self.frame.height() * 0.34
        self.particles.burst(cx, cy)
        self._toast("BROADCAST // CHANNEL", P["cyan"])
        self._launch(lambda se: spam_worker(self.sig, se, token, channel_id, message, delay, self.stats))

    def start_rename(self):
        token = self.token_rename.text()
        gc_id = self.gc_id.text()
        base_name = self.base_name.text()
        if not token or not gc_id or not base_name:
            QMessageBox.warning(self, "Incomplete", "Token, Group Chat ID and Base Name are required.")
            return
        delay = self._parse_delay(self.delay_rename)
        self.append_log(f"Changing name → {gc_id} (delay {delay}s)", "sys")
        cx, cy = self.frame.width() * 0.27, self.frame.height() * 0.34
        self.particles.burst(cx, cy)
        self._toast("BROADCAST // NAME CHANGER", P["cyan"])
        self._launch(lambda se: rename_worker(self.sig, se, token, gc_id, base_name, delay, self.stats))

    def stop(self):
        if self.stop_event:
            self.stop_event.set()
        self.stop_btn.setEnabled(False)
        self.append_log("Stop requested — halting.", "warn")
        self._toast("STOPPED", P["red"])
        self.set_state("STOPPED")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = self.frame.geometry()
        r = QRectF(g).adjusted(1, 1, -1, -1)
        for i in range(5, 0, -1):
            col = QColor(47, 125, 255)
            col.setAlpha(9 + (5 - i) * 6)
            p.setPen(QPen(col, i * 2.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(r.adjusted(-i, -i, i, i + 2), 22 + i, 22 + i)
        p.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.backdrop.setGeometry(self.frame.rect())
        self.particles.setGeometry(self.frame.rect())
        if hasattr(self, "boot"):
            self.boot.setGeometry(self.frame.rect())

    def _edge_at(self, pos):
        w, h = self.width(), self.height()
        m = self.EDGE
        x, y = pos.x(), pos.y()
        left = x <= m
        right = x >= w - m
        top = y <= m
        bottom = y >= h - m
        if top and left: return "tl"
        if top and right: return "tr"
        if bottom and left: return "bl"
        if bottom and right: return "br"
        if left: return "l"
        if right: return "r"
        if top: return "t"
        if bottom: return "b"
        return None

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position().toPoint()
        edge = self._edge_at(pos)
        if edge:
            self._resize_edge = edge
            self._start_geo = self.geometry()
            self._start_pos = event.globalPosition().toPoint()
            event.accept()
            return
        if pos.y() < 68:
            self._drag = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self._resize_edge and self._start_geo and self._start_pos:
            gp = event.globalPosition().toPoint()
            dx = gp.x() - self._start_pos.x()
            dy = gp.y() - self._start_pos.y()
            g = QRect(self._start_geo)
            e = self._resize_edge
            if "l" in e: g.setLeft(g.left() + dx)
            if "r" in e: g.setRight(g.right() + dx)
            if "t" in e: g.setTop(g.top() + dy)
            if "b" in e: g.setBottom(g.bottom() + dy)
            if g.width() >= self.minimumWidth() and g.height() >= self.minimumHeight():
                self.setGeometry(g)
            event.accept()
            return
        if self._drag is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag)
            event.accept()
            return
        edge = self._edge_at(pos)
        cursors = {
            "l": Qt.CursorShape.SizeHorCursor, "r": Qt.CursorShape.SizeHorCursor,
            "t": Qt.CursorShape.SizeVerCursor, "b": Qt.CursorShape.SizeVerCursor,
            "tl": Qt.CursorShape.SizeFDiagCursor, "br": Qt.CursorShape.SizeFDiagCursor,
            "tr": Qt.CursorShape.SizeBDiagCursor, "bl": Qt.CursorShape.SizeBDiagCursor,
        }
        self.setCursor(cursors.get(edge, Qt.CursorShape.ArrowCursor))

    def mouseReleaseEvent(self, event):
        self._drag = None
        self._resize_edge = None
        self._start_geo = None
        self._start_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            (self.start_spam if self.tabs.currentIndex() == 0 else self.start_rename)()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MR CLAN")

    icon = QIcon(icon_path() or ICON_FILE)
    if not icon.isNull():
        app.setWindowIcon(icon)

    pw, ok = QInputDialog.getText(
        None, "MR CLAN", "Enter password:", QLineEdit.EchoMode.Password
    )
    if not ok:
        return
    if pw != PASSWORD:
        QMessageBox.critical(None, "Denied", "Wrong password. Exiting.")
        return

    win = BotWindow()
    if not icon.isNull():
        win.setWindowIcon(icon)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
