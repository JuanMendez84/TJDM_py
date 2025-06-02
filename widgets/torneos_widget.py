import sqlite3
from db import DB_PATH
import random
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QSpinBox,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QListWidget, QListWidgetItem,
    QFormLayout, QLineEdit, QTextEdit, QDateEdit, QHeaderView, QLabel, QComboBox
)
from PySide6.QtCore import Qt, QDate

class FormularioTorneo(QDialog):
    def __init__(self, parent=None, torneo_data=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Torneo" if not torneo_data else "Editar Torneo")
        self.setMinimumWidth(700)
        self.setMinimumWidth(800)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # --- Primera fila: Nombre, Fecha inicio, Fecha fin ---
        fila1 = QHBoxLayout()
        self.input_nombre = QLineEdit()
        self.input_fecha_inicio = QDateEdit(calendarPopup=True)
        self.input_fecha_inicio.setDate(QDate.currentDate())
        self.input_fecha_fin = QDateEdit(calendarPopup=True)
        self.input_fecha_fin.setDate(QDate.currentDate().addMonths(1))
        fila1.addWidget(QLabel("Nombre:"))
        fila1.addWidget(self.input_nombre)
        fila1.addWidget(QLabel("Fecha inicio:"))
        fila1.addWidget(self.input_fecha_inicio)
        fila1.addWidget(QLabel("Fecha fin:"))
        fila1.addWidget(self.input_fecha_fin)
        self.layout.addLayout(fila1)

        # --- Segunda fila: Descripción ---
        fila2 = QHBoxLayout()
        self.input_descripcion = QTextEdit()
        self.input_descripcion.setMaximumHeight(50)
        fila2.addWidget(QLabel("Descripción:"))
        fila2.addWidget(self.input_descripcion)
        self.layout.addLayout(fila2)

        # --- Tercera fila: Usuarios y Juegos ---
        fila3 = QHBoxLayout()
        self.lista_usuarios = QListWidget()
        self.lista_usuarios.setSelectionMode(QListWidget.MultiSelection)
        self.lista_usuarios.setMaximumHeight(120)
        self.lista_usuarios.setMaximumWidth(200)
        self.cargar_usuarios()

        #self.lista_juegos = QListWidget()
        #self.lista_juegos.setSelectionMode(QListWidget.MultiSelection)
        #self.lista_juegos.setMaximumHeight(120)
        #self.lista_juegos.setMaximumWidth(200)
        #self.cargar_juegos()

        usuarios_widget = QVBoxLayout()
        usuarios_widget.addWidget(QLabel("Jugadores:"))
        usuarios_widget.addWidget(self.lista_usuarios)

        #juegos_widget = QVBoxLayout()
        #juegos_widget.addWidget(QLabel("Juegos seleccionados:"))
        #juegos_widget.addWidget(self.lista_juegos)

        fila3.addLayout(usuarios_widget)
        #fila3.addSpacing(20)
        #fila3.addLayout(juegos_widget)
        self.layout.addLayout(fila3)

        fila4 = QHBoxLayout()
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems([
            "Manualmente", 
            "Totalmente al azar",
            "Al azar por categorías"
        ])
        fila4.addWidget(QLabel("Selección de juegos:"))
        fila4.addWidget(self.combo_metodo)
        self.layout.addLayout(fila4)

        # Widgets dinámicos según el método
        self.widget_dinamico = QWidget()
        self.layout_dinamico = QVBoxLayout()
        self.widget_dinamico.setLayout(self.layout_dinamico)
        self.layout.addWidget(self.widget_dinamico)

        # Lista de juegos seleccionados
        self.lista_juegos = QListWidget()
        self.lista_juegos.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(QLabel("Juegos seleccionados:"))
        self.layout.addWidget(self.lista_juegos)

        # Botones
        botones = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.accept)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        botones.addStretch()
        botones.addWidget(self.btn_guardar)
        botones.addWidget(self.btn_cancelar)
        self.layout.addLayout(botones)

        # Inicializar
        self.combo_metodo.currentIndexChanged.connect(self.actualizar_ui)
        self.actualizar_ui()  # Inicializar la UI

        # Si editas, puedes cargar datos aquí (no implementado en este fragmento)

    def actualizar_ui(self):
        # Limpiar widgets dinámicos
        while self.layout_dinamico.count():
            child = self.layout_dinamico.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        metodo = self.combo_metodo.currentText()
        self.lista_juegos.clear()

        if metodo == "Manualmente":
            # Cargar todos los juegos para selección manual
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM JUEGOS ORDER BY nombre")
            juegos = cursor.fetchall()
            conn.close()
            for juego_id, nombre in juegos:
                item = QListWidgetItem(nombre)
                item.setData(Qt.UserRole, juego_id)
                self.lista_juegos.addItem(item)
            self.lista_juegos.setSelectionMode(QListWidget.MultiSelection)

        elif metodo == "Totalmente al azar":
            self.spin_num_juegos = QSpinBox()
            self.spin_num_juegos.setMinimum(1)
            self.spin_num_juegos.setMaximum(50)
            self.btn_generar = QPushButton("Generar lista aleatoria")
            self.btn_generar.clicked.connect(self.generar_aleatorio_total)
            self.layout_dinamico.addWidget(QLabel("Número de juegos:"))
            self.layout_dinamico.addWidget(self.spin_num_juegos)
            self.layout_dinamico.addWidget(self.btn_generar)

        elif metodo == "Al azar por categorías":
            self.lista_categorias = QListWidget()
            self.lista_categorias.setSelectionMode(QListWidget.MultiSelection)
            self.cargar_categorias()
            self.spin_num_juegos = QSpinBox()
            self.spin_num_juegos.setMinimum(1)
            self.spin_num_juegos.setMaximum(50)
            self.btn_generar = QPushButton("Generar por categorías")
            self.btn_generar.clicked.connect(self.generar_aleatorio_categorias)
            self.layout_dinamico.addWidget(QLabel("Selecciona categorías:"))
            self.layout_dinamico.addWidget(self.lista_categorias)
            self.layout_dinamico.addWidget(QLabel("Número de juegos:"))
            self.layout_dinamico.addWidget(self.spin_num_juegos)
            self.layout_dinamico.addWidget(self.btn_generar)

    def cargar_categorias(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM CATEGORIAS ORDER BY nombre")
        categorias = cursor.fetchall()
        conn.close()
        self.lista_categorias.clear()
        for nombre, in categorias:
            item = QListWidgetItem(nombre)
            self.lista_categorias.addItem(item)

    def generar_aleatorio_total(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM JUEGOS")
        todos_juegos = cursor.fetchall()
        conn.close()
        num_juegos = self.spin_num_juegos.value()
        seleccionados = random.sample(todos_juegos, min(num_juegos, len(todos_juegos)))
        self.lista_juegos.clear()
        for juego_id, nombre in seleccionados:
            item = QListWidgetItem(nombre)
            item.setData(Qt.UserRole, juego_id)
            item.setSelected(True)
            self.lista_juegos.addItem(item)
        self.lista_juegos.setSelectionMode(QListWidget.MultiSelection)

    def generar_aleatorio_categorias(self):
        # Obtener categorías seleccionadas (en minúsculas para comparación insensible)
        categorias = [item.text().strip().lower() for item in self.lista_categorias.selectedItems()]
        if not categorias:
            return
    
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    
        # Paso 1: Obtener IDs de las categorías seleccionadas
        placeholders = ",".join("?" for _ in categorias)
        cursor.execute(f"""
            SELECT id FROM CATEGORIAS 
            WHERE LOWER(nombre) IN ({placeholders})
        """, categorias)
        categoria_ids = [row[0] for row in cursor.fetchall()]
    
        if not categoria_ids:
            conn.close()
            return
    
        # Paso 2: Buscar juegos que pertenezcan a TODAS las categorías seleccionadas
        query = f"""
            SELECT J.id, J.nombre
            FROM JUEGOS J
            WHERE NOT EXISTS (
                SELECT C.id 
                FROM CATEGORIAS C 
                WHERE C.id IN ({','.join(['?']*len(categoria_ids))})
                AND NOT EXISTS (
                    SELECT 1 
                    FROM JUEGOS_CATEGORIAS JC 
                    WHERE JC.juego_id = J.id 
                    AND JC.categoria_id = C.id
                )
            )
            ORDER BY RANDOM()
            LIMIT ?
        """
        cursor.execute(query, categoria_ids + [self.spin_num_juegos.value()])
        juegos = cursor.fetchall()
        conn.close()
    
        # Mostrar resultados
        self.lista_juegos.clear()
        for juego_id, nombre in juegos:
            item = QListWidgetItem(nombre)
            item.setData(Qt.UserRole, juego_id)
            item.setSelected(True)
            self.lista_juegos.addItem(item)
    

#fin del código
    
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
                        
                # Crea las partidas y asigna equipos/jugadores
                # Obtén los ids de los equipos por orden de id
                cursor.execute("SELECT id FROM EQUIPOS ORDER BY id")
                equipos_ids = [row[0] for row in cursor.fetchall()]

                for juego_id in juegos_ids:
                # Crea la partida
                    cursor.execute(
                    "INSERT INTO PARTIDAS (torneo_id, juego_id, fecha_inicio, fecha_fin) VALUES (?, ?, NULL, NULL)",
                    (torneo_id, juego_id)
                    )
                    partida_id = cursor.lastrowid

                # Asigna equipos a los jugadores en orden
                for idx, usuario_id in enumerate(usuarios_ids):
                    equipo_id = equipos_ids[idx % len(equipos_ids)]  # Rueda por los 6 equipos
                    cursor.execute(
                        "INSERT INTO PARTIDA_JUGADORES (partida_id, usuario_id, equipo_id, posicion, puntos) VALUES (?, ?, ?, NULL, 0)",
                        (partida_id, usuario_id, equipo_id)
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
