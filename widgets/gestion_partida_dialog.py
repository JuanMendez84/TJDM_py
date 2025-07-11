from PySide6.QtWidgets import QDialog, QPushButton, QMessageBox, QComboBox, QVBoxLayout, QLabel, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem
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

        # Labels para mostrar fechas (solo se añaden una vez)
        self.label_juego = QLabel()
        self.label_fecha_inicio = QLabel()
        self.label_fecha_fin = QLabel()
        self.layout.addWidget(self.label_juego)
        self.layout.addWidget(self.label_fecha_inicio)
        self.layout.addWidget(self.label_fecha_fin)

        # Widgets para botones
        self.botones_widget = QWidget()
        self.botones_layout = QHBoxLayout(self.botones_widget)

        # Botones
        self.btn_iniciar = QPushButton("Iniciar partida")
        self.btn_finalizar = QPushButton("Finalizar partida")
        self.botones_layout.addWidget(self.btn_iniciar)
        self.botones_layout.addWidget(self.btn_finalizar)

        self.cargar_datos_partida()
        self.cargar_jugadores()
        self.layout.addWidget(self.botones_widget)

        # Conexiones de botones
        self.btn_iniciar.clicked.connect(self.iniciar_partida)
        self.btn_finalizar.clicked.connect(self.finalizar_partida)

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

        # Almacenar estados para lógica de botones
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

        # Actualizar estado de botones
        self.btn_iniciar.setVisible(not self.fecha_inicio)
        self.btn_finalizar.setVisible(bool(self.fecha_inicio) and not self.fecha_fin)

        self.label_juego.setText(f"Juego: {juego_nombre}")
        self.label_fecha_inicio.setText(f"Fecha inicio: {fecha_inicio if fecha_inicio else '--/--/---- --:--:--'}")
        self.label_fecha_fin.setText(f"Fecha fin: {fecha_fin if fecha_fin else '--/--/---- --:--:--'}")
        
    def cargar_jugadores(self):
        # Elimina la tabla anterior si existe
        if hasattr(self, 'tabla_jugadores'):
            self.layout.removeWidget(self.tabla_jugadores)
            self.tabla_jugadores.deleteLater()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.nombre, e.nombre, e.color, e.id
            FROM PARTIDA_JUGADORES pj
            JOIN USUARIOS u ON pj.usuario_id = u.id
            JOIN EQUIPOS e ON pj.equipo_id = e.id
            WHERE pj.partida_id = ?
            ORDER BY u.nombre
        """, (self.partida_id,))
        jugadores = cursor.fetchall()
        conn.close()

        self.tabla_jugadores = QTableWidget()
        self.tabla_jugadores.setColumnCount(4)
        self.tabla_jugadores.setHorizontalHeaderLabels(["Jugador", "Equipo", "Color", "Posición"])
        self.tabla_jugadores.setRowCount(len(jugadores))

        self.equipos_posiciones = {}  # equipo_id: posicion
        self.combo_boxes = {}  # equipo_id: QComboBox

        for row, (nombre, equipo, color, idequipo) in enumerate(jugadores):
            item_jugador = QTableWidgetItem(nombre)
            item_equipo = QTableWidgetItem(equipo)
            item_color = QTableWidgetItem()
            item_color.setBackground(QColor("#" + color))
            
            equipo_id = idequipo

            combo = self.combo_boxes.get(equipo_id)
        
            if not combo:
                combo = QComboBox()
                combo.addItems([str(i+1) for i in range(len(jugadores))])  # Ajusta el rango según lógica de posiciones
                combo.setEnabled(bool(self.fecha_inicio))
                combo.currentTextChanged.connect(lambda pos, eid=equipo_id: self.cambiar_posicion_equipo(eid, pos))
                self.combo_boxes[equipo_id] = combo
                # Inicializa la posición con el valor actual del combo
                if combo.isEnabled():
                    self.equipos_posiciones[equipo_id] = combo.currentText()
            self.tabla_jugadores.setCellWidget(row, 3, combo)

            self.tabla_jugadores.setItem(row, 0, item_jugador)
            self.tabla_jugadores.setItem(row, 1, item_equipo)
            self.tabla_jugadores.setItem(row, 2, item_color)

        self.layout.addWidget(self.tabla_jugadores)
        # Llama a la función para actualizar el estado del botón
        self.actualizar_estado_finalizar()

    def cambiar_posicion_equipo(self, equipo_id, posicion):
        # Cambia el valor del combo de todos los jugadores de ese equipo
        for eid, combo in self.combo_boxes.items():
            if eid == equipo_id:
                combo.blockSignals(True)
                combo.setCurrentText(str(posicion))
                combo.blockSignals(False)
        self.equipos_posiciones[equipo_id] = posicion
        self.actualizar_estado_finalizar()

    def actualizar_estado_finalizar(self):
        total_equipos = len(self.combo_boxes)
        posiciones_asignadas = len([p for p in self.equipos_posiciones.values() if p])
        self.btn_finalizar.setEnabled(total_equipos == posiciones_asignadas)


    def iniciar_partida(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE PARTIDAS
            SET fecha_inicio = datetime('now')
            WHERE id = ?
        """, (self.partida_id,))
        conn.commit()
        conn.close()
        self.cargar_datos_partida()  # Actualizar UI
        self.cargar_jugadores()

    def finalizar_partida(self):
        # Chequeo: no puede haber posiciones repetidas entre equipos distintos
        posiciones = list(self.equipos_posiciones.values())
        if len(posiciones) != len(set(posiciones)):
            QMessageBox.critical(self, "Error", "Dos equipos distintos no pueden tener la misma posición.")
            return  # No continúa con el update

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE PARTIDAS
            SET fecha_fin = datetime('now')
            WHERE id = ?
        """, (self.partida_id,))

        # Actualizar posiciones en PARTIDA_JUGADORES
        for equipo_id, posicion in self.equipos_posiciones.items():
            cursor.execute("""
                UPDATE PARTIDA_JUGADORES SET posicion = ? 
                WHERE partida_id = ? AND equipo_id = ?
            """, (posicion, self.partida_id, equipo_id))
        # Aquí va el cálculo de puntos

        conn.commit()
        conn.close()
        self.cargar_datos_partida()
