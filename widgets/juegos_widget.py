import sqlite3
import warnings
from db import DB_PATH, obtener_categorias_de_juego


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QLineEdit, QSpinBox, QPushButton, QFrame, QHBoxLayout,
    QMessageBox, QListWidget, QListWidgetItem, QDialog, QLabel, QDialogButtonBox
)

class GestionJuegosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Tabla de juegos
        self.tabla_juegos = QTableWidget()
        self.tabla_juegos.setColumnCount(4)
        self.tabla_juegos.setHorizontalHeaderLabels(["Nombre", "MinJugadores", "MaxJugadores", "Categorías"])
        self.tabla_juegos.verticalHeader().setVisible(False)
        self.tabla_juegos.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        self.tabla_juegos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_juegos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_juegos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # Formulario para añadir juegos
        form_frame = QFrame()
        form_layout = QFormLayout()

        # Campos del formulario (DEFINIR PRIMERO)
        self.input_nombre = QLineEdit()
        self.input_min = QSpinBox()
        self.input_min.setMinimum(1)
        self.input_min.setMaximum(999)
        self.input_max = QSpinBox()
        self.input_max.setMinimum(1)
        self.input_max.setMaximum(999)
        self.btn_anadir = QPushButton("Añadir juego")
        self.btn_anadir.clicked.connect(self.anadir_juego)

        # Lista de categorías (AÑADIR DESPUÉS DE LOS CAMPOS)
        #self.categorias_list = QListWidget()
        #self.categorias_list.setSelectionMode(QListWidget.MultiSelection)

        # Añadir elementos al formulario (ORDEN CORRECTO)
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Mínimo jugadores:", self.input_min)
        form_layout.addRow("Máximo jugadores:", self.input_max)
        #form_layout.addRow("Categorías:", self.categorias_list)  # <-- Ahora sí existe input_nombre
        form_layout.addRow(self.btn_anadir)

        # Botones adicionales
        botones_layout = QHBoxLayout()
        self.btn_eliminar = QPushButton("Eliminar juego seleccionado")
        self.btn_eliminar.setEnabled(False)
        self.btn_eliminar.clicked.connect(self.eliminar_juego)
        botones_layout.addWidget(self.btn_anadir)
        botones_layout.addWidget(self.btn_eliminar)
        form_layout.addRow(botones_layout)

        form_frame.setLayout(form_layout)
        self.layout.addWidget(self.tabla_juegos)
        self.layout.addWidget(form_frame)
        self.setLayout(self.layout)

        # Cargar datos (LLAMAR AL FINAL)
        self.cargar_juegos()
        #self.cargar_categorias_disponibles()  # <-- Ahora input_nombre ya está definido
        self.tabla_juegos.itemChanged.connect(self.guardar_edicion)
        self.tabla_juegos.itemSelectionChanged.connect(self.actualizar_botones)


    def actualizar_botones(self):
        """Habilita/deshabilita el botón de eliminar según la selección"""
        seleccionado = bool(self.tabla_juegos.selectedItems())
        self.btn_eliminar.setEnabled(seleccionado)

    def eliminar_juego(self):
        # Obtener nombre del juego seleccionado
        fila_seleccionada = self.tabla_juegos.currentRow()
        nombre = self.tabla_juegos.item(fila_seleccionada, 0).text()

        # Confirmación
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar el juego '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM JUEGOS WHERE Nombre=?", (nombre,))
                conn.commit()
                conn.close()
                self.cargar_juegos()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {str(e)}")

    def cargar_juegos(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            try:
                self.tabla_juegos.itemChanged.disconnect(self.guardar_edicion)
            except (TypeError, RuntimeError) as e:
                pass  # No estaba conectada

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, Nombre, MinJugadores, MaxJugadores FROM JUEGOS')
        juegos = cursor.fetchall()
        conn.close()

        self.tabla_juegos.setRowCount(len(juegos))
        for row, (juego_id, nombre, min_jug, max_jug) in enumerate(juegos):
            self.tabla_juegos.setItem(row, 0, QTableWidgetItem(nombre))
            self.tabla_juegos.setItem(row, 1, QTableWidgetItem(str(min_jug)))
            self.tabla_juegos.setItem(row, 2, QTableWidgetItem(str(max_jug)))
            categorias = obtener_categorias_de_juego(juego_id)
            # Mostrar solo las tres primeras, y "..." si hay más
            if len(categorias) > 3:
                texto = ", ".join(categorias[:3]) + f" ... (+{len(categorias)-3})"
            else:
                texto = ", ".join(categorias)
            item_cat = QTableWidgetItem(texto)
            item_cat.setToolTip(", ".join(categorias))  # Tooltip con todas
            self.tabla_juegos.setItem(row, 3, item_cat)
    
        self.tabla_juegos.cellClicked.connect(self.mostrar_categorias_completas)
        self.tabla_juegos.itemChanged.connect(self.guardar_edicion)

    def cargar_categorias_disponibles(self):
        self.categorias_list.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM CATEGORIAS ORDER BY nombre")
        for cat_id, nombre in cursor.fetchall():
            item = QListWidgetItem(nombre)
            item.setData(1, cat_id)  # 1 = Qt.UserRole
            self.categorias_list.addItem(item)
        conn.close()

    def anadir_juego(self):
        nombre = self.input_nombre.text().strip()
        min_jug = self.input_min.value()
        max_jug = self.input_max.value()

        # Validación básica
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        if max_jug < min_jug:
            QMessageBox.warning(self, "Error", "El máximo debe ser igual o mayor al mínimo")
            return

        # Ventana emergente para seleccionar categorías
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecciona categorías")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Selecciona las categorías para este juego:"))

        cat_list = QListWidget()
        cat_list.setSelectionMode(QListWidget.MultiSelection)
        # Cargar categorías
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM CATEGORIAS ORDER BY nombre")
        categorias = cursor.fetchall()
        conn.close()
        for cat_id, nombre_cat in categorias:
            item = QListWidgetItem(nombre_cat)
            item.setData(1, cat_id)
            cat_list.addItem(item)
        layout.addWidget(cat_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            # Insertar juego
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO JUEGOS (Nombre, MinJugadores, MaxJugadores) VALUES (?, ?, ?)",
                    (nombre, min_jug, max_jug)
                )
                juego_id = cursor.lastrowid
                # Insertar relaciones
                for item in cat_list.selectedItems():
                    categoria_id = item.data(1)
                    cursor.execute(
                        "INSERT INTO JUEGOS_CATEGORIAS (juego_id, categoria_id) VALUES (?, ?)",
                        (juego_id, categoria_id)
                    )
                conn.commit()
                conn.close()
                self.input_nombre.clear()
                self.input_min.setValue(1)
                self.input_max.setValue(1)
                self.cargar_juegos()
            except sqlite3.IntegrityError:
                QMessageBox.critical(self, "Error", "Ya existe un juego con ese nombre")

    def mostrar_categorias_completas(self, row, column):
        if column == 3:
            categorias = self.tabla_juegos.item(row, column).toolTip()
            QMessageBox.information(self, "Categorías asociadas", categorias if categorias else "Sin categorías")

    def guardar_edicion(self, item):
        fila = item.row()
        columna = item.column()
        nombre_original = self.tabla_juegos.item(fila, 0).text()
        min_jug = self.tabla_juegos.item(fila, 1).text()
        max_jug = self.tabla_juegos.item(fila, 2).text()
    
        # Validación de tipos y lógica
        try:
            min_jug = int(min_jug)
            max_jug = int(max_jug)
        except ValueError:
            QMessageBox.warning(self, "Error", "MinJugadores y MaxJugadores deben ser números.")
            self.cargar_juegos()
            return
    
        if not nombre_original:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío.")
            self.cargar_juegos()
            return
    
        if max_jug < min_jug:
            QMessageBox.warning(self, "Error", "El máximo debe ser igual o mayor al mínimo.")
            self.cargar_juegos()
            return
    
        # Obtener el id del juego editado (para evitar problemas si el nombre cambia)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM JUEGOS LIMIT 1 OFFSET ?", (fila,)
        )
        resultado = cursor.fetchone()
        if not resultado:
            conn.close()
            return
        juego_id = resultado[0]
    
        # Validar unicidad del nombre si se ha editado
        cursor.execute(
            "SELECT COUNT(*) FROM JUEGOS WHERE Nombre=? AND id<>?", (nombre_original, juego_id)
        )
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Error", "Ya existe un juego con ese nombre.")
            self.cargar_juegos()
            conn.close()
            return
    
        # Actualizar en la base de datos
        try:
            cursor.execute(
                "UPDATE JUEGOS SET Nombre=?, MinJugadores=?, MaxJugadores=? WHERE id=?",
                (nombre_original, min_jug, max_jug, juego_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {str(e)}")
        finally:
            conn.close()
        self.cargar_juegos()