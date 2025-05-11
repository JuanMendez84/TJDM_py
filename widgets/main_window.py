from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget
from widgets.juegos_widget import GestionJuegosWidget
from widgets.categorias_widget import GestionCategoriasWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Aplicación Principal")
        self.setGeometry(100, 100, 600, 400)

        # Menú superior
        menu_bar = self.menuBar()

        # Menú Archivo
        archivo_menu = menu_bar.addMenu("Archivo")
        gestionar_juegos_action = archivo_menu.addAction("Gestionar juegos")
        gestionar_juegos_action.triggered.connect(self.abrir_gestion_juegos)
        gestionar_categorias_action = archivo_menu.addAction("Gestionar categorías")
        gestionar_categorias_action.triggered.connect(self.abrir_gestion_categorias)
        salir_action = archivo_menu.addAction("Salir")
        salir_action.triggered.connect(self.close)

        # Menú Ayuda
        ayuda_menu = menu_bar.addMenu("Ayuda")
        acerca_action = ayuda_menu.addAction("Acerca de")
        acerca_action.triggered.connect(self.mostrar_acerca_de)

        # Frame central vacío
        central_widget = QWidget()
        self.setCentralWidget(central_widget)


    def abrir_gestion_categorias(self):
        self.gestion_categorias_widget = GestionCategoriasWidget()
        self.setCentralWidget(self.gestion_categorias_widget)
        
    def abrir_gestion_juegos(self):
        self.gestion_juegos_widget = GestionJuegosWidget()
        self.setCentralWidget(self.gestion_juegos_widget)  # Reemplaza el contenido central

    def mostrar_acerca_de(self):
        QMessageBox.information(self, "Acerca de", "Aplicación de ejemplo con PySide6.")
