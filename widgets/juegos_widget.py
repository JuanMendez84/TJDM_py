import sqlite3
import warnings
import csv
import pandas as pd
from db import DB_PATH, obtener_categorias_de_juego
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QFormLayout, QLineEdit, QSpinBox, QPushButton, QFrame, QHBoxLayout,
    QMessageBox, QListWidget, QListWidgetItem, QDialog, QLabel, QDialogButtonBox, QMessageBox
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
        self.tabla_juegos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
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
        self.btn_importar = QPushButton("Agregar desde fichero...")
        self.btn_importar.clicked.connect(self.importar_desde_fichero)

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
        botones_layout.addWidget(self.btn_importar)
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
        
        self.tabla_juegos.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener todos los juegos con sus categorías
        cursor.execute('''
        SELECT J.id, J.nombre, J.MinJugadores, J.MaxJugadores, 
               GROUP_CONCAT(C.nombre, ', ') as categorias
        FROM JUEGOS J
        LEFT JOIN JUEGOS_CATEGORIAS JC ON J.id = JC.juego_id
        LEFT JOIN CATEGORIAS C ON JC.categoria_id = C.id
        GROUP BY J.id
        ORDER BY J.nombre
    ''')

        for row_idx, (id_juego, nombre, min_jug, max_jug, categorias_str) in enumerate(cursor.fetchall()):
            # Formatear categorías
            categorias = categorias_str.split(', ') if categorias_str else []
            texto_categorias, tooltip_categorias = self.formatear_categorias(categorias)

            # Crear items para la tabla
            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setData(Qt.UserRole, id_juego)
            item_min = QTableWidgetItem(str(min_jug))
            item_max = QTableWidgetItem(str(max_jug))
            item_categorias = QTableWidgetItem(texto_categorias)
            item_categorias.setToolTip(tooltip_categorias)  # <-- Tooltip con todas

            # Añadir fila
            self.tabla_juegos.insertRow(row_idx)
            self.tabla_juegos.setItem(row_idx, 0, item_nombre)
            self.tabla_juegos.setItem(row_idx, 1, item_min)
            self.tabla_juegos.setItem(row_idx, 2, item_max)
            self.tabla_juegos.setItem(row_idx, 3, item_categorias)

        conn.close()

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

    def formatear_categorias(self, categorias):
        if len(categorias) > 3:
            return ", ".join(categorias[:3]) + "...", ", ".join(categorias)
        else:
            return ", ".join(categorias), ", ".join(categorias)

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

        # Obtener ID del juego desde la columna 0
        item_nombre = self.tabla_juegos.item(fila, 0)
        juego_id = item_nombre.data(Qt.UserRole)
        nombre_actual = item_nombre.text()

        # Obtener valores editados
        nuevo_nombre = nombre_actual
        nuevo_min = self.tabla_juegos.item(fila, 1).text()
        nuevo_max = self.tabla_juegos.item(fila, 2).text()

        # Validar tipos
        try:
            nuevo_min = int(nuevo_min)
            nuevo_max = int(nuevo_max)
        except ValueError:
            QMessageBox.warning(self, "Error", "Los jugadores deben ser números")
            self.tabla_juegos.itemChanged.disconnect(self.guardar_edicion)
            self.cargar_juegos()
            self.tabla_juegos.itemChanged.connect(self.guardar_edicion)
            return

        # Validar lógica
        if nuevo_max < nuevo_min:
            QMessageBox.warning(self, "Error", "El máximo debe ser ≥ al mínimo")
            self.tabla_juegos.itemChanged.disconnect(self.guardar_edicion)
            self.cargar_juegos()
            self.tabla_juegos.itemChanged.connect(self.guardar_edicion)
            return

        # Obtener nombre original desde la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM JUEGOS WHERE id=?", (juego_id,))
        nombre_original = cursor.fetchone()[0]

        # Si el nombre cambió, validar duplicados
        if nombre_actual != nombre_original:
            cursor.execute(
                "SELECT COUNT(*) FROM JUEGOS WHERE nombre=? AND id != ?",
                (nombre_actual, juego_id)
            )
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Error", "Ya existe un juego con ese nombre")
                conn.close()
                self.tabla_juegos.itemChanged.disconnect(self.guardar_edicion)
                self.cargar_juegos()
                self.tabla_juegos.itemChanged.connect(self.guardar_edicion)
                return

        # Actualizar la base de datos
        try:
            cursor.execute(
                "UPDATE JUEGOS SET nombre=?, MinJugadores=?, MaxJugadores=? WHERE id=?",
                (nombre_actual, nuevo_min, nuevo_max, juego_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {str(e)}")
        finally:
            conn.close()

        self.tabla_juegos.itemChanged.disconnect(self.guardar_edicion)
        self.cargar_juegos()  # Recargar para reflejar cambios
        self.tabla_juegos.itemChanged.connect(self.guardar_edicion)


    def importar_desde_fichero(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar fichero", "", "CSV (*.csv);;Excel (*.xlsx *.xls)"
        )
        if not archivo:
            return

        # Leer el archivo
        filas = []
        if archivo.lower().endswith('.csv'):
            with open(archivo, encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                filas = [row for row in reader if row]
        else:
            df = pd.read_excel(archivo, header=None)
            filas = df.values.tolist()

        # Validar y procesar filas
        informe = []
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener todas las categorías existentes
        cursor.execute("SELECT nombre, id FROM CATEGORIAS")
        categorias_dict = {nombre.strip().lower(): idcat for nombre, idcat in cursor.fetchall()}

        num_insertados = 0
        for idx, fila in enumerate(filas, start=1):
            if len(fila) < 4:
                informe.append(f"Fila {idx}: formato incorrecto (faltan columnas)")
                continue

            nombre_juego = str(fila[0]).strip()
            min_jug = str(fila[1]).strip()
            max_jug = str(fila[2]).strip()
            categorias = [c.strip() for c in str(fila[3]).split(',') if c.strip()]

            # Validar categorías
            categorias_no_existentes = [c for c in categorias if c.lower() not in categorias_dict]
            if categorias_no_existentes:
                informe.append(f"Fila {idx}: categorías no existentes: {', '.join(categorias_no_existentes)}")
                continue

            # Insertar juego
            try:
                cursor.execute(
                    "INSERT INTO JUEGOS (nombre, MinJugadores, MaxJugadores) VALUES (?, ?, ?)",
                    (nombre_juego, min_jug, max_jug)
                )
                juego_id = cursor.lastrowid
                # Insertar en JUEGOS_CATEGORIAS
                for cat in categorias:
                    cursor.execute(
                        "INSERT INTO JUEGOS_CATEGORIAS (juego_id, categoria_id) VALUES (?, ?)",
                        (juego_id, categorias_dict[cat.lower()])
                    )
                num_insertados += 1
            except sqlite3.IntegrityError:
                informe.append(f"Fila {idx}: el juego '{nombre_juego}' ya existe (descartado)")
                continue

        conn.commit()
        conn.close()

        # Mostrar informe
        mensaje = f"Juegos insertados correctamente: {num_insertados}\n"
        if informe:
            mensaje += "\nErrores:\n" + "\n".join(informe)
        else:
            mensaje += "\nNo hubo errores."
        QMessageBox.information(self, "Importación finalizada", mensaje)

        self.cargar_juegos()  # Refresca la tabla
