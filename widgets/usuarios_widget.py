import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

DB_PATH = "miapp.db"  # Usa tu variable global si la tienes

class GestionUsuariosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Usuarios")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(3)
        self.tabla_usuarios.setHorizontalHeaderLabels(["Usuario", "Nombre", "Contraseña"])
        self.tabla_usuarios.verticalHeader().setVisible(False)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_usuarios.setEditTriggers(QTableWidget.NoEditTriggers)

        self.layout.addWidget(self.tabla_usuarios)

        # Formulario de alta
        form_layout = QHBoxLayout()
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_contrasena = QLineEdit()
        self.input_contrasena.setPlaceholderText("Contraseña")
        self.input_contrasena.setEchoMode(QLineEdit.Password)
        self.btn_anadir = QPushButton("Añadir")

        form_layout.addWidget(QLabel("Usuario:"))
        form_layout.addWidget(self.input_usuario)
        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(QLabel("Contraseña:"))
        form_layout.addWidget(self.input_contrasena)
        form_layout.addWidget(self.btn_anadir)

        self.layout.addLayout(form_layout)

        # Botón eliminar
        self.btn_eliminar = QPushButton("Eliminar usuario seleccionado")
        self.layout.addWidget(self.btn_eliminar)

        # Conexiones
        self.btn_anadir.clicked.connect(self.anadir_usuario)
        self.btn_eliminar.clicked.connect(self.eliminar_usuario)

        self.cargar_usuarios()

    def cargar_usuarios(self):
        self.tabla_usuarios.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, nombre, contrasena FROM USUARIOS ORDER BY usuario")
        for row_idx, (usuario, nombre, contrasena) in enumerate(cursor.fetchall()):
            self.tabla_usuarios.insertRow(row_idx)
            self.tabla_usuarios.setItem(row_idx, 0, QTableWidgetItem(usuario))
            self.tabla_usuarios.setItem(row_idx, 1, QTableWidgetItem(nombre if nombre else ""))
            self.tabla_usuarios.setItem(row_idx, 2, QTableWidgetItem("*" * len(contrasena)))
        conn.close()

    def anadir_usuario(self):
        usuario = self.input_usuario.text().strip()
        nombre = self.input_nombre.text().strip()
        contrasena = self.input_contrasena.text().strip()
        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error", "Usuario y contraseña son obligatorios.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO USUARIOS (usuario, contrasena, nombre) VALUES (?, ?, ?)",
                (usuario, contrasena, nombre)
            )
            conn.commit()
            conn.close()
            self.cargar_usuarios()
            self.input_usuario.clear()
            self.input_nombre.clear()
            self.input_contrasena.clear()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Error", "El usuario ya existe.")

    def eliminar_usuario(self):
        fila = self.tabla_usuarios.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Selecciona un usuario para eliminar.")
            return
        usuario = self.tabla_usuarios.item(fila, 0).text()
        confirmar = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Eliminar el usuario '{usuario}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmar == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM USUARIOS WHERE usuario = ?", (usuario,))
            conn.commit()
            conn.close()
            self.cargar_usuarios()
