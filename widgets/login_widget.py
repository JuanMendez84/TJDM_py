from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from db import verificar_credenciales

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        self.setModal(True)
        layout = QVBoxLayout()

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.usuario_input)

        self.contrasena_input = QLineEdit()
        self.contrasena_input.setPlaceholderText("Contraseña")
        self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.contrasena_input)

        self.login_btn = QPushButton("Aceptar")
        self.login_btn.clicked.connect(self.intentar_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def intentar_login(self):
        usuario = self.usuario_input.text()
        contrasena = self.contrasena_input.text()
        if verificar_credenciales(usuario, contrasena):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos")