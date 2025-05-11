import sqlite3
from db import DB_PATH

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QLineEdit, QPushButton, QFrame, QMessageBox
)


class GestionCategoriasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Tabla de categorías
        self.tabla_categorias = QTableWidget()
        self.tabla_categorias.setColumnCount(1)
        self.tabla_categorias.setHorizontalHeaderLabels(["Nombre"])
        self.tabla_categorias.verticalHeader().setVisible(False)
        self.tabla_categorias.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # Formulario para añadir categorías
        form_frame = QFrame()
        form_layout = QFormLayout()
        
        self.input_nombre = QLineEdit()
        self.btn_anadir = QPushButton("Añadir categoría")
        self.btn_anadir.clicked.connect(self.anadir_categoria)

        form_layout.addRow("Nombre categoría:", self.input_nombre)
        form_layout.addRow(self.btn_anadir)
        
        form_frame.setLayout(form_layout)

        self.layout.addWidget(self.tabla_categorias)
        self.layout.addWidget(form_frame)
        self.setLayout(self.layout)
        self.cargar_categorias()

    def cargar_categorias(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT nombre FROM CATEGORIAS')
        categorias = cursor.fetchall()
        conn.close()

        self.tabla_categorias.setRowCount(len(categorias))
        for row, (nombre,) in enumerate(categorias):
            self.tabla_categorias.setItem(row, 0, QTableWidgetItem(nombre))

    def anadir_categoria(self):
        nombre = self.input_nombre.text().strip()

        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO CATEGORIAS (nombre) VALUES (?)",
                (nombre,)
            )
            conn.commit()
            conn.close()
            
            self.input_nombre.clear()
            self.cargar_categorias()
            
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "Ya existe una categoría con ese nombre")