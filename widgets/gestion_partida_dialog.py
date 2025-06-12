from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QColor, QPainter
from PySide6.QtCore import Qt
import sqlite3

DB_PATH = "miapp.db"  # Ajusta la ruta si es necesario

class GestionPartidaDialog(QDialog):
    def __init__(self, partida_id, parent=None):
        super().__init__(parent)
        self.partida_id = partida_id
        self.setWindowTitle("Gestión de Partida")
        self.resize(500, 400)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.cargar_datos_partida()
        self.cargar_jugadores()

    def cargar_datos_partida(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT j.nombre, pa.fecha_inicio, pa.fecha_fin
            FROM PARTIDAS pa
            JOIN JUEGOS j ON pa.juego_id = j.id
            WHERE pa.id = ?
        """, (self.partida_id,))
        juego_nombre, fecha_inicio, fecha_fin = cursor.fetchone()
        conn.close()

        self.layout.addWidget(QLabel(f"Juego: {juego_nombre}"))
        self.layout.addWidget(QLabel(f"Fecha inicio: {fecha_inicio if fecha_inicio else '--/--/---- --:--:--'}"))
        self.layout.addWidget(QLabel(f"Fecha fin: {fecha_fin if fecha_fin else '--/--/---- --:--:--'}"))

    def cargar_jugadores(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.nombre, e.nombre, e.color
            FROM PARTIDA_JUGADORES pj
            JOIN USUARIOS u ON pj.usuario_id = u.id
            JOIN EQUIPOS e ON pj.equipo_id = e.id
            WHERE pj.partida_id = ?
            ORDER BY u.nombre
        """, (self.partida_id,))
        jugadores = cursor.fetchall()
        conn.close()

        self.tabla_jugadores = QTableWidget()
        self.tabla_jugadores.setColumnCount(3)
        self.tabla_jugadores.setHorizontalHeaderLabels(["Jugador", "Equipo", "Color"])
        self.tabla_jugadores.setRowCount(len(jugadores))

        for row, (nombre, equipo, color) in enumerate(jugadores):
            item_jugador = QTableWidgetItem(nombre)
            item_equipo = QTableWidgetItem(equipo)
            item_color = QTableWidgetItem()
            item_color.setBackground(QColor("#" + color))

            self.tabla_jugadores.setItem(row, 0, item_jugador)
            self.tabla_jugadores.setItem(row, 1, item_equipo)
            self.tabla_jugadores.setItem(row, 2, item_color)

        self.layout.addWidget(self.tabla_jugadores)
