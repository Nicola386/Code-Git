from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsPathItem,
    QGraphicsEllipseItem, QGraphicsSimpleTextItem
)
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt
import math
import pandas as pd


def lade_letzte_sonnendaten(csv_dateipfad):
    df = pd.read_csv('context_data.csv', header=None, on_bad_lines='skip')
    
    letzte = df.iloc[-1]
    print(letzte)
    # Spaltenpositionen gemäß deiner Grafik
    
    elevation = float(letzte[5])
    azimut = float(letzte[4])
    sunrise = float(letzte[2])
    sunset = float(letzte[3])

    zeitpunkt = datetime.now()

    return {
        "zeitpunkt": zeitpunkt,
        "azimut": azimut,
        "elevation": elevation,
        "sunrise": sunrise,
        "sunset": sunset
    }


def sonnenverlauf(view_widget, csv_dateipfad):
    daten = lade_letzte_sonnendaten(csv_dateipfad)

    datum = daten["zeitpunkt"].date()
    sunrise_time = datetime.combine(datum, datetime.min.time()) + timedelta(minutes=daten["sunrise"])
    sunset_time = datetime.combine(datum, datetime.min.time()) + timedelta(minutes=daten["sunset"])
    now = daten["zeitpunkt"]

    ratio = (now - sunrise_time).total_seconds() / (sunset_time - sunrise_time).total_seconds()
    ratio = max(0.0, min(1.0, ratio))

    scene = QGraphicsScene()
    width = 200
    height = 80
    margin_x = 20
    margin_y = 10
    sun_radius = 6

    # Sonnenpfad
    path = QPainterPath()
    path.moveTo(margin_x, margin_y + height)
    for i in range(101):
        x = margin_x + (i / 100.0) * width
        y = margin_y + height - math.sin(math.pi * i / 100.0) * height
        path.lineTo(x, y)

    sun_path = QGraphicsPathItem(path)
    sun_path.setPen(QPen(QColor("#aaaaaa"), 2))
    scene.addItem(sun_path)

    # Sonne
    x = margin_x + ratio * width
    y = margin_y + height - math.sin(math.pi * ratio) * height
    sun = QGraphicsEllipseItem(x - sun_radius, y - sun_radius, sun_radius * 2, sun_radius * 2)
    sun.setBrush(QBrush(QColor("#FFD700")))
    sun.setPen(QPen(Qt.NoPen))
    scene.addItem(sun)

    # Text
    font = QFont("Arial", 8)
    sunrise_text = QGraphicsSimpleTextItem(sunrise_time.strftime("↑ %H:%M"))
    sunrise_text.setFont(font)
    sunrise_text.setPos(margin_x - 10, margin_y + height + 10)
    scene.addItem(sunrise_text)

    sunset_text = QGraphicsSimpleTextItem(sunset_time.strftime("↓ %H:%M"))
    sunset_text.setFont(font)
    sunset_text.setPos(margin_x + width - 30, margin_y + height + 10)
    scene.addItem(sunset_text)

    view_widget.setScene(scene)
    view_widget.setSceneRect(0, 0, width + margin_x * 2, height + 40)

    return daten
