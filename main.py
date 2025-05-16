from PySide6.QtWidgets import QApplication
from db import * 
from widgets.login_widget import LoginDialog
from widgets.main_window import MainWindow
import sys

if __name__ == "__main__":
    crear_bd()
    crear_tabla_juegos()
    crear_tabla_categorias()
    crear_tabla_juegos_categorias()
    crear_tablas_torneos()
    crear_tabla_partidas()
    crear_tabla_partida_jugadores()

    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() == login.DialogCode.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        app.quit()
        sys.exit()
