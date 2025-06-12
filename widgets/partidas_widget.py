from widgets.gestion_partida_dialog import GestionPartidaDialog
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QListWidgetItem,
    QListWidget, QPushButton, QLabel, QFrame, QWidget, QGridLayout, QMessageBox
)
from PySide6.QtGui import QColor, QBrush, QPainter, QPalette
from PySide6.QtCore import Qt
import sqlite3

DB_PATH = "miapp.db"  # Ajusta la ruta si es necesario

class PartidasWidget(QDialog):
    def __init__(self, torneo_id, parent=None):
        super().__init__(parent)
        self.torneo_id = torneo_id
        self.setWindowTitle("Gestión de Partidas del Torneo")
        self.resize(800, 600)

        # Layout principal
        self.layout = QVBoxLayout(self)

        # 1. Clasificación
        self.tabla_clasificacion = QTableWidget()
        self.tabla_clasificacion.setColumnCount(3)
        self.tabla_clasificacion.setHorizontalHeaderLabels(["Posición", "Jugador", "Puntos"])
        self.layout.addWidget(self.tabla_clasificacion)

        # Separador
        self.layout.addWidget(QLabel("Partidas del Torneo"))
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)

        # 2. Sección inferior: partidas pendientes y terminadas
        hbox = QHBoxLayout()

        # 2.1. Partidas pendientes (izquierda)
        self.lista_pendientes = QListWidget()
        self.lista_pendientes.setSelectionMode(QListWidget.SingleSelection)
        self.boton_gestionar = QPushButton("Gestionar Partida")
        self.boton_gestionar.clicked.connect(self.gestionar_partida_seleccionada)
        vbox_izq = QVBoxLayout()
        vbox_izq.addWidget(QLabel("Partidas Pendientes"))
        vbox_izq.addWidget(self.lista_pendientes)
        vbox_izq.addWidget(self.boton_gestionar)
        hbox.addLayout(vbox_izq)

        # 2.2. Partidas terminadas (derecha)
        self.lista_terminadas = QListWidget()
        self.lista_terminadas.setSelectionMode(QListWidget.SingleSelection)
        self.boton_detalles = QPushButton("Consultar Detalles")
        self.boton_detalles.clicked.connect(self.consultar_detalles)
        vbox_der = QVBoxLayout()
        vbox_der.addWidget(QLabel("Partidas Terminadas"))
        vbox_der.addWidget(self.lista_terminadas)
        vbox_der.addWidget(self.boton_detalles)
        hbox.addLayout(vbox_der)

        self.layout.addLayout(hbox)

        # Cargar datos
        self.cargar_clasificacion()
        self.cargar_partidas()

    def cargar_clasificacion(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.nombre, SUM(pj.puntos) as total_puntos
            FROM PARTIDAS pa
            JOIN PARTIDA_JUGADORES pj ON pa.id = pj.partida_id
            JOIN USUARIOS u ON pj.usuario_id = u.id
            WHERE pa.torneo_id = ?
            GROUP BY pj.usuario_id
            ORDER BY total_puntos DESC
        """, (self.torneo_id,))
        resultados = cursor.fetchall()
        conn.close()

        self.tabla_clasificacion.setRowCount(len(resultados))
        posicion = 1
        anterior_puntos = None
        posiciones = []
        for i, (nombre, puntos) in enumerate(resultados):
            if anterior_puntos is None:
                posiciones.append(posicion)
            else:
                if puntos == anterior_puntos:
                    posiciones.append(posicion)
                else:
                    posicion = i + 1
                    posiciones.append(posicion)
            anterior_puntos = puntos

        # Colores
        color_oro = QBrush(QColor("#FFD700"))
        color_plata = QBrush(QColor("#C0C0C0"))
        color_bronce = QBrush(QColor("#CD7F32"))

        if resultados:
            max_puntos = resultados[0][1]
            segundos = [p for n, p in resultados if p < max_puntos]
            segundo_puntos = segundos[0] if segundos else None
            terceros = [p for n, p in resultados if p < (segundo_puntos if segundo_puntos is not None else max_puntos)]
            tercer_puntos = terceros[0] if terceros else None
        else:
            max_puntos = segundo_puntos = tercer_puntos = None

        for i, ((nombre, puntos), pos) in enumerate(zip(resultados, posiciones)):
            item_pos = QTableWidgetItem(str(pos))
            item_nombre = QTableWidgetItem(nombre)
            item_puntos = QTableWidgetItem(str(puntos))

            if puntos == max_puntos:
                for item in (item_pos, item_nombre, item_puntos):
                    item.setBackground(color_oro)
            elif segundo_puntos is not None and puntos == segundo_puntos:
                for item in (item_pos, item_nombre, item_puntos):
                    item.setBackground(color_plata)
            elif tercer_puntos is not None and puntos == tercer_puntos:
                for item in (item_pos, item_nombre, item_puntos):
                    item.setBackground(color_bronce)

            self.tabla_clasificacion.setItem(i, 0, item_pos)
            self.tabla_clasificacion.setItem(i, 1, item_nombre)
            self.tabla_clasificacion.setItem(i, 2, item_puntos)

    def cargar_partidas(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Partidas pendientes (fecha_fin es NULL)
        cursor.execute("""
            SELECT pa.id, j.nombre, pa.fecha_inicio, pa.fecha_fin
            FROM PARTIDAS pa
            JOIN JUEGOS j ON pa.juego_id = j.id
            WHERE pa.torneo_id = ? AND pa.fecha_fin IS NULL
            ORDER BY pa.fecha_inicio
        """, (self.torneo_id,))
        pendientes = cursor.fetchall()
        for partida_id, juego_nombre, fecha_inicio, _ in pendientes:
            item = f"{juego_nombre} (ID: {partida_id})"
            if fecha_inicio:
                item += f" - Inicio: {fecha_inicio}"
            item_widget = QListWidgetItem(item)
            item_widget.setData(Qt.UserRole, partida_id)
            self.lista_pendientes.addItem(item_widget)

        # Partidas terminadas (fecha_fin NO es NULL)
        cursor.execute("""
            SELECT pa.id, j.nombre, pa.fecha_inicio, pa.fecha_fin
            FROM PARTIDAS pa
            JOIN JUEGOS j ON pa.juego_id = j.id
            WHERE pa.torneo_id = ? AND pa.fecha_fin IS NOT NULL
            ORDER BY pa.fecha_fin DESC
        """, (self.torneo_id,))
        terminadas = cursor.fetchall()
        for partida_id, juego_nombre, fecha_inicio, fecha_fin in terminadas:
            item = f"{juego_nombre} (ID: {partida_id})"
            if fecha_inicio:
                item += f" - Inicio: {fecha_inicio}"
            if fecha_fin:
                item += f" - Fin: {fecha_fin}"
            item_widget = QListWidgetItem(item)
            item_widget.setData(Qt.UserRole, partida_id)
            self.lista_terminadas.addItem(item_widget)
        conn.close()

    def gestionar_partida_seleccionada(self):
        seleccion = self.lista_pendientes.selectedItems()
        if not seleccion:
            QMessageBox.warning(self, "Aviso", "Selecciona una partida pendiente.")
            return

        item = self.lista_pendientes.currentItem()
        if item:
            partida_id = item.data(Qt.UserRole)
        else:
            QMessageBox.warning(self, "Aviso", "Selecciona una partida pendiente.")
            return

        ventana_gestion = GestionPartidaDialog(partida_id, self)
        ventana_gestion.exec()

    def consultar_detalles(self):
        seleccion = self.lista_terminadas.selectedItems()
        if not seleccion:
            QMessageBox.warning(self, "Aviso", "Selecciona una partida terminada.")
            return

        # Por ahora no hace nada
        print("Detalles de partida terminada seleccionada")
