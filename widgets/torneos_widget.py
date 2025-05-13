import sqlite3
from db import DB_PATH
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QListWidget, QListWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QDateEdit, QHeaderView
)
from PySide6.QtCore import Qt, QDate

class FormularioTorneo(QDialog):
    def __init__(self, parent=None, torneo_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Torneo" if not torneo_data else "Editar Torneo")
        
        layout = QFormLayout()
        
        # Campos del formulario
        self.input_nombre = QLineEdit()
        self.input_descripcion = QTextEdit()
        self.input_fecha_inicio = QDateEdit(calendarPopup=True)
        self.input_fecha_inicio.setDate(QDate.currentDate())
        self.input_fecha_fin = QDateEdit(calendarPopup=True)
        self.input_fecha_fin.setDate(QDate.currentDate().addMonths(1))
        
        # Listas de selección múltiple
        self.lista_usuarios = QListWidget()
        self.lista_usuarios.setSelectionMode(QListWidget.MultiSelection)
        self.lista_juegos = QListWidget()
        self.lista_juegos.setSelectionMode(QListWidget.MultiSelection)

        # Cargar usuarios y juegos de la BD
        self.cargar_usuarios()
        self.cargar_juegos()

        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Descripción:", self.input_descripcion)
        layout.addRow("Fecha inicio:", self.input_fecha_inicio)
        layout.addRow("Fecha fin (opcional):", self.input_fecha_fin)
        layout.addRow("Jugadores:", self.lista_usuarios)
        layout.addRow("Juegos:", self.lista_juegos)

        # Botones
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.accept)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        layout.addRow(btn_guardar, btn_cancelar)
        self.setLayout(layout)
        
        # Cargar datos si estamos editando
        if torneo_data:
            self.cargar_datos(torneo_data)
    
    def cargar_datos(self, data):
        self.input_nombre.setText(data['nombre'])
        self.input_descripcion.setPlainText(data['descripcion'])
        self.input_fecha_inicio.setDate(QDate.fromString(data['fecha_inicio'], 'yyyy-MM-dd'))
        if data['fecha_fin']:
            self.input_fecha_fin.setDate(QDate.fromString(data['fecha_fin'], 'yyyy-MM-dd'))

    def cargar_usuarios(self):
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM USUARIOS ORDER BY nombre")
        for user_id, nombre in cursor.fetchall():
            item = QListWidgetItem(nombre)
            item.setData(Qt.UserRole, user_id)
            self.lista_usuarios.addItem(item)
        conn.close()

    def cargar_juegos(self):
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM JUEGOS ORDER BY nombre")
        for juego_id, nombre in cursor.fetchall():
            item = QListWidgetItem(nombre)
            item.setData(Qt.UserRole, juego_id)
            self.lista_juegos.addItem(item)
        conn.close()

class GestionTorneosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        # Tabla de torneos
        self.tabla_torneos = QTableWidget()
        self.tabla_torneos.setColumnCount(7)
        self.tabla_torneos.setHorizontalHeaderLabels([
            "Nombre", "Descripción", "Fecha Creación", "Fecha Inicio", "Fecha Fin", "Participantes", "Juegos"
        ])
        self.tabla_torneos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_torneos.verticalHeader().setVisible(False)
        
        # Botones
        self.btn_anadir = QPushButton("Añadir Torneo")
        self.btn_editar = QPushButton("Editar Torneo")
        self.btn_eliminar = QPushButton("Eliminar Torneo")
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
        
        # Layout botones
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_anadir)
        botones_layout.addWidget(self.btn_editar)
        botones_layout.addWidget(self.btn_eliminar)
        
        # Ensamblar layout
        self.layout.addWidget(self.tabla_torneos)
        self.layout.addLayout(botones_layout)
        self.setLayout(self.layout)
        
        # Conexiones
        self.btn_anadir.clicked.connect(self.anadir_torneo)
        self.btn_editar.clicked.connect(self.editar_torneo)
        self.btn_eliminar.clicked.connect(self.eliminar_torneo)
        self.tabla_torneos.itemSelectionChanged.connect(self.actualizar_botones)
        
        self.cargar_torneos()
    
    def cargar_torneos(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nombre, descripcion, fecha_creacion, fecha_inicio, fecha_fin 
            FROM TORNEOS ORDER BY fecha_inicio DESC
        ''')
        torneos = cursor.fetchall()
        conn.close()
        
        self.tabla_torneos.setRowCount(len(torneos))
        for row, (torneo_id, nombre, desc, creacion, inicio, fin) in enumerate(torneos):
            self.tabla_torneos.setItem(row, 0, QTableWidgetItem(nombre))
            self.tabla_torneos.setItem(row, 1, QTableWidgetItem(desc if desc else ""))
            self.tabla_torneos.setItem(row, 2, QTableWidgetItem(creacion))
            self.tabla_torneos.setItem(row, 3, QTableWidgetItem(inicio))
            self.tabla_torneos.setItem(row, 4, QTableWidgetItem(fin if fin else ""))
            jugadores = self.obtener_nombres_usuarios(torneo_id)
            juegos = self.obtener_nombres_juegos(torneo_id)
            self.tabla_torneos.setItem(row, 5, QTableWidgetItem(jugadores))
            self.tabla_torneos.setItem(row, 6, QTableWidgetItem(juegos))

    def actualizar_botones(self):
        seleccionado = bool(self.tabla_torneos.selectedItems())
        self.btn_editar.setEnabled(seleccionado)
        self.btn_eliminar.setEnabled(seleccionado)
    
    def anadir_torneo(self):
        dialog = FormularioTorneo(self)
        if dialog.exec() == QDialog.Accepted:
            nombre = dialog.input_nombre.text().strip()
            desc = dialog.input_descripcion.toPlainText().strip()
            fecha_inicio = dialog.input_fecha_inicio.date().toString('yyyy-MM-dd')
            fecha_fin = dialog.input_fecha_fin.date().toString('yyyy-MM-dd') if dialog.input_fecha_fin.date() > dialog.input_fecha_inicio.date() else None

            # Obtén los IDs seleccionados de usuarios y juegos
            usuarios_ids = [item.data(Qt.UserRole) for item in dialog.lista_usuarios.selectedItems()]
            juegos_ids = [item.data(Qt.UserRole) for item in dialog.lista_juegos.selectedItems()]

            try:
                conn = sqlite3.connect('miapp.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO TORNEOS 
                    (nombre, descripcion, fecha_creacion, fecha_inicio, fecha_fin)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    nombre,
                    desc if desc else None,
                    datetime.now().strftime('%Y-%m-%d'),
                    fecha_inicio,
                    fecha_fin
                ))

                torneo_id = cursor.lastrowid  # <-- ID del torneo recién creado
    
                # Inserta en TORNEOS_USUARIOS
                for usuario_id in usuarios_ids:
                    cursor.execute(
                        "INSERT INTO TORNEOS_USUARIOS (torneo_id, usuario_id) VALUES (?, ?)",
                        (torneo_id, usuario_id)
                    )
    
                # Inserta en TORNEOS_JUEGOS
                for juego_id in juegos_ids:
                    cursor.execute(
                        "INSERT INTO TORNEOS_JUEGOS (torneo_id, juego_id) VALUES (?, ?)",
                        (torneo_id, juego_id)
                    )
                
                conn.commit()
                self.cargar_torneos()
            except sqlite3.IntegrityError:
                QMessageBox.critical(self, "Error", "Ya existe un torneo con ese nombre")
            finally:
                conn.close()
    
    def eliminar_torneo(self):
        fila = self.tabla_torneos.currentRow()
        nombre = self.tabla_torneos.item(fila, 0).text()
        
        confirmar = QMessageBox.question(
            self, 
            "Confirmar eliminación", 
            f"¿Eliminar el torneo '{nombre}'? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmar == QMessageBox.Yes:
            conn = sqlite3.connect('miapp.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM TORNEOS WHERE nombre = ?', (nombre,))
            conn.commit()
            conn.close()
            self.cargar_torneos()
    
    def editar_torneo(self):
        # Implementación similar a anadir_torneo pero con UPDATE
        pass

    def obtener_nombres_usuarios(self, torneo_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre FROM USUARIOS
            WHERE id IN (
                SELECT usuario_id FROM TORNEOS_USUARIOS WHERE torneo_id = ?
            )
            ORDER BY nombre
        ''', (torneo_id,))
        nombres = [row[0] for row in cursor.fetchall()]
        conn.close()
        # Muestra hasta 3 nombres, el resto como resumen
        if len(nombres) > 3:
            return ", ".join(nombres[:3]) + f" ...(+{len(nombres) - 3})"
        else:
            return ", ".join(nombres)

    def obtener_nombres_juegos(self, torneo_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre FROM JUEGOS
            WHERE id IN (
                SELECT juego_id FROM TORNEOS_JUEGOS WHERE torneo_id = ?
            )
            ORDER BY nombre
        ''', (torneo_id,))
        nombres = [row[0] for row in cursor.fetchall()]
        conn.close()
        if len(nombres) > 3:
            return ", ".join(nombres[:3]) + f" ...(+{len(nombres) - 3})"
        else:
            return ", ".join(nombres)
