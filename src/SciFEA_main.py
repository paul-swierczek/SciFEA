import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, 
    QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, 
    QListWidget, QGridLayout, QFormLayout, QMessageBox,
    QSizePolicy, QButtonGroup, QCheckBox, QRadioButton,
    QComboBox, QFileDialog, QDialog, QDialogButtonBox,
    QStackedWidget, QStackedLayout, QStyle, QLayout
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import (QPainter, QColor, QPen, QIcon, QBrush, QPixmap, QFont, QKeySequence)
from PySide6.QtCore import (Qt, QSize)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import math
import sympy as sp
import os
import json
import copy
import random
import re
from solver.function_builder import FormulateDistribution


# Ścieżka startu wyboru folderu
FOLDER_PATH = os.path.dirname(__file__)
# Ścieżka ikony
file_directory = os.path.dirname(__file__)
icon_path = os.path.join(file_directory, r"assets/images/Logo_main_icon.ico")
images_path = os.path.join(file_directory, r"assets/images")
# Słownik konfiguracji ignorowania symboli sympy:
sympy_LOCAL = {"I": sp.Symbol("I"), "E": sp.Symbol("E"), "S": sp.Symbol("S"), "Beta": sp.Symbol("Beta"), "beta": sp.Symbol("beta"), "Q": sp.Symbol("Q")}

# ====================
# klasa strony głównej
# ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Parametry okna, pobieranie stałych dla placy programu wymiarów wyświetlacza komputera
        self.display_dimentions = QApplication.primaryScreen().size()
        self.display_width = self.display_dimentions.width()
        self.display_height = self.display_dimentions.height()
        # wywołanie funkcji ustawiającej wymiary okna:
        self.set_window_size()
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("SciFEA")

        # Inicjacje widgetów używanych na różnych stronach: ===============================================
        self.canvas = MeshCanvas(self)  # Odniesienie do widhetu rysującego aby można było łączyć się z nim
        # Ustaw politykę rozmiaru, aby rozciągał się na całą dostępną przestrzeń
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # widgety list elementów
        self.Node_list = QListWidget()
        self.EL_list = QListWidget()
        # inicjacja klasy silnika obciążeń
        self.LoadsCore = LoadMeshEditorCore(self, self.canvas)
        # =================================================================================================

        # Zamiast dotychczasowego central_widget i layoutu, użyj QStackedWidget
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Strona 1: Wstęp do programu, indeks 0
        self.welcome_page_var = self.welcome_page()
        self.stacked.addWidget(self.welcome_page_var)

        # Strona 2: Menadżer projektu: indeks 1
        self.project_manager_var = self.project_manager()
        self.stacked.addWidget(self.project_manager_var)

        # Strona 3: edytor siatki, indeks 2
        self.mesher_page_var = self.mesher_page()
        self.stacked.addWidget(self.mesher_page_var)

        # Strona 4: edytor siatki obciążeń, indeks 3
        self.load_mesher_page_var = self.load_mesher_page()
        self.stacked.addWidget(self.load_mesher_page_var)

        # Strona 5: post processor, indeks 4
        self.postprocessor_var = self.postprocessor_page()
        self.stacked.addWidget(self.postprocessor_var)

        # Ustawiamy domyślnie przeglądarkę
        self.stacked.setCurrentIndex(0)

    def set_window_size(self, window_width = 1200, window_height = 600):
        window_corner_x = self.display_width / 2 - window_width / 2
        window_corner_y = self.display_height /2 - window_height / 2
        self.setGeometry(window_corner_x, window_corner_y, window_width, window_height)

    def make_icon_btn_lt(self, patent_lt = None, btn_txt = "", font_size = 10,  icon_size_x = 32, icon_size_y = 32, image_path = icon_path):
        local_lt = QHBoxLayout()
        patent_lt.addLayout(local_lt)
        pixmap = QPixmap(image_path)
        imageBOX = QLabel()
        imageBOX.setPixmap(pixmap)
        imageBOX.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        imageBOX.setScaledContents(True)
        imageBOX.setFixedSize(icon_size_x, icon_size_y)
        btn = QPushButton(f"{btn_txt}")
        btn_font = btn.font()
        btn_font.setPointSize(font_size)
        btn.setFont(btn_font)
        btn.setMinimumHeight(icon_size_y)
        local_lt.addWidget(btn)
        local_lt.addWidget(imageBOX)
        return btn

    # =====================================================================================================================
    # ===================================================================================================================== LAYOUTY STRON
    # =====================================================================================================================

    # ========================================
    # Layout strony startowej
    # ========================================
    def welcome_page(self):
        # zmiana rozmiaru okna:
        self.set_window_size(window_width = 800, window_height = 600)
        self.setWindowTitle("SciFEA - welcome")
        # Definicja głównego widgetu strony
        widget = QWidget()
        # Layouty główne:
        main_layout = QHBoxLayout(widget)
        left_lt = QVBoxLayout()
        right_lt = QVBoxLayout()
        main_layout.addLayout(left_lt, stretch = 6)
        main_layout.addLayout(right_lt, stretch = 2)

        # lewy layout: wstawienie zdjęcia:
        main_logo_path = os.path.join(file_directory, f"assets/images/Logo_main.png")
        image_box = QLabel(self) # pojemnik na zdjęcie
        main_logo_image = QPixmap(main_logo_path) # obiekt grafiko w Qt
        image_box.setPixmap(main_logo_image) # wstrzyknięcie obiektu grafiki qt do widgetu
        # należy ustawić bezwzględne słuchanie podziału streach a nie rozmiaru w pikselach obrazu:
        image_box.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # Ta linijka sprawia, że obrazek dostosuje się do rozmiaru QLabel:
        image_box.setScaledContents(True)
        left_lt.addWidget(image_box)

        # Prawy layout:
        right_lt.addStretch()
        right_label = QLabel("Select working enviroment")
        right_label_font = right_label.font()
        right_label_font.setPointSize(12)
        right_label.setFont(right_label_font)
        right_lt.addWidget(right_label)
        new_project_btn = self.make_icon_btn_lt(patent_lt = right_lt, btn_txt = "New Project", font_size = 10, icon_size_x = 50, icon_size_y = 50, 
                                                image_path = os.path.join(images_path, r"New_project.png"))
        open_project_btn = self.make_icon_btn_lt(patent_lt = right_lt, btn_txt = "Open Project", font_size = 10, icon_size_x = 50, icon_size_y = 50, 
                                                        image_path = os.path.join(images_path, r"Open_project.png"))
        new_raw_mesh_btn = self.make_icon_btn_lt(patent_lt = right_lt, btn_txt = "New Raw mesh", font_size = 10, icon_size_x = 50, icon_size_y = 50, 
                                                        image_path = os.path.join(images_path, r"New_raw_mesh.png"))
        open_raw_mesh_btn = self.make_icon_btn_lt(patent_lt = right_lt, btn_txt = "Open Raw mesh", font_size = 10, icon_size_x = 50, icon_size_y = 50, 
                                                                image_path = os.path.join(images_path, r"Open_raw_mesh.png"))
        right_lt.addStretch()

        # Połączenia z dalszymi funkcjami:
        new_raw_mesh_btn.clicked.connect(self.new_mesh_route)
        open_raw_mesh_btn.clicked.connect(self.edit_mesh_route)
        open_project_btn.clicked.connect(lambda: self.PRJ_loader(get_dir = True))
        new_project_btn.clicked.connect(self.create_new_project_directory)

        return widget
    

    # ========================================
    # Layout strony menadżera projektu
    # ========================================
    def project_manager(self):
        widget = QWidget()
        # Layouty główne:
        main_layout = QHBoxLayout(widget)
        self.manager_left_lt = QVBoxLayout()
        self.manager_right_lt = QVBoxLayout()
        main_layout.addLayout(self.manager_left_lt, stretch = 5)
        main_layout.addLayout(self.manager_right_lt, stretch = 2)

        # powrót do głównego menu:
        back_to_welcome = QPushButton("Go back to welcome page")
        self.manager_right_lt.addWidget(back_to_welcome)
        back_to_welcome.clicked.connect(self.del_project_directories)
        back_to_welcome.clicked.connect(self.go_to_welcome_page)

        return widget


    # ========================================
    # Layout strony edycji siatki
    # ========================================
    def mesher_page(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)  # główny układ poziomy

        # Definicja głównego widgetu strony
        widget = QWidget()
        layout = QHBoxLayout(widget)
        # Layouty główne:
        left_panel = QWidget()
        center_panel = QWidget()
        right_panel = QWidget()
        self.mesher_left_layout = QVBoxLayout(left_panel)
        self.mesher_center_layout = QVBoxLayout(center_panel)
        right_layout = QVBoxLayout(right_panel)

        # Ustawienie proporcji layoutów:
        layout.addWidget(left_panel, 2)   # waga 1 – wąski
        layout.addWidget(center_panel, 7) # waga 4 – szeroki (4x więcej miejsca)
        layout.addWidget(right_panel, 1)  # waga 1 – wąski

        # Zawartość lewego layout:
        NodList_label = QLabel("Nodes list: ")
        NodList_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        ElList_label = QLabel("Elements list: ")
        ElList_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cancel_selection_btn = QPushButton("remove selection")
        self.mesher_left_layout.addStretch(1)
        self.mesher_left_layout.addWidget(NodList_label)
        self.mesher_left_layout.addWidget(ElList_label)
        self.mesher_left_layout.addWidget(cancel_selection_btn)
        # połączenia, widgety są insertowane przez oddzielną funkcję
        self.Node_list.clicked.connect(lambda: self.select_canvas_item(obj_type = "node"))
        self.EL_list.clicked.connect(lambda: self.select_canvas_item(obj_type = "element"))
        cancel_selection_btn.clicked.connect(lambda: self.select_canvas_item(cancel = True))

        # Środkowy panel (Canvas)
        canvas_label = QLabel("Mesh visualization")
        canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_font = canvas_label.font()
        label_font.setPointSize(12)
        canvas_label.setFont(label_font)
        # --- PASEK NARZĘDZI BIBLIOTEKI QT dla MatPlotLib---
        toolbar = NavigationToolbar(self.canvas, widget)
        self.mesher_center_layout.insertWidget(0, canvas_label)
        self.mesher_center_layout.insertWidget(1, toolbar)
        # umieszczanie canvas i CanvLabel, toolbar jest już powiązany z canvas
        self.mesher_center_layout.addWidget(self.canvas)
        

        # Prawy panel (przyciski)
        self.btn_new_node = QPushButton("New node")
        self.btn_edit_node = QPushButton("Edit node")
        self.btn_new_element = QPushButton("New element")
        self.btn_edit_element = QPushButton("Edit element")
        self.btn_material_manager = QPushButton("Material manager")
        self.btn_section_manager = QPushButton("Cross section manager")
        self.btn_symbols_manager = QPushButton("Symbols manager")
        self.btn_Canva = QPushButton("Canvas options")
        self.btn_Vedit = QPushButton("Visual object editor")
        self.btn_theme = QPushButton("Default theme (color)")
        # wykonuję funkcję aby domyślnie było czarne:
        self.change_theme()
        self.btn_validate = QPushButton("Validate mesh")
        self.btn_save_mesh = QPushButton("Save mesh file")
        self.btn_back = QPushButton("Go back to welcome page")
        # funkcja powrotu w zależności od nazwy guzika:
        def go_back():
            if self.btn_back.text() == "Go back to welcome page":
                self.go_to_welcome_page()
            elif self.btn_back.text() == "Go back to project manager":
                self.go_to_project_page()
        # Pozycjonowanie przycisków
        # Rozdzielenie na poniższe layouty aby moża było lepiej sterować rozciągnięciem
        physical_tools_layout = QVBoxLayout()
        physical_tools_layout.addWidget(QLabel("Node Tools"))
        physical_tools_layout.addWidget(self.btn_new_node)
        physical_tools_layout.addWidget(self.btn_edit_node)
        physical_tools_layout.addStretch()
        physical_tools_layout.addWidget(QLabel("Element Tools"))
        physical_tools_layout.addWidget(self.btn_new_element)
        physical_tools_layout.addWidget(self.btn_edit_element)
        physical_tools_layout.addStretch()
        visual_tools_layout = QVBoxLayout()
        visual_tools_layout.addWidget(QLabel("Display settings"))
        visual_tools_layout.addWidget(self.btn_Canva)
        visual_tools_layout.addWidget(self.btn_Vedit)
        visual_tools_layout.addWidget(self.btn_theme)
        visual_tools_layout.addStretch()
        self.data_dialogs_layout = QVBoxLayout()
        self.data_dialogs_layout.addWidget(QLabel("Property Managers"))
        self.data_dialogs_layout.addWidget(self.btn_section_manager)
        self.data_dialogs_layout.addWidget(self.btn_material_manager)
        file_validation_lt = QVBoxLayout()
        file_validation_lt.addWidget(QLabel("File & Validation"))
        file_validation_lt.addWidget(self.btn_validate)
        file_validation_lt.addWidget(self.btn_save_mesh)

            
        

        # Właściwe pozycjonowanie:
        right_layout.addStretch(1)
        right_layout.addLayout(physical_tools_layout, stretch = 6)
        right_layout.addStretch(1)
        right_layout.addLayout(self.data_dialogs_layout, stretch = 3)
        right_layout.addStretch(1) # Popchnięcie przycisku powrotu na sam dół
        right_layout.addLayout(visual_tools_layout, stretch = 3)
        right_layout.addStretch(1)
        right_layout.addLayout(file_validation_lt)
        right_layout.addStretch(1)
        right_layout.addWidget(self.btn_back)
        # Połączenia prawego layoutu:
        self.btn_new_node.clicked.connect(self.new_node_dialog)
        self.btn_edit_node.clicked.connect(self.edit_node_dialog)
        self.btn_new_element.clicked.connect(self.new_element_dialog)
        self.btn_edit_element.clicked.connect(self.edit_element_dialog)
        self.btn_Canva.clicked.connect(self.canvas_option_edit)
        self.btn_Vedit.clicked.connect(self.visual_OBJ_edit)
        self.btn_section_manager.clicked.connect(self.section_manager_dialog)
        self.btn_material_manager.clicked.connect(self.material_manager_dialog)
        self.btn_symbols_manager.clicked.connect(self.symbols_manager_dialog)
        self.btn_validate.clicked.connect(self.validate_dialog)
        self.btn_theme.clicked.connect(self.change_theme)
        self.btn_save_mesh.clicked.connect(self.save_mesh_dialog)
        self.btn_back.clicked.connect(go_back)
        self.btn_back.clicked.connect(self.canvas.delete_mesheditor_data)

        return widget


    # ========================================
    # Layout strony edycji siatki obciążeń
    # ========================================
    def load_mesher_page(self):
        # funkcja pomocnicza
        def make_label(parent_lt, text = "", font = 10):
                    label_widget = QLabel(f"{text}")
                    label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label_widget_font = label_widget.font()
                    label_widget_font.setPointSize(font)
                    label_widget.setFont(label_widget_font)
                    parent_lt.addWidget(label_widget)
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        # Layouty główne:
        left_panel = QWidget()
        center_panel = QWidget()
        right_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.load_mesher_center_layout = QVBoxLayout(center_panel)
        right_layout = QVBoxLayout(right_panel)

        # Ustawienie proporcji layoutów:
        layout.addWidget(left_panel, 2)   # waga 1 – wąski
        layout.addWidget(center_panel, 7) # waga 4 – szeroki (4x więcej miejsca)
        layout.addWidget(right_panel, 1)  # waga 1 – wąski

        # Zawartość lewego layout:
        # sekcja node loads:
        node_loads_lt = QVBoxLayout()
        make_label(node_loads_lt, "Node Loads", 12)
        self.node_load_list = QListWidget()
        node_loads_lt.addWidget(self.node_load_list)
        # sekcja obciążeń elementów:
        element_loads_lt = QVBoxLayout()
        make_label(element_loads_lt, "Element Loads", 12)
        self.element_load_list = QListWidget()
        element_loads_lt.addWidget(self.element_load_list)
        # sekcja obciążeń regionalnych:
        region_loads_lt = QVBoxLayout()
        make_label(region_loads_lt, "Region Loads", 12)
        self.region_load_list = QListWidget()
        region_loads_lt.addWidget(self.region_load_list)
        Reset_selection_btn = QPushButton("Reset selection")
        self.node_load_list.clicked.connect(lambda: self.select_canvas_item(obj_type = "node_loads"))
        self.element_load_list.clicked.connect(lambda: self.select_canvas_item(obj_type = "element_loads"))
        self.region_load_list.clicked.connect(lambda: self.select_canvas_item(obj_type = "region_loads"))
        Reset_selection_btn.clicked.connect(lambda: self.select_canvas_item(cancel = True))


        left_layout.addLayout(node_loads_lt)
        left_layout.addStretch()
        left_layout.addLayout(element_loads_lt)
        left_layout.addStretch()
        left_layout.addLayout(region_loads_lt)
        left_layout.addStretch()
        left_layout.addWidget(Reset_selection_btn)



        # Środkowy panel (Canvas)
        canvas_label = QLabel("Load Mesh visualization")
        label_font = canvas_label.font()
        label_font.setPointSize(12)
        canvas_label.setFont(label_font)
        canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar = NavigationToolbar(self.canvas, widget)
        self.load_mesher_center_layout.insertWidget(0, canvas_label, stretch = 1)
        self.load_mesher_center_layout.insertWidget(1, toolbar, stretch = 1)
        horizontal_lt_lists = QHBoxLayout()
        self.load_mesher_center_layout.insertLayout(2, horizontal_lt_lists, stretch = 2)
        self.Load_NodesListLt = QVBoxLayout()
        self.Load_NodesListLt.addWidget(QLabel("Nodes list:"))
        horizontal_lt_lists.addLayout(self.Load_NodesListLt)
        self.Load_ELListLt = QVBoxLayout()
        self.Load_ELListLt.addWidget(QLabel("Elements list:"))
        horizontal_lt_lists.addLayout(self.Load_ELListLt)


        # Prawy panel:
        # layout obciążeń:
        new_loads_lt = QVBoxLayout()
        make_label(new_loads_lt, "New Loads", 12)
        self.new_node_load_btn = QPushButton("New node load")
        self.new_element_load_btn = QPushButton("New element load")
        new_region_load_btn = QPushButton("New region load")
        new_loads_lt.addWidget(self.new_node_load_btn)
        new_loads_lt.addWidget(self.new_element_load_btn)
        new_loads_lt.addWidget(new_region_load_btn)

        self.new_node_load_btn.clicked.connect(self.Load_open_NewNodeForce)
        self.new_element_load_btn.clicked.connect(self.Load_open_NewElementLoad)
        new_region_load_btn.clicked.connect(self.Load_open_NewRegionLoad)

        # layout edycji:
        selection_edit_load_lt = QVBoxLayout()
        make_label(selection_edit_load_lt, "Edit selected load", 12)
        self.edit_SELload_btn = QPushButton("edit")
        selection_edit_load_lt.addWidget(self.edit_SELload_btn)
        self.edit_SELload_btn.clicked.connect(self.Load_load_editor_dialog)

        # Layout managere symboli:
        self.Load_symbol_mnager_lt = QHBoxLayout()
        self.Load_symbol_manager_btn = QPushButton("Symbols Manager")
        self.Load_symbol_mnager_lt.addWidget(self.Load_symbol_manager_btn)
        self.Load_symbol_manager_btn.clicked.connect(self.Load_open_symbols_manager)

        # Layout edycji wizualnej:
        visual_settings_lt = QVBoxLayout()
        make_label(visual_settings_lt, "Display settings", 12)
        canvas_settings_btn = QPushButton("Canvas / Visual settings")
        self.mesh_display_theme_btn = QPushButton("Mesh theme - classic")
        visual_settings_lt.addWidget(canvas_settings_btn)
        visual_settings_lt.addWidget(self.mesh_display_theme_btn)
        canvas_settings_btn.clicked.connect(self.Load_open_canvas_settings)
        self.mesh_display_theme_btn.clicked.connect(self.Load_change_mesh_theme)

        # Layout zapisania:
        writing_lt = QVBoxLayout()
        make_label(writing_lt, "Writing tools", 12)
        validate_btn = QPushButton("Validate load mesh")
        save_as_btn = QPushButton("Save load mesh")
        writing_lt.addWidget(validate_btn)
        writing_lt.addWidget(save_as_btn)
        save_as_btn.clicked.connect(self.Load_open_save_file_dialog)

        # przycisk powrotu
        back_to_prj_manager = QPushButton("Go back to project manager")
        back_to_prj_manager.clicked.connect(self.go_to_project_page)

        # pozycjonowanie:
        right_layout.addLayout(new_loads_lt)
        right_layout.addStretch()
        right_layout.addLayout(selection_edit_load_lt)
        right_layout.addStretch()
        right_layout.addLayout(self.Load_symbol_mnager_lt)
        right_layout.addStretch()
        right_layout.addLayout(visual_settings_lt)
        right_layout.addStretch()
        right_layout.addLayout(writing_lt)
        right_layout.addStretch()
        right_layout.addWidget(back_to_prj_manager)
        
        return widget


    # ========================================
    # Layout strony post processora
    # ========================================
    def postprocessor_page(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)  # główny układ poziomy

        return widget


    # ========================================================================================================================================
    # ========================================================================================================================================
    # ========================================================================================================================================
 
    # funkcje zmiany stron =================
    def go_to_welcome_page(self):
        self.stacked.setCurrentIndex(0)
        self.setWindowTitle("SciFEA - welcome")
        self.set_window_size(800, 600)

    def go_to_project_page(self):
        self.compose_prj_manager()
        self.stacked.setCurrentIndex(1)
        if hasattr(self, "prj_directories") and self.prj_directories is not None:
            try:
                project_name = os.path.basename(self.prj_directories["main"].strip().rstrip("_SciFEAprj"))
                self.setWindowTitle(f"Project Manager - {project_name}")
                self.set_window_size(800, 600)
            except Exception as e:
                print(f"{e}")

    def go_to_mesher_page(self, prj_manager = False):
        self.move_canvas_to(self.mesher_center_layout, self.mesher_left_layout, self.mesher_left_layout, stretch = 5)
        self.stacked.setCurrentIndex(2)
        self.set_window_size(1200, 600)
        self.select_canvas_item(obj_type = None, cancel = True)
        # wstawienie managera symboli:
        if self.data_type == "symbolic" and self.data_dialogs_layout.indexOf(self.btn_symbols_manager) == -1:
            self.data_dialogs_layout.addWidget(self.btn_symbols_manager)
            self.btn_symbols_manager.show()
        elif self.data_type == "numerical" and self.data_dialogs_layout.indexOf(self.btn_symbols_manager) != -1:
            self.data_dialogs_layout.removeWidget(self.btn_symbols_manager)
            self.btn_symbols_manager.setParent(None)
            self.btn_symbols_manager.hide()
        if prj_manager:
            self.btn_back.setText("Go back to project manager")
        else:
            self.btn_back.setText("Go back to welcome page")
        # czyszczenie list
        self.EL_list.clear()
        self.Node_list.clear()
    
    def go_to_load_mesher_page(self, load_name = "", parent_mesh = ""):
        self.move_canvas_to(self.load_mesher_center_layout, self.Load_NodesListLt, self.Load_ELListLt, insert = [1,1], stretch = 1)
        self.stacked.setCurrentIndex(3)
        self.set_window_size(1200, 600)
        self.setWindowTitle(f"Load Mesh Editor - {load_name} - {parent_mesh}")
        self.select_canvas_item(obj_type = None, cancel = True)
        self.mesh_display_theme_btn.setText("Mesh theme - classic")
        # wstawienie managera symboli:
        if self.data_type == "symbolic" and self.Load_symbol_mnager_lt.indexOf(self.Load_symbol_manager_btn) == -1:
            self.Load_symbol_mnager_lt.addWidget(self.Load_symbol_manager_btn)
            self.Load_symbol_manager_btn.show()
        elif self.data_type == "numerical" and self.Load_symbol_mnager_lt.indexOf(self.Load_symbol_manager_btn) != -1:
            self.Load_symbol_mnager_lt.removeWidget(self.Load_symbol_manager_btn)
            self.Load_symbol_manager_btn.setParent(None)
            self.Load_symbol_manager_btn.hide()

    def go_to_postprocessor_page(self):
        self.stacked.setCurrentIndex(4)
        self.setWindowTitle("SciFEA - welcome")
        self.set_window_size(800, 600)

    # przenoszenie widgetu canvas i list węzłów/elementów:
    def move_canvas_to(self, target_layout, list_widget_target_lt_1 = None, list_widget_target_lt_2 = None, insert = [2,4], stretch = 1):
        # 1. Usunięcie z dotychczasowych layoutów
        if self.canvas.parentWidget() and self.canvas.parentWidget().layout():
            self.canvas.parentWidget().layout().removeWidget(self.canvas)
        if list_widget_target_lt_1 and self.EL_list.parentWidget() and self.EL_list.parentWidget().layout():
            self.EL_list.parentWidget().layout().removeWidget(self.EL_list)
        if list_widget_target_lt_2 and self.Node_list.parentWidget() and self.Node_list.parentWidget().layout():
            self.Node_list.parentWidget().layout().removeWidget(self.Node_list)
                
        # 2. Wpięcie do nowego layoutu (Qt sam ustawi właściwego rodzica)
        target_layout.insertWidget(2, self.canvas, stretch = 10)
        if list_widget_target_lt_1:
            list_widget_target_lt_1.insertWidget(insert[0], self.Node_list, stretch = stretch)
        if list_widget_target_lt_2:
            list_widget_target_lt_2.insertWidget(insert[1], self.EL_list, stretch = stretch)

        # 3. Pokazanie i odświeżenie
        self.canvas.show()
        self.EL_list.show()
        self.Node_list.show()
    #=======================================

    # =========================================================================================== funkcje - MANAGER PROJEKTU
    # usuwanie ścieżki projektu:
    def del_project_directories(self):
        if hasattr(self, "prj_directories"):
            del self.prj_directories

    # funkcja tworzenia nowego projektu:
    def create_new_project_directory(self):
        main_directory = QFileDialog.getExistingDirectory(self, "Select new project directory")
        if main_directory is None:
            QMessageBox.critical(self, "Error", "Project directory was not selected")
            return
        else:
            # reszta kompetencji spoczywa na dialogu
            dialog = NewProjectDialog(self, directory = main_directory)
            dialog.exec()

    # ładowanie projektu:
    def PRJ_loader(self, get_dir = True, directory = ""):
        def check_directory_composition(main_dir = ""):
            # sprawdzenie czy projekt ma odpowiednią końcówkę:
            if not main_dir.endswith("_SciFEAprj"):
                QMessageBox.critical(self, "Invalid directory",
                                     "Main directory name should end with \"_SciFEAprj\"")
                return False
            loads_dir = os.path.join(main_dir, "Loads")
            results_dir = os.path.join(main_dir, "Results")
            list = os.listdir(main_dir)
            log_list = []
            if "Loads" not in list:
                os.makedirs(loads_dir)
                log_list.append("Project directory does not contain \"Loads\" folder\n - created new empty folder")
            if "Results" not in list:
                os.makedirs(results_dir)
                log_list.append("Project directory does not contain \"Results\" folder\n - created new empty folder")
            if log_list:
                dialog = ListReportLog(self, None, "Project loader warning", "", log_list)
                dialog.exec()
            self.prj_directories = {
                "main" : main_dir,
                "loads" : loads_dir,
                "results" : results_dir
            }
            return True

        if get_dir:
            main_directory = QFileDialog.getExistingDirectory(self, "Select project directory")
            if main_directory is None:
                QMessageBox.critical(self, "Error", "Project directory was not selected")
                return
        else:
            main_directory = directory

        if not check_directory_composition(main_directory):
            return
        else:
            self.go_to_project_page()
            return

    # kompozytor menagera projektu:
    def compose_prj_manager(self):
        # czyszczenie layoutów:
        def clear_layout(lt):
            try:
                lt = lt() if callable(lt) else lt
            except Exception:
                return
            if not lt:
                return
            while lt.count():
                item = lt.takeAt(0)
                widget = item.widget()
                layout = item.layout()
                if widget:
                    widget.deleteLater()
                elif layout:
                    clear_layout(layout)
                else:
                    del item

        # czyszczenie layoutów:
        clear_layout(lambda: self.prj_manager_file_lt["lt_mesh"])
        clear_layout(lambda: self.prj_manager_file_lt["lt_loads"])
        clear_layout(lambda: self.prj_manager_file_lt["lt_results"])
        clear_layout(lambda: self.prj_manager_sub_right_lt)

        def build_file_layout(parent_lt, label_txt = "", stretch_val = 1, insert = None):
            new_lt = QVBoxLayout()
            if insert:
                parent_lt.insertLayout(insert, new_lt, stretch = stretch_val)
            else:
                parent_lt.addLayout(new_lt, stretch = stretch_val)
            label = QLabel(f"{label_txt}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_font = label.font()
            label_font.setPointSize(14)
            label.setFont(label_font)
            new_lt.addWidget(label)
            return new_lt

        # tworzenie layoutów
        self.prj_manager_file_lt = {}
        self.prj_manager_file_lt["lt_mesh"] = build_file_layout(self.manager_left_lt, "======== MESH ========", stretch_val = 2)
        self.prj_manager_file_lt["lt_loads"] = build_file_layout(self.manager_left_lt, "======== LOADS ========", stretch_val = 5)
        self.prj_manager_file_lt["lt_results"] = build_file_layout(self.manager_left_lt, "======== RESULTS ========", stretch_val = 5)
        self.prj_manager_sub_right_lt = QVBoxLayout()
        self.manager_right_lt.insertLayout(0, self.prj_manager_sub_right_lt, stretch = 9)

        # flaga dla tworzenia prawego layoutu:
        self.mesh_lt_flag = False

        # Ustawienie layoutu siatki:
        def set_lt_mesh():
            No_mesh = False
            Multiple_mesh = False
            label_widget = self.prj_manager_file_lt["lt_mesh"].itemAt(0).widget()
            # Funkcja podświetlająca widget
            def set_widget_color(widget, flag = True,  alt_text = None):
                if flag:
                    widget.setStyleSheet("")
                else:
                    widget.setStyleSheet("background-color: red; color: white")
                if alt_text:
                    current_txt = widget.text()
                    widget.setText(f"{current_txt}\n{alt_text}")

            # zbieramy informację o plikach siatki:
            file_list = os.listdir(self.prj_directories["main"])
            mesh_file_list = []

            for name in file_list:
                if name.endswith("_msh.json"):
                    if not self.check_mesh_summary(summary_path = os.path.join(self.prj_directories["main"], name), MessageBox = False):
                        dump = os.path.join(self.prj_directories["main"], "mesh_dump")
                        if not os.path.exists(dump):
                            os.makedirs(dump)
                        new_name = os.path.join(dump, name)
                        os.replace(os.path.join(self.prj_directories["main"], name), new_name)
                    else:
                        mesh_file_list.append(name)

            # sprawdzenie czy odnaleziono plik listy
            if not mesh_file_list:
                No_mesh = True
            # sprawdzenie czy lista 
            elif len(mesh_file_list) > 1: 
                Multiple_mesh = True
            else:
                mesh_file_name = mesh_file_list[0]
                # przypisujemy odpowiednie odnośniki ścieżkowe poprzez mesh_summary check:
                self.check_mesh_summary(summary_path = os.path.join(self.prj_directories["main"], mesh_file_name), MessageBox = False)
                print(self.mesh_name)

            # funkcja budująca GUI dla jednego pliku siatki:
            def one_mesh_GUI():
                new_widget = QLabel(f"assigned mesh file: {mesh_file_name.strip().rstrip("_msh.json")}")
                font = new_widget.font()
                font.setPointSize(12)
                new_widget.setFont(font)
                new_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.prj_manager_file_lt["lt_mesh"].addWidget(new_widget)

            # funkcja budująca GUI dla braku pliku siatki ----------------- wymaga dialogu modyfikacji siatki
            def no_mesh_GUI():
                new_widget = QLabel(f"mesh file not assigned")
                new_widget.setStyleSheet("color: red")
                font = new_widget.font()
                font.setPointSize(12)
                new_widget.setFont(font)
                new_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                add_mesh_btn = QPushButton("Assign mesh")
                def open_MeshManager():
                    dialog = MeshManagerDialog(self, no_mesh = True)
                    dialog.exec()

                self.prj_manager_file_lt["lt_mesh"].addWidget(new_widget)
                self.prj_manager_file_lt["lt_mesh"].addWidget(add_mesh_btn)
                add_mesh_btn.clicked.connect(open_MeshManager)

            def multible_mesh_GUI():
                def manage_mesh_files():
                    # tworzenie folderu:
                    mesh_dump = os.path.join(self.prj_directories["main"], "mesh_dump")
                    if not os.path.exists(mesh_dump):
                        os.makedirs(mesh_dump)
                    list_item = mesh_list_widget.currentItem()
                    if not list_item:
                        QMessageBox.warning(self, "Invalid selection", "Mesh file not selected")
                        return
                    else:
                        selected_mesh = list_item.text()
                        for mesh_name in mesh_file_list:
                            if mesh_name != selected_mesh:
                                full_name = os.path.join(self.prj_directories["main"], mesh_name)
                                new_name = os.path.join(mesh_dump, mesh_name)
                                os.replace(full_name, new_name)
                    # restart gui:
                    self.compose_prj_manager()
                    
                new_widget = QLabel(f"multible mesh files found:")
                new_widget.setStyleSheet("color: red")
                font = new_widget.font()
                font.setPointSize(12)
                new_widget.setFont(font)
                new_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                mesh_list_widget = QListWidget()
                mesh_list_widget.addItems(mesh_file_list)
                bottom_lt = QHBoxLayout()
                bottom_lt.addWidget(QLabel("Select project mesh from the list above\n(Remaining mesh files will be moved to \"mesh_dump\")"))
                confirm_btn = QPushButton("assign selected mesh")
                bottom_lt.addWidget(confirm_btn)
                bottom_lt.addStretch()
                self.prj_manager_file_lt["lt_mesh"].addWidget(new_widget)
                self.prj_manager_file_lt["lt_mesh"].addWidget(mesh_list_widget)
                self.prj_manager_file_lt["lt_mesh"].addLayout(bottom_lt)
                confirm_btn.clicked.connect(manage_mesh_files)                  
            
            if not No_mesh and not Multiple_mesh:
                set_widget_color(label_widget, flag = True)
                one_mesh_GUI()
                self.mesh_lt_flag = True
            elif No_mesh:
                set_widget_color(label_widget, flag = True, alt_text = "(mesh file not assigned)")
                no_mesh_GUI()
            elif Multiple_mesh:
                set_widget_color(label_widget, flag = False, alt_text = "(project cannot contain multible mesh files)")
                multible_mesh_GUI()
            return
        
        set_lt_mesh()

        # Ustawienie layoutu siatek obciążeń:
        def set_lt_loads():
            # Pobieranie plików obciążenia
            self.prj_directories["load_files"] = {}
            loads_base_path = self.prj_directories["loads"]
            file_list = os.listdir(self.prj_directories["loads"])
            load_list = []
            for name in file_list:
                if name.endswith("_Lmsh.json"):
                    load_list.append(name.strip().rstrip("_Lmsh.json"))
                    self.prj_directories["load_files"][name.strip().rstrip("_Lmsh.json")] = os.path.join(loads_base_path, name)

            if not load_list:
                load_list_widget = QLabel("No load mesh files found")
                load_list_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                load_list_widget = QListWidget()
                load_list_widget.addItems(load_list)
            self.prj_manager_file_lt["lt_loads"].addWidget(load_list_widget)         
            return load_list_widget

        load_list_widget = set_lt_loads()

        def set_lt_results():
            dir_list = os.listdir(self.prj_directories["results"])
            self.prj_directories["results_dirs"] = {}
            result_dir_list = []
            for name in dir_list:
                if os.path.isdir(os.path.join(self.prj_directories["results"], name)):
                    result_dir_list.append(name)
                    full_path = os.path.join(self.prj_directories["results"], name)
                    self.prj_directories["results_dirs"][name] = full_path
            if not dir_list:
                results_list_widget = QLabel("No result directories found")
                results_list_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                results_list_widget = QListWidget()
                results_list_widget.addItems(result_dir_list)
            self.prj_manager_file_lt["lt_results"].addWidget(results_list_widget)  

            return results_list_widget
            
        results_list_widget = set_lt_results()

        # otwieranie menagera siatki:
        def open_projectManager(no_mesh = False):
            dialog = MeshManagerDialog(self, no_mesh = no_mesh)
            dialog.exec()
        # Ustawienie prawego layoutu:
        # Funkcja pomagająca:
        def make_btn_lt(parent_lt = None, label_txt = "", btn_txt = "", return_lt = False, add_stretch = True):
            btn_lt = QVBoxLayout()
            parent_lt.addLayout(btn_lt)
            label = QLabel(f"{label_txt}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_font = label.font()
            label_font.setPointSize(12)
            label.setFont(label_font)
            btn_lt.addWidget(label)
            btn = QPushButton(f"{btn_txt}")
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn_lt.addWidget(btn)
            if add_stretch:
                btn_lt.addStretch()
            if return_lt:
                return btn_lt, btn
            else:
                return btn

        if self.mesh_lt_flag:
            # Ustawienie przycisku dodanie siatki:
            open_meshManager_btn = make_btn_lt(self.prj_manager_sub_right_lt, "Mesh Actions", "Mesh manager")
            open_meshManager_btn.clicked.connect(lambda: open_projectManager(no_mesh = False))

            # Ustawienie przycisków dla siatki obciążeń
            loads_lt, new_load_mesh_btn = make_btn_lt(self.prj_manager_sub_right_lt, "Load Mesh", "New load mesh", return_lt = True, add_stretch = False)
            new_load_mesh_btn.clicked.connect(self.Load_open_new_loads_dialog)
            if self.prj_directories["load_files"]:
                def load_mesh_prelauncher(delete = False):
                    item = load_list_widget.currentItem()
                    if item and not delete:
                        text = item.text().strip()
                        self.launch_load_mesh_editor(self.prj_directories["load_files"][text])
                    elif item and delete:
                        text = item.text().strip()
                        decision = QMessageBox.information(self, "Confirm Load Mesh deletion", 
                                                       "Do you want to preceed with load mesh file removal?\nRemoved file cannot be restored, it will not appear in system's trash can directory",
                                                       QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                        if decision == QMessageBox.StandardButton.Ok:
                            os.remove(self.prj_directories["load_files"][text])
                            del self.prj_directories["load_files"][text]
                            self.compose_prj_manager()
                    else:
                        if delete:
                            QMessageBox.warning(self, "Cannot delete Load mesh", 
                                                "Load Mesh was not selected.\nChoose load mesh filename from \"==Loads==\" list.")
                        else:
                            QMessageBox.warning(self, "Cannot launch Load Mesh Editor", 
                                                "Load Mesh was not selected.\nChoose load mesh filename from \"==Loads==\" list.")
                        return

                edit_mesh_btn = QPushButton("Edit selected load mesh")
                delete_load_mesh_btn = QPushButton("Delete Load Mesh")
                delete_load_mesh_btn.setStyleSheet("background-color: red; color: white")
                loads_lt.addWidget(edit_mesh_btn)
                loads_lt.addWidget(delete_load_mesh_btn)
                loads_lt.addStretch()
                edit_mesh_btn.clicked.connect(load_mesh_prelauncher)
                delete_load_mesh_btn.clicked.connect(lambda: load_mesh_prelauncher(delete = True))
                
    # Funkcja assignowania wybranej siatki do projektu:
    def assign_selected_mesh_to_prj(self):
        assigned_mesh_path, _ = QFileDialog.getOpenFileName(self, "Select mesh JSON file", "", "(*.json)")
        if not assigned_mesh_path:
            return
        # sprawdzam czy wybrana siatka ma poprawne mesh_summary
        if self.check_mesh_summary(assigned_mesh_path):
            mesh_name = os.path.basename(assigned_mesh_path)
            try:
                os.rename(assigned_mesh_path, os.path.join(self.prj_directories["main"], mesh_name))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occured while moving mesh file:\n{e}")
                return

    # Funkcja sprawdzająca siatkę obciążeń:
    def check_load_summary(self, loads_path):
        # otwarcie pliku siatki obciążeń:
        try:
            with open(loads_path, "r", encoding="utf-8") as load_mesh:
                self.old_load_mesh = json.load(load_mesh)
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                                 f"An error occured while extracting \"{os.path.basename(loads_path)}\":\n{e}")
            return False
        # otwarto plik - sprawdzanie summary:
        try:
            load_name = self.old_load_mesh["load_summary"]["load_name"]
            parent_mesh = self.old_load_mesh["load_summary"]["parent_mesh"]
            if parent_mesh.rstrip() != self.mesh_name:
                found_mesh = " - Parent mesh was not found in mesh_dump"
                mesh_dump = os.path.join(self.prj_directories["main"], "mesh_dump")
                if os.path.exists(mesh_dump) and os.path.isdir(mesh_dump):
                    mesh_list = os.listdir(mesh_dump)
                    if parent_mesh in mesh_list:
                        found_mesh = " - Parent mesh found in \"mesh_dump\" folder.\nChange current mesh for project via \"Modify Mesh\" dialog"
                QMessageBox.critical(self, "Invalid Load mesh",
                                     f"Load Mesh parent mesh is not assigned as projects working mesh\n{found_mesh}")
                return False
            else:
                invalid_1 = invalid_2 = ""
                if self.mesh_element_layout_type != self.old_load_mesh["load_summary"]["mesh_type"]:
                    invalid_1 = f"Parent mesh topology ({self.mesh_element_layout_type})\nLoad mesh topology ({self.old_load_mesh["load_summary"]["mesh_type"]})"
                if self.data_type != self.old_load_mesh["load_summary"]["data_type"]:
                    invalid_2 = f"Parent mesh data type ({self.data_type})\nLoad mesh data type ({self.old_load_mesh["load_summary"]["data_type"]})"
                if invalid_1 or invalid_2:
                    QMessageBox.critical(self, "Invalid Load mesh summary", 
                                f"Load Mesh properties does not correspond to parent mesh:\n{invalid_1}\n{invalid_2}")
                    return False
                else:
                    self.load_mesh_full_path = loads_path
                    return True
        except Exception as e:
            QMessageBox.critical( self, f"Load Mesh file {os.path.basename(loads_path)} reading error",
                                    "Missing required loads summary keys:\n"
                                    f"{e}\n\n"
                                    "Expected layout:\n"
                                    "\"load_summary\": {\n"
                                    "    \"load_name\": \"name\",\n"
                                    "    \"parent_mesh\": \"mesh_name\",\n"
                                    "    \"data_type\": \"eg. symbolic / numerical\",\n"
                                    "    \"mesh_type\": \"eg. Parallel_Beam_Approach\"\n"
                                    "}")
            return False
    
    # Funkcja ładowania edytora siatki obciążeń:
    def launch_load_mesh_editor(self, loads_path):
        # Sprawdzenie czy siatka obciążeń jest poprawna:
        if self.check_load_summary(loads_path):
            # Sprawdzenie czy siatka jest poprawna i gotowa:
            try:
                self.canvas.unpack_mesh(mesh_dat = self.old_mesh, data_type = self.data_type, raporting = False)
            except Exception as e:
                QMessageBox.critical(self, "ERROR", f"Failed to unpack mesh file for validation:\n{e}")
                return
            if self.canvas.MASTER_validate(full_validation = False, float_converter = False, return_flag = True):
                # manager projektu podczas sprawdzania (check_mesh_summary) zapisał odpowiedni plik siatki, więc można nią wczytać
                self.setWindowTitle(f"Mesh editor - ({self.mesh_name})")
                self.go_to_load_mesher_page(load_name = os.path.basename(loads_path).rstrip(".json"), parent_mesh = self.mesh_name.rstrip(".json"))
                # odpalenie silnika:
                self.LoadsCore.unpack_load_mesh()
            else:
                print("cwelownia")
                return
        else:
            return

    # Funkcje działające po otworzeniu edytora obciążeń ===========

    # funkcja stylu rysowania siatki:
    def Load_change_mesh_theme(self):
        if self.mesh_display_theme_btn.text() == "Mesh theme - classic":
            self.mesh_display_theme_btn.setText("Mesh theme - simplistic")
            self.canvas.draw_simple_mesh()
            self.LoadsCore.draw_load_mesh()
            
        else:
            self.mesh_display_theme_btn.setText("Mesh theme - classic")
            self.canvas.clear_mesh()
            self.canvas.canvas_settings()
            self.canvas.draw_mesh(Raport_dialog = False)
            self.LoadsCore.draw_load_mesh()

    # wywoływanie dialogów:
    def Load_open_canvas_settings(self):
        dialog = CanvasOptionsDialog(self, self.canvas, load_mesh = True, LoadsCore = self.LoadsCore)
        dialog.exec()

    def Load_open_new_loads_dialog(self):
        dialog = NewLoadMesh(self)
        if dialog.exec() == QDialog.Accepted:
            self.compose_prj_manager()

    def Load_open_symbols_manager(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas, load_syms = True, LoadsCore = self.LoadsCore)
        dialog.exec()
    
    def Load_open_NewNodeForce(self):
        dialog = NodeLoadManager(self, canvas = self.canvas, LoadsCore = self.LoadsCore, mode = "add", obj_id = self.selected_mesh_obj["id"])
        dialog.exec()
    
    def Load_open_NewElementLoad(self):
        dialog = ElementLoadManager(parent = self, canvas = self.canvas, LoadsCore = self.LoadsCore, mode = "add", obj_id = self.selected_mesh_obj["id"])
        dialog.exec()

    def Load_open_NewRegionLoad(self):
        dialog = RegionLoadManager(parent = self, canvas = self.canvas, LoadsCore = self.LoadsCore, mode = "add")
        dialog.exec()
    
    def Load_open_save_file_dialog(self):
        dialog = SaveAsDialog(parent = self, canvas = self.canvas, load_mesh = True, LoadsCore = self.LoadsCore)
        dialog.exec()

    def Load_load_editor_dialog(self):
        if self.selected_mesh_obj["type"] == "node_loads":
            dialog = NodeLoadManager(parent = self, canvas = self.canvas, LoadsCore = self.LoadsCore, mode = "edit", obj_id = self.selected_mesh_obj["id"])
            dialog.exec()
        elif self.selected_mesh_obj["type"] == "element_loads":
            dialog = ElementLoadManager(parent = self, canvas = self.canvas, LoadsCore = self.LoadsCore, mode = "edit", obj_id = self.selected_mesh_obj["id"])
            dialog.exec()
        elif self.selected_mesh_obj["type"] == "region_loads":
            dialog = RegionLoadManager(parent = self, canvas = self.canvas, LoadsCore = self.LoadsCore, mode = "edit", obj_id = self.selected_mesh_obj["id"])
            dialog.exec()
        else:
            print("Unknown obj_type")
    # ===================================================================================================================

    # =========================================================================================== funkcje - EDYTOR SIATKI
    # funkcja ścieżki dla nowej siatki
    def new_mesh_route(self, file_path = None, prj_manager = False):
        # Pobranie lokalizacji nowego pliku:
        if not file_path:
            selected_file_path = QFileDialog.getExistingDirectory(self, "Choose new mesh file directory")
            if not selected_file_path:
                return
        else:
            selected_file_path = file_path
        
        dialog = NewMeshFile(self, selected_file_path)
        if dialog.exec() == QDialog.Accepted:
            # otwieranie okna edycji siatki:
            if prj_manager:
                self.go_to_mesher_page(prj_manager = True)
                self.prj_directories["mesh_path"] = os.path.join(self.prj_directories["main"], self.mesh_name)
            else:
                self.go_to_mesher_page()
            self.setWindowTitle(f"Mesh editor - ({self.mesh_name})")
            # inicjowanie słowników canvasa:
            self.canvas.initiate_new_mesh(data_type = self.data_type)

    # funkcja sprawdzająca mesh_summary i zwrcająca do Mainwindow parametry siatki (topologię, typ danych, nazwę ect.)
    def check_mesh_summary(self, summary_path, MessageBox = True):
        if summary_path.endswith("_Lmsh.json"):
            if MessageBox:
                QMessageBox.critical(self, "Wrong selection",
                                        "\"_Lmsh\" endings are reserved for load mesh")
            return False
        if not summary_path.endswith("_msh.json"):
            if MessageBox:
                QMessageBox.critical(self, "Invalid file suffix",
                                        "Mesh files must end with \"_msh\" suffix")
            return False
        supported_types = ("Parallel_Beam_Approach", "Generalized_Coordinate_Framing")
        supported_data = ("symbolic", "numerical")
        try:
            with open(summary_path, "r", encoding="utf-8") as mesh:
                self.old_mesh = json.load(mesh)
            try:
                summary = self.old_mesh["model_summary"]
                mesh_element_layout_type = summary["mesh_type"]
                data_type = summary["data_type"]
                mesh_name = summary["mesh_name"]
                log = ""
                if mesh_element_layout_type not in supported_types:
                    log += f"\nUnknown mesh type: {mesh_element_layout_type}\n supported types: {supported_types}"
                if data_type not in supported_data:
                    log += f"\nUnknown data type: {data_type}\n supported types: {supported_data}"
                if log != "":
                    QMessageBox.critical(self, "Invalid mesh model summary",
                                            f"{log}")
                    return False
                else:
                    self.mesh_element_layout_type = mesh_element_layout_type
                    self.data_type = data_type
                    self.full_mesh_path = summary_path
                    self.mesh_name = os.path.basename(self.full_mesh_path)
                    return True
            except Exception as e:
                QMessageBox.critical(self, f"Mesh file {os.path.basename(summary_path)} reading error",
                                    "Missing required model summary keys:\n"
                                    f"{e}\n"
                                    "Expected layout:\n"
                                    "\"model_summary\": {\n"
                                    "\"mesh_type\": \"eg. Parallel_Beam_Approach\",\n"
                                    "\"mesh_name\": \"name\",\n"
                                    "\"data_type\": \"eg. symbolic\"}")            
                return False
                
        except Exception as e:
            QMessageBox.critical(self, "Mesh file summary reading error",
                                                "error log:\n"
                                                f"{e}")
            return False
    
    # funkcja ścieżki dla edycji siatki                                                                 # FUNKCJE WCZYTUJĄCE SIATKĘ DLA MANAGER PROJEKTU
    def edit_mesh_route(self, file_path = None, prj_manager = False):
        # okno pobrania pliku, jeżeli nie jest otwierany przez managera
        if not file_path:
            selected_path, _ = QFileDialog.getOpenFileName(self, "Select mesh JSON file", "", "(*.json)") # trzeba bobrać dwie wartości nie samo file_path
            if not selected_path:
                return
        else:
            selected_path = file_path
        # sprawdzenie czy summary jest poprawne:
        if self.check_mesh_summary(selected_path):
            try:
                self.go_to_mesher_page(prj_manager = prj_manager)
                self.canvas.unpack_mesh(mesh_dat = self.old_mesh, data_type = self.data_type)
                self.setWindowTitle(f"Mesh editor - ({self.mesh_name})")
            except Exception as e:
                if prj_manager:
                    self.go_to_project_page()
                else:
                    self.go_to_welcome_page()
                QMessageBox.critical(self, "Mesh file reading error",
                                        "error log:\n"
                                        f"{e}\n")
                return

    # funkcja zmiany domyślnego wyglądu EDYTOR SIATKI
    def change_theme(self):
        if self.btn_theme.text().endswith("(color)"):
            self.btn_theme.setText("Default theme (black)")
            # =========================
            # DARK THEME
            # =========================

            # elementy:
            self.canvas.element_type['2N4DOF_EB']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N4DOF_EB']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N6DOF_EB_Q']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N6DOF_EB_Q']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N4DOF_T_EX']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N4DOF_T_EX']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N4DOF_T_FI']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N4DOF_T_FI']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N4DOF_T_RI']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N4DOF_T_RI']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N2DOF_Bar']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N2DOF_Bar']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['Spring']['v_params']['element_color'] = "black"

            self.canvas.element_type['2N4DOF_Truss']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N4DOF_Truss']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['Spring_2D']['v_params']['element_color'] = "black"

            self.canvas.element_type['2N6DOF_EB']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N6DOF_EB']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N6DOF_T_EX']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N6DOF_T_EX']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N6DOF_T_FI']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N6DOF_T_FI']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N6DOF_T_RI']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N6DOF_T_RI']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['2N8DOF_EB_Q']['v_params']['element_color'] = "black"
            self.canvas.element_type['2N8DOF_EB_Q']['v_params']['symbol_color'] = "black"

            self.canvas.element_type['unknown_element']['v_params']['element_color'] = "black"
            self.canvas.element_type['unknown_element']['v_params']['symbol_color'] = "black"

            # podpory / węzły:
            # marker_face_color celowo pominięte — pozostaje białe
            self.canvas.support_type['Free']['v_params']['marker_color'] = "black"

            self.canvas.support_type['fix_rot']['v_params']['marker_color'] = "black"

            self.canvas.support_type['pinned_support']['v_params']['support_color'] = "black"
            self.canvas.support_type['pinned_support']['v_params']['marker_color'] = "black"

            self.canvas.support_type['roller_support_fixX']['v_params']['support_color'] = "black"
            self.canvas.support_type['roller_support_fixX']['v_params']['marker_color'] = "black"

            self.canvas.support_type['roller_support_fixZ']['v_params']['support_color'] = "black"
            self.canvas.support_type['roller_support_fixZ']['v_params']['marker_color'] = "black"

            self.canvas.support_type['FIXED_support']['v_params']['support_color'] = "black"
            self.canvas.support_type['FIXED_support']['v_params']['marker_color'] = "black"

            self.canvas.support_type['rollerFIX_support_fixX']['v_params']['support_color'] = "black"
            self.canvas.support_type['rollerFIX_support_fixX']['v_params']['marker_color'] = "black"

            self.canvas.support_type['rollerFIX_support_fixZ']['v_params']['support_color'] = "black"
            self.canvas.support_type['rollerFIX_support_fixZ']['v_params']['marker_color'] = "black"

            self.canvas.support_type['unknown_support']['v_params']['support_color'] = "black"
            self.canvas.support_type['unknown_support']['v_params']['marker_color'] = "black"

        elif self.btn_theme.text().endswith("(black)"):
            self.btn_theme.setText("Default theme (color)")
            # =========================
            # LIGHT THEME / POWRÓT DO KOLORÓW
            # =========================

            # elementy:
            self.canvas.element_type['2N4DOF_EB']['v_params']['element_color'] = "green"
            self.canvas.element_type['2N4DOF_EB']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N6DOF_EB_Q']['v_params']['element_color'] = "green"
            self.canvas.element_type['2N6DOF_EB_Q']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N4DOF_T_EX']['v_params']['element_color'] = "green"
            self.canvas.element_type['2N4DOF_T_EX']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N4DOF_T_FI']['v_params']['element_color'] = "green"
            self.canvas.element_type['2N4DOF_T_FI']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N4DOF_T_RI']['v_params']['element_color'] = "green"
            self.canvas.element_type['2N4DOF_T_RI']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N2DOF_Bar']['v_params']['element_color'] = "blue"
            self.canvas.element_type['2N2DOF_Bar']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['Spring']['v_params']['element_color'] = "black"

            self.canvas.element_type['2N4DOF_Truss']['v_params']['element_color'] = "blue"
            self.canvas.element_type['2N4DOF_Truss']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['Spring_2D']['v_params']['element_color'] = "black"

            self.canvas.element_type['2N6DOF_EB']['v_params']['element_color'] = "blue"
            self.canvas.element_type['2N6DOF_EB']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N6DOF_T_EX']['v_params']['element_color'] = "blue"
            self.canvas.element_type['2N6DOF_T_EX']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N6DOF_T_FI']['v_params']['element_color'] = "blue"
            self.canvas.element_type['2N6DOF_T_FI']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N6DOF_T_RI']['v_params']['element_color'] = "blue"
            self.canvas.element_type['2N6DOF_T_RI']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['2N8DOF_EB_Q']['v_params']['element_color'] = "blue"
            self.canvas.element_type['2N8DOF_EB_Q']['v_params']['symbol_color'] = "green"

            self.canvas.element_type['unknown_element']['v_params']['element_color'] = "red"
            self.canvas.element_type['unknown_element']['v_params']['symbol_color'] = "red"

            # podpory / węzły:
            self.canvas.support_type['Free']['v_params']['marker_color'] = "green"
            self.canvas.support_type['Free']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['fix_rot']['v_params']['marker_color'] = "gray"
            self.canvas.support_type['fix_rot']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['pinned_support']['v_params']['support_color'] = "blue"
            self.canvas.support_type['pinned_support']['v_params']['marker_color'] = "blue"
            self.canvas.support_type['pinned_support']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['roller_support_fixX']['v_params']['support_color'] = "blue"
            self.canvas.support_type['roller_support_fixX']['v_params']['marker_color'] = "blue"
            self.canvas.support_type['roller_support_fixX']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['roller_support_fixZ']['v_params']['support_color'] = "blue"
            self.canvas.support_type['roller_support_fixZ']['v_params']['marker_color'] = "blue"
            self.canvas.support_type['roller_support_fixZ']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['FIXED_support']['v_params']['support_color'] = "blue"
            self.canvas.support_type['FIXED_support']['v_params']['marker_color'] = "blue"
            self.canvas.support_type['FIXED_support']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['rollerFIX_support_fixX']['v_params']['support_color'] = "blue"
            self.canvas.support_type['rollerFIX_support_fixX']['v_params']['marker_color'] = "blue"
            self.canvas.support_type['rollerFIX_support_fixX']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['rollerFIX_support_fixZ']['v_params']['support_color'] = "blue"
            self.canvas.support_type['rollerFIX_support_fixZ']['v_params']['marker_color'] = "blue"
            self.canvas.support_type['rollerFIX_support_fixZ']['v_params']['marker_face_color'] = "white"

            self.canvas.support_type['unknown_support']['v_params']['support_color'] = "red"
            self.canvas.support_type['unknown_support']['v_params']['marker_color'] = "red"
            self.canvas.support_type['unknown_support']['v_params']['marker_face_color'] = "white"
    
    def visual_OBJ_edit(self):
        dialog = VisualObjEditDialog(self, self.canvas) # PRZEKAZUJEMY self.canvas
        dialog.exec()

    def canvas_option_edit(self):
        dialog = CanvasOptionsDialog(self, self.canvas)
        dialog.exec()

    def new_node_dialog(self):
        dialog = NewNodeDialog(self, self.canvas)
        dialog.exec()

    def edit_node_dialog(self):
        dialog = EditNodeDialog(self, self.canvas)
        dialog.exec()

    def new_element_dialog(self):
        dialog = NewElementDialog(self, self.canvas)
        dialog.exec()

    def edit_element_dialog(self):
        dialog = EditElementDialog(self, self.canvas)
        dialog.exec()

    def material_manager_dialog(self):
        dialog = MaterialManager(self, self.canvas)
        dialog.exec()

    def section_manager_dialog(self):
        dialog = SectionManager(self, self.canvas)
        dialog.exec()

    def symbols_manager_dialog(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas)
        dialog.exec()
    
    def save_mesh_dialog(self):
        dialog = SaveAsDialog(self, self.canvas)
        dialog.exec()

    def validate_dialog(self):
        dialog = ValidationDialog(self, self.canvas)
        dialog.exec()
    
    # Funkcja zaznaczenia obiektu:
    def select_canvas_item(self, obj_type = None, cancel = False):
        def clear_nonLoad():
            self.Node_list.clearSelection()
            self.EL_list.clearSelection()
            if self.stacked.currentIndex() == 3:
                self.new_element_load_btn.setShortcut(QKeySequence(""))
                self.new_element_load_btn.setEnabled(False)
                self.new_element_load_btn.setDefault(False)
                #
                self.new_node_load_btn.setShortcut(QKeySequence(""))
                self.new_node_load_btn.setEnabled(False)
                self.new_node_load_btn.setDefault(False)

        if obj_type == "node":
            obj_id = self.Node_list.currentRow() + 1
            self.selected_mesh_obj = {"type" : obj_type, "id" : obj_id}
            self.EL_list.clearSelection()
            if self.stacked.currentIndex() == 3:
                self.node_load_list.clearSelection()
                self.element_load_list.clearSelection()
                self.region_load_list.clearSelection()
                # nowy element
                self.new_node_load_btn.setShortcut(QKeySequence("Return"))
                self.new_node_load_btn.setEnabled(True)
                self.new_node_load_btn.setDefault(True)
                # nowy węzeł
                self.new_element_load_btn.setShortcut(QKeySequence(""))
                self.new_element_load_btn.setEnabled(False)
                self.new_element_load_btn.setDefault(False)
                # modyfikacja obciążenia:
                self.edit_SELload_btn.setShortcut(QKeySequence(""))
                self.edit_SELload_btn.setEnabled(False)
                self.edit_SELload_btn.setDefault(False)
                #
                self.node_load_list.clearSelection()
                self.element_load_list.clearSelection()
                self.region_load_list.clearSelection()

        elif obj_type == "element":
            obj_id = self.EL_list.currentRow() + 1
            self.selected_mesh_obj = {"type" : obj_type, "id" : obj_id}
            self.Node_list.clearSelection()
            if self.stacked.currentIndex() == 3:
                self.node_load_list.clearSelection()
                self.element_load_list.clearSelection()
                self.region_load_list.clearSelection()
                #
                self.new_node_load_btn.setShortcut(QKeySequence(""))
                self.new_node_load_btn.setEnabled(False)
                self.new_node_load_btn.setDefault(False)
                # element
                self.new_element_load_btn.setShortcut(QKeySequence("Return"))
                self.new_element_load_btn.setEnabled(True)
                self.new_element_load_btn.setDefault(True)
                #
                self.edit_SELload_btn.setShortcut(QKeySequence(""))
                self.edit_SELload_btn.setEnabled(False)
                self.edit_SELload_btn.setDefault(False)
                #
                self.node_load_list.clearSelection()
                self.element_load_list.clearSelection()
                self.region_load_list.clearSelection()              

        elif obj_type == "node_loads":
            item = self.node_load_list.currentItem()
            obj_id = item.text().split(";")[0]
            self.selected_mesh_obj = {"type" : obj_type, "id" : obj_id}
            clear_nonLoad()
            self.edit_SELload_btn.setShortcut(QKeySequence("Return"))
            self.edit_SELload_btn.setEnabled(True)
            self.edit_SELload_btn.setDefault(True) 
            #
            self.element_load_list.clearSelection()
            self.region_load_list.clearSelection()

        elif obj_type == "element_loads":
            item = self.element_load_list.currentItem()
            obj_id = item.text().split(";")[0]
            self.selected_mesh_obj = {"type" : obj_type, "id" : obj_id}
            clear_nonLoad()
            self.edit_SELload_btn.setShortcut(QKeySequence("Return"))
            self.edit_SELload_btn.setEnabled(True)
            self.edit_SELload_btn.setDefault(True)
            #
            self.node_load_list.clearSelection()
            self.region_load_list.clearSelection() 

        elif obj_type == "region_loads":
            item = self.region_load_list.currentItem()
            obj_id = item.text().split(";")[0]
            self.selected_mesh_obj = {"type" : obj_type, "id" : obj_id}
            clear_nonLoad()
            self.edit_SELload_btn.setShortcut(QKeySequence("Return"))
            self.edit_SELload_btn.setEnabled(True)
            self.edit_SELload_btn.setDefault(True)
            #
            self.node_load_list.clearSelection()
            self.element_load_list.clearSelection()

        else:
            obj_id = None
            self.selected_mesh_obj = None
            clear_nonLoad()
            self.edit_SELload_btn.setShortcut(QKeySequence(""))
            self.edit_SELload_btn.setEnabled(False)
            self.edit_SELload_btn.setDefault(False)
            #
            self.node_load_list.clearSelection()
            self.element_load_list.clearSelection()
            self.region_load_list.clearSelection() 
            
        self.canvas.draw_OBJ_selection(obj_type, obj_id, cancel)
        self.LoadsCore.draw_load_selection(obj_type, obj_id, cancel)
    # ===================================================================================================================


# ====================================================================================
# ==================================================================================== KLASY EDYTORA SIATKI OBCIĄŻEŃ

# ======================================== 
# Dialog okna tworzenia nowego projektu
# ======================================== EDYTOR OBCIĄŻEŃ
class NewLoadMesh(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.MainWindow = parent
        self.setWindowTitle("New Load mesh")
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        Mesh_params_label = QLabel("Parent Mesh parameters:")
        Mesh_params_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_font = Mesh_params_label.font()
        label_font.setPointSize(12)
        Mesh_params_label.setFont(label_font)
        main_layout.addWidget(Mesh_params_label)
        def make_param_line_lt(parent_lt, text_1 = "", text_2 = ""):
            local_lt = QHBoxLayout()
            parent_lt.addLayout(local_lt)
            local_lt.addWidget(QLabel(f"{text_1}"))
            local_lt.addWidget(QLabel(f"{text_2}"))
            local_lt.addStretch()

        make_param_line_lt(main_layout, "Name: ", self.MainWindow.mesh_name)
        make_param_line_lt(main_layout, "Data type: ", self.MainWindow.data_type)
        make_param_line_lt(main_layout, "Topology: ", self.MainWindow.mesh_element_layout_type)

        # podawanie nazwy
        main_layout.addStretch()
        local_h_lt = QHBoxLayout()
        main_layout.addLayout(local_h_lt)
        local_h_lt.addWidget(QLabel("Load Mesh name: "))
        self.name_line = QLineEdit("")
        local_h_lt.addWidget(self.name_line)
        confirm_btn = QPushButton("create load mesh")
        local_h_lt.addWidget(confirm_btn)

        confirm_btn.clicked.connect(self.make_loads_file)

    def make_loads_file(self):
        load_name = self.name_line.text()
        if load_name.strip() == "":
            QMessageBox.warning(self, "Invalid Load Mesh name", "Load mesh name was not provided")
            return
        full_loads_path = os.path.join(self.MainWindow.prj_directories["loads"], f"{load_name}_Lmsh.json")
        load_summary = {
                        "load_name" : load_name,
                        "parent_mesh" : self.MainWindow.mesh_name,
                        "data_type" : self.MainWindow.data_type,
                        "mesh_type" : self.MainWindow.mesh_element_layout_type
                        }
        if self.MainWindow.data_type == "symbolic":
            json_dump = {"load_summary": load_summary,
                         "load_symbol_substitutes": {},
                         "node_loads": {},
                         "element_loads": {},
                         "region_loads": {}}
        else:
            json_dump = {"load_summary": load_summary,
                         "node_loads": {},
                         "element_loads": {},
                         "region_loads": {}}

        # zapis:
        try:
            with open(full_loads_path, "x", encoding="utf-8") as load_mesh:
                json.dump(json_dump, load_mesh, indent = 4)
                self.accept()
                return
        except Exception as e:
            QMessageBox.critical(self, "ERROR", 
                                 f"An error occured while saving Load mesh file:\n{e}")
            return


# ======================================== 
# Dialog okna manipulcaji obciążeniem węzła
# ======================================== EDYTOR OBCIĄŻEŃ
class NodeLoadManager(QDialog):
    def __init__(self, parent = None, canvas = None, LoadsCore = None, mode = "add", obj_id = None):
        super().__init__(parent)
        
        self.MainWindow = parent
        self.canvas = canvas
        self.LoadsCore = LoadsCore
        self.dialog_mode = mode
        self.dict_id = obj_id

        if mode == "add":
            title = "New Node Load"
            label_txt = f"Apply force to Node ID: {self.dict_id}"
            apply_txt = "Apply force"
        else:
            title = "Edit Node Load"
            label_txt = f"Edit force id: {self.dict_id}, Node ID: {self.LoadsCore.get_meshOBJ_id(self.dict_id)}"
            apply_txt = "Apply changes"

        self.setWindowTitle(f"{title}")
        self.setModal(False)
        
        main_lt = QVBoxLayout(self)
        self.main_label = QLabel(f"{label_txt}")
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_label_font = self.main_label.font()
        main_label_font.setPointSize(12)
        self.main_label.setFont(main_label_font)
        main_lt.addWidget(self.main_label)
        self.main_v_lt = QVBoxLayout()
        main_lt.addLayout(self.main_v_lt)

        self.build_GUI()

        bottom_lt = QHBoxLayout()
        main_lt.addLayout(bottom_lt)
        self.apply_btn = QPushButton(f"{apply_txt}")
        apply_close = QPushButton("Apply & Close")
        apply_close.setDefault(True)
        close_btn = QPushButton("Close")
        bottom_lt.addWidget(self.apply_btn)
        bottom_lt.addWidget(apply_close)
        bottom_lt.addWidget(close_btn)
        close_btn.clicked.connect(self.close_dialog)
        apply_close.clicked.connect(self.save_close)
        self.apply_btn.clicked.connect(self.save_changes)

    def Refresh_GUI(self):
        # funkcja usuwająca widgety i layouty:
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item
        clear_layout(self.main_v_lt)
        self.build_GUI()

    def build_GUI(self):
        load_input_types = ["Components (Fx, Fz, My)", "Force, Angle & Moment"]
        def make_horizontal_lt(parent_lt = None,  widget_type = QLineEdit(), label_txt = "", stretch = True):
            local_lt = QHBoxLayout()
            parent_lt.addLayout(local_lt)
            local_lt.addWidget(QLabel(f"{label_txt}"))
            new_widget = widget_type
            local_lt.addWidget(new_widget)
            if stretch:
                local_lt.addStretch()
            return new_widget

        # Tworzenie wyboru typu podania siły:
        self.force_method_box = make_horizontal_lt(self.main_v_lt, QComboBox(), "Input method: ")
        self.force_method_box.addItems(load_input_types)
        if hasattr(self, 'selected_input') and self.selected_input is not None:
            self.force_method_box.setCurrentText(self.selected_input)

        # Metoda "Components (Fx, Fz, My)"
        if self.force_method_box.currentText() == "Components (Fx, Fz, My)":
            if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                x_widget = QLabel("0 - (PBA topology)")
            else:
                x_widget = QLineEdit()
            self.X_line = make_horizontal_lt(self.main_v_lt, widget_type = x_widget, label_txt = "X: ")
            self.Z_line = make_horizontal_lt(self.main_v_lt, widget_type = QLineEdit(), label_txt = "Z: ")
            self.RY_line = make_horizontal_lt(self.main_v_lt, widget_type = QLineEdit(), label_txt = "RY: ")

        elif self.force_method_box.currentText() == "Force, Angle & Moment":
            if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                angle_widget = QLabel("90 - (PBA topology)")
            else:
                angle_widget = QLineEdit()
            self.Force_line = make_horizontal_lt(self.main_v_lt, widget_type = QLineEdit(), label_txt = "Force: ")
            self.Angle_line = make_horizontal_lt(self.main_v_lt, widget_type = angle_widget, label_txt = "Angle (deg): ")
            self.RY_line = make_horizontal_lt(self.main_v_lt, widget_type = QLineEdit(), label_txt = "RY: ")

        self.fill_LineEdits()

        if self.dialog_mode == "edit":
            delete_btn = make_horizontal_lt(self.main_v_lt, widget_type = QPushButton("Delete"), label_txt = "Delete load: ")
            delete_btn.setStyleSheet("background-color: red; color: white")
            delete_btn.clicked.connect(lambda: self.save_changes(delete = True))
        # inicjowanie zmiany gui:
        def change_input():
            self.selected_input = self.force_method_box.currentText()
            self.Refresh_GUI()

        self.force_method_box.currentTextChanged.connect(change_input)

    def fill_LineEdits(self):
        if self.dialog_mode == "add":
            return
        if self.force_method_box.currentText() == "Components (Fx, Fz, My)":
            if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                self.Z_line.setText(f"{self.LoadsCore.node_loads[self.dict_id]["Z"]}")
                a, b = self.val_highlight(self.Z_line, "force")
            else:
                self.X_line.setText(f"{self.LoadsCore.node_loads[self.dict_id]["X"]}")
                a, b = self.val_highlight(self.X_line, "force")
                self.Z_line.setText(f"{self.LoadsCore.node_loads[self.dict_id]["Z"]}")
                a, b = self.val_highlight(self.Z_line, "force")
            self.RY_line.setText(f"{self.LoadsCore.node_loads[self.dict_id]["RY"]}")
            a, b = self.val_highlight(self.RY_line, "moment_of_force")

        elif self.force_method_box.currentText() == "Force, Angle & Moment":
            if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                self.Force_line.setText(f"{self.LoadsCore.node_loads[self.dict_id]["Z"]}")
                a, b = self.val_highlight(self.Force_line, "force")
            else:
                flag_list = []
                X_val, flag = self.LoadsCore.validate_val(self.LoadsCore.node_loads[self.dict_id]["X"], "force", True)
                flag_list.append(flag)
                Z_val, flag = self.LoadsCore.validate_val(self.LoadsCore.node_loads[self.dict_id]["Z"], "force", True)
                flag_list.append(flag)
                if False in flag_list:
                    self.Force_line.setText(f"X: {self.LoadsCore.node_loads[self.dict_id]["X"]}, Z: {self.LoadsCore.node_loads[self.dict_id]["Z"]}    ???")
                    self.Angle_line.setText(f"X: {self.LoadsCore.node_loads[self.dict_id]["X"]}, Z: {self.LoadsCore.node_loads[self.dict_id]["Z"]}    ???")
                else:
                    angle = np.rad2deg(np.arctan2(Z_val, X_val))
                    force = np.hypot(Z_val, X_val)
                    self.Force_line.setText(f"{force}")
                    self.Angle_line.setText(f"{angle}")
                               
                a, b = self.val_highlight(self.Force_line, "force")
                a, b = self.val_highlight(self.Angle_line, "angle")

            self.RY_line.setText(f"{self.LoadsCore.node_loads[self.dict_id]["RY"]}")
            a, b = self.val_highlight(self.RY_line, "moment_of_force")

    def val_highlight(self, widget, sym_key):
        value = widget.text()
        if value.strip() == "":
            widget.setStyleSheet("")
            return 0, True 
        abs_val, flag = self.LoadsCore.validate_val(val = value, sym_key = sym_key, flag = True)
        if flag:
            widget.setStyleSheet("")
            return abs_val, flag
        else:
            widget.setStyleSheet("background-color: red; color: white")
            return abs_val, flag
    
    def convert_to_vector(self):
        def flagged(main_flag, flag):
            if not main_flag:
                return False
            elif main_flag and not flag:
                return False
            elif main_flag and flag:
                return True

        convertion_flag = True
        if self.force_method_box.currentText() == "Components (Fx, Fz, My)":
            if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                X_val = 0
            else:
                X_val, flag = self.val_highlight(widget = self.X_line, sym_key = "force")
                convertion_flag = flagged(convertion_flag, flag)
            Z_val, flag = self.val_highlight(widget = self.Z_line, sym_key = "force")
            convertion_flag = flagged(convertion_flag, flag)
            RY_val, flag = self.val_highlight(widget = self.RY_line, sym_key = "moment_of_force")
            convertion_flag = flagged(convertion_flag, flag)
            if self.MainWindow.data_type == "symbolic":
                if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                    X_val = "0"
                else:
                    X_val = self.X_line.text() if self.X_line.text().strip() != "" else "0"
                Z_val = self.Z_line.text() if self.Z_line.text().strip() != "" else "0"
                RY_val = self.RY_line.text() if self.RY_line.text().strip() != "" else "0"

        elif self.force_method_box.currentText() == "Force, Angle & Moment":
            if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                X_val = 0
                Z_val, flag = self.val_highlight(widget = self.Force_line, sym_key = "force")
                convertion_flag = flagged(convertion_flag, flag)
            else:
                f_angle, flag = self.val_highlight(widget = self.Angle_line, sym_key = "angle")
                convertion_flag = flagged(convertion_flag, flag)
                Force, flag = self.val_highlight(widget = self.Force_line, sym_key = "force")
                convertion_flag = flagged(convertion_flag, flag)
                if convertion_flag:
                    if self.MainWindow.data_type == "symbolic":
                        Force_str = "0" if self.Force_line.text().strip() == "" else self.Force_line.text()
                        print(Force_str)
                        # Dokładny kąt w radianach:
                        angle_round = round(f_angle, 6)
                        angle_sym = sp.Rational(str(angle_round))
                        angle_rad = angle_sym / 180 * sp.pi
                        try:
                            Force_str = sp.sympify(Force_str, locals = sympy_LOCAL)
                            X_str = str(sp.cos(angle_rad) * Force_str)
                            Z_str = str(sp.sin(angle_rad) * Force_str)
                        except Exception:
                            X_str = f"{str(sp.cos(angle_rad))}*{Force_str}"
                            Z_str = f"{str(sp.sin(angle_rad))}*{Force_str}"

                        X_val = X_str
                        Z_val = Z_str
                    else:
                        X_val = np.cos(np.deg2rad(f_angle)) * Force
                        Z_val = np.sin(np.deg2rad(f_angle)) * Force

            RY_val, flag = self.val_highlight(widget = self.RY_line, sym_key = "moment_of_force")
            convertion_flag = flagged(convertion_flag, flag)
            if self.MainWindow.data_type == "symbolic":
                if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                    X_val = "0"
                    Z_val = self.Force_line.text()
                RY_val = "0" if self.RY_line.text().strip() == "" else self.RY_line.text()

        if convertion_flag:
            return {"X": X_val, "Z": Z_val, "RY": RY_val}
        else:
            return False

    def save_changes(self, delete = False):
        vector = self.convert_to_vector()
        if not vector:
            QMessageBox.warning(self, "Validation error", "Couldnt convert highlighted values to float")
            return
        if self.dialog_mode == "add":
            key = self.LoadsCore.generate_unique_key(self.LoadsCore.node_loads, self.dict_id)
            self.dialog_mode = "edit"
            self.dict_id = key
            self.main_label.setText(f"Edit force id: {self.dict_id}, Node ID: {self.LoadsCore.get_meshOBJ_id(self.dict_id)}")
            self.setWindowTitle("Edit Node Load")
            self.apply_btn.setText("Apply changes")
        else:
            key = self.dict_id
        if delete:
            self.dialog_mode = "add"
            self.dict_id = self.LoadsCore.get_meshOBJ_id(self.dict_id)
            self.main_label.setText(f"Apply force to Node ID: {self.dict_id}")
            self.setWindowTitle("New Node Load")
            self.canvas.remove_visualOBJ(self.LoadsCore.drawn_loadOBJ["node"][key])
            del self.LoadsCore.node_loads[key]
            del self.LoadsCore.drawn_loadOBJ["node"][key]
            self.LoadsCore.draw_load_selection(cancel = True)
            self.canvas.draw()
        else:
            self.LoadsCore.node_loads[key] = vector
            self.LoadsCore.draw_node_load(obj_id = key, draw = True)
            self.LoadsCore.draw_load_selection(obj_type = "node_loads", obj_id = key, cancel = False)
        self.Refresh_GUI()
        self.LoadsCore.generate_load_lists(n_load = True)

    def save_close(self):
        self.save_changes()
        if not self.convert_to_vector():
            return
        else:
            self.accept()

    def close_dialog(self):
        self.accept()

        
# ======================================== 
# Dialog okna manipulcaji obciążeniem elementu
# ======================================== EDYTOR OBCIĄŻEŃ
class ElementLoadManager(QDialog):
    def __init__(self, parent = None, canvas = None, LoadsCore = None, mode = "add", obj_id = None):
        super().__init__(parent)
        
        self.MainWindow = parent
        self.canvas = canvas
        self.LoadsCore = LoadsCore
        self.dialog_mode = mode
        self.dict_id = obj_id
        self.element_id = self.LoadsCore.get_meshOBJ_id(obj_id)
        self.current_direction_type = self.current_formula_type = self.current_n_points = None
        self.numerical_distribution = None
        self.symbolic_distribution = None

        # zarządzanie tytułem:
        if mode == "add":
            title = "New Element Load distribution"
            label_txt = f"Apply load distribution to element ID: {self.dict_id}"
            apply_txt = "Apply Load distribution"
        else:
            title = "Edit Element Load distribution"
            label_txt = f"Edit load distribution id: {self.dict_id}, Element ID: {self.LoadsCore.get_meshOBJ_id(self.dict_id)}"
            apply_txt = "Apply changes" 

        self.setWindowTitle(f"{title}")
        self.setMinimumWidth(1200)
        # layout:
        main_layout = QHBoxLayout(self)
        self.left_lt = QVBoxLayout()
        self.center_lt = QVBoxLayout()
        self.right_lt = QVBoxLayout()
        main_layout.addLayout(self.left_lt, stretch = 2)
        main_layout.addLayout(self.center_lt, stretch = 2)
        main_layout.addLayout(self.right_lt, stretch = 1)
        

        # Lewy_lt
        self.element_label = QLabel(f"{label_txt}")
        self.element_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        element_label_font = self.element_label.font()
        element_label_font.setPointSize(14)
        self.element_label.setFont(element_label_font)
        self.left_lt.addWidget(self.element_label)

        self.Main_params_lt = QVBoxLayout()
        self.left_lt.addLayout(self.Main_params_lt)
        self.left_lt.addStretch()

        bottom_lt = QHBoxLayout()
        self.apply_btn = QPushButton(f"{apply_txt}")
        apply_close_btn = QPushButton("Apply & Close")
        close_btn = QPushButton("Close")
        bottom_lt.addWidget(self.apply_btn)
        bottom_lt.addWidget(apply_close_btn)
        bottom_lt.addWidget(close_btn)
        self.left_lt.addLayout(bottom_lt)
        self.apply_btn.clicked.connect(self.save_changes)
        apply_close_btn.clicked.connect(self.save_close)
        close_btn.clicked.connect(self.close_dialog)

        # layout centralny:
        LoadsDistr_label = QLabel("Load disribution visualization (dimensionless)")
        LoadsDistr_label_font = LoadsDistr_label.font()
        LoadsDistr_label_font.setPointSize(14)
        LoadsDistr_label.setFont(LoadsDistr_label_font)
        LoadsDistr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lt.addWidget(LoadsDistr_label)
        # Ustwienie tego aby widget wykresu nie kurczył się:
        self.LoadsCanvas = AuxilaryCanvas(self, width = 4, height = 4)
        self.LoadsCanvas.setMinimumWidth(400) # Ustawienie minimalnej szerokości, 400 pikseli wynika z testów
        self.LoadsCanvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) # (rozszerzaj się, rozszerzaj się)
        self.center_lt.addWidget(self.LoadsCanvas)
        # Dolny canvas
        Func_label = QLabel("Load disribution function (dimensionless)")
        Func_label_font = Func_label.font()
        Func_label_font.setPointSize(14)
        Func_label.setFont(Func_label_font)
        Func_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_lt.addWidget(Func_label)
        # Ustwienie tego aby widget wykresu nie kurczył się:
        self.FuncCanvas = AuxilaryCanvas(self, width = 4, height = 2)
        self.FuncCanvas.setMinimumWidth(400) # Ustawienie minimalnej szerokości, 400 pikseli wynika z testów
        self.FuncCanvas.setMinimumHeight(200)
        self.FuncCanvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) # (rozszerzaj się, rozszerzaj się)
        self.center_lt.addWidget(self.FuncCanvas)

        # Prawy layout
        settings_label = QLabel("Canvas Settings")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_label_font = settings_label.font()
        settings_label_font.setPointSize(14)
        settings_label.setFont(settings_label_font)
        self.right_lt.addWidget(settings_label)
        thick_line_thickness_lst = ["0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2", "3", "4", "5"]
        thin_line_thickness_lst = ["0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2"]
        linestyle_lst = ['None', '--', '-', '-.', ':']
        opacity_lst = ["0", "0.25", "0.5", "0.75", "1"]
        set_aspect_lst = ['equal', 'auto']
        color_lst = ["black", "blue", "green", "red", "gray", "pink"]
        text_size_list = ["0", "2", "3", "4", "5", "6", "7", "8", "9", "10", "12", "14", "16", "18", "20"]
        margin_lst = ["0", "0.1", "0.15", "0.2", "0.25", "0.5", "0.75", "1"]
        resolution_lst = ["10", "15", "20", "25", "30", "40", "50"]

        # Funkcja tworząca combo boxy
        def make_combobox_lt(parent_lt, label_text, items, current_txt = ""):
            local_lt = QHBoxLayout()
            parent_lt.addLayout(local_lt)
            local_lt.addWidget(QLabel(label_text))
            
            comboBox = QComboBox()
            comboBox.addItems(items)
            if current_txt:
                comboBox.setCurrentText(current_txt)
                
            local_lt.addWidget(comboBox)
            local_lt.addStretch()
            return comboBox

        self.Thicc_lineBox = make_combobox_lt(self.right_lt, "Thick linewidth: ", thick_line_thickness_lst, "1.5")
        self.Thicc_transparencyBox = make_combobox_lt(self.right_lt, "Thick line transparency: ", opacity_lst, "0.75")
        self.Thicc_linestyleBox = make_combobox_lt(self.right_lt, "Thick linestyle: ", linestyle_lst, "-")
        self.Thicc_colorBox = make_combobox_lt(self.right_lt, "Thick line color: ", color_lst, "black")
        
        self.Thinn_lineBox = make_combobox_lt(self.right_lt, "Thin linewidth: ", thin_line_thickness_lst, "0.75")
        self.Thinn_transparencyBox = make_combobox_lt(self.right_lt, "Thin line transparency: ", opacity_lst, "0.75")
        self.Thinn_linestyleBox = make_combobox_lt(self.right_lt, "Thin linestyle: ", linestyle_lst, "--")
        self.Thinn_colorBox = make_combobox_lt(self.right_lt, "Thin line color: ", color_lst, "black")
        
        self.Grid_linestyleBox = make_combobox_lt(self.right_lt, "Grid linestyle: ", linestyle_lst, ":")
        self.Grid_transparencyBox = make_combobox_lt(self.right_lt, "Grid transparency: ", opacity_lst, "0.75")
        self.Grid_colorBox = make_combobox_lt(self.right_lt, "Grid color: ", color_lst, "black")
        self.ResolutionBox = make_combobox_lt(self.right_lt, "Canvas resolution (pts): ", resolution_lst, "20")
        
        self.Canvas_MarginBox = make_combobox_lt(self.right_lt, "Canvas margin: ", margin_lst, "0.2")
        self.Canvas_aspectBox = make_combobox_lt(self.right_lt, "Canvas aspect: ", set_aspect_lst, "equal")
        self.Canvas_TextsizeBox = make_combobox_lt(self.right_lt, "Canvas font size: ", text_size_list, "7")
        self.Canvas_TextColorBox = make_combobox_lt(self.right_lt, "Canvas font color: ", color_lst, "black")
        self.Canvas_TextTransparencyBox = make_combobox_lt(self.right_lt, "Canvas font transparency: ", opacity_lst, "1")
        self.Func_TextsizeBox = make_combobox_lt(self.right_lt, "Latex formula font size: ", text_size_list, "8")
        
        # Przycisk zarządzania dodatkowymi informacjami:
        def axis_btn_status():
            if axis_btn.text() == "Showing additional info":
                axis_btn.setText("Hiding additional info")
                self.disable_info = True
            else:
                axis_btn.setText("Showing additional info")
                self.disable_info = False
        
        self.disable_info = False
        axis_btn = QPushButton("Showing additional info")
        self.right_lt.addWidget(axis_btn)
        apply_plot_settings_btn = QPushButton("Apply plot settings")
        generate_latex_func_btn = QPushButton("Generate Formula (LaTeX)")
        latex_label = QLabel("Generates mathematical expression using LaTeX\n(may take a few seconds)")
        latex_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_lt.addStretch()
        self.right_lt.addWidget(apply_plot_settings_btn)
        self.right_lt.addWidget(generate_latex_func_btn)
        self.right_lt.addWidget(latex_label)

        # Połączenie
        apply_plot_settings_btn.clicked.connect(self.compose_canvas)
        axis_btn.clicked.connect(axis_btn_status)
        generate_latex_func_btn.clicked.connect(self.generate_LaTeX_formula)

        # generowanie reszty:
        self.build_intencityGUI()
        self.build_distributionGUI()
        # dla edycji:
        if self.dialog_mode == "edit":
            if self.validate_inputs():
                sym_dict = None if self.MainWindow.data_type != "symbolic" else self.LoadsCore.load_symbol_substitutes
                self.Distribution_Class = FormulateDistribution(load_data = self.LoadsCore.element_loads[self.dict_id]["load_data"], sym_dict = sym_dict, sympy_local = sympy_LOCAL)
                self.numerical_distribution = self.Distribution_Class.SymPy_dimensionless(numerical = True)
                self.symbolic_distribution = self.Distribution_Class.SymPy_dimensionless()
        # wywołanie ustawień canvasa:
        self.compose_canvas()
                
    # ===================================
    # Funkcja ustawień canvasa:
    def canvas_settings(self):
        # przypisanie ustawień stałych:
        self.thinn_line = float(self.Thinn_lineBox.currentText())
        self.thinn_transparency = float(self.Thinn_transparencyBox.currentText())
        self.thinn_line_color = self.Thinn_colorBox.currentText()
        self.thinn_linestyle = self.Thinn_linestyleBox.currentText()
        self.thicc_line = float(self.Thicc_lineBox.currentText())
        self.thicc_transparency = float(self.Thicc_transparencyBox.currentText())
        self.thicc_line_color = self.Thicc_colorBox.currentText()
        self.thicc_linestyle = self.Thicc_linestyleBox.currentText()

        self.text_sizeCanvas = float(self.Canvas_TextsizeBox.currentText())
        self.text_colorCanvas = self.Canvas_TextColorBox.currentText()
        self.text_tansparencyCanvas = float(self.Canvas_TextTransparencyBox.currentText())
        self.textFuncSize = float(self.Func_TextsizeBox.currentText())
        self.Resolution = int(self.ResolutionBox.currentText())
        if self.Resolution <= 15:
            self.hatch_d = 1
        elif self.Resolution <= 30:
            self.hatch_d = 2
        else:
            self.hatch_d = 3

        # ustawienia samego płutna:
        self.LoadsCanvas.axes.clear()
        self.LoadsCanvas.axes.set_aspect(self.Canvas_aspectBox.currentText())
        self.LoadsCanvas.axes.margins(float(self.Canvas_MarginBox.currentText()))
        self.LoadsCanvas.axes.autoscale_view()
        self.LoadsCanvas.axes.grid(linestyle = self.Grid_linestyleBox.currentText(), alpha = float(self.Grid_transparencyBox.currentText()), color = self.Grid_colorBox.currentText())
        self.LoadsCanvas.axes.set_xlabel(r"$\xi$", fontsize = self.text_sizeCanvas + 4)
        self.LoadsCanvas.axes.set_ylabel(rf"$q_{{{self.dict_id}}}(\xi)$", fontsize = self.text_sizeCanvas + 4)
        self.LoadsCanvas.figure.set_layout_engine("constrained")
        self.LoadsCanvas.draw()

        # Ustawienia płótna wyłącznie pod wyświetlanie równania:
        self.FuncCanvas.axes.clear()
        self.FuncCanvas.axes.axis("off")

        return

    # funkcja generująca zapis Latex
    def generate_LaTeX_formula(self):
        def wrap_latex_plus_minus(latex_cleaned, max_len=50):
            out = []
            brace_depth = 0   # głębokość { }
            lr_depth = 0      # głębokość \left ... \right
            env_depth = 0     # głębokość \begin{...} ... \end{...} (np. cases)
            chars_since_break = 0
            i = 0
            n = len(latex_cleaned)

            while i < n:
                # Śledzenie zagnieżdżeń komend LaTeX
                if latex_cleaned.startswith(r"\left", i):
                    lr_depth += 1
                elif latex_cleaned.startswith(r"\right", i):
                    lr_depth = max(0, lr_depth - 1)
                elif latex_cleaned.startswith(r"\begin", i):
                    env_depth += 1
                elif latex_cleaned.startswith(r"\end", i):
                    env_depth = max(0, env_depth - 1)

                ch = latex_cleaned[i]
                if ch == "{":
                    brace_depth += 1
                elif ch == "}":
                    brace_depth = max(0, brace_depth - 1)

                # Łamanie linii przy + lub - po przekroczeniu limitu znaków
                if (
                    chars_since_break >= max_len
                    and ch in ("+", "-")
                    and brace_depth == 0
                    and lr_depth == 0
                    and env_depth == 0
                ):
                    out.append(r" \\ ")
                    chars_since_break = 0

                out.append(ch)
                chars_since_break += 1
                i += 1

            return "".join(out)
        # Pobranie 
        self.textFuncSize = float(self.Func_TextsizeBox.currentText())
        if self.symbolic_distribution is None:
            clean_latex = r"$NOT \text{ } DEFINED$"
        else:
            def simplify_num(num):
                num_clean = round(float(num), 2)
                return int(num_clean) if num_clean.is_integer() else num_clean
            # rozczepienie wyrażenia sympy:
            display_func = sp.latex(self.symbolic_distribution.xreplace({n: simplify_num(n) for n in self.symbolic_distribution.atoms(sp.Float)}))
            sympy_base = sp.latex(sp.sympify(self.LoadsCore.element_loads[self.dict_id]["load_data"]["base_intensity"], locals = sympy_LOCAL))
            sympy_ax = sp.latex(sp.sympify(self.LoadsCore.element_loads[self.dict_id]["load_data"]["axial_factor"], locals = sympy_LOCAL))
            sympy_norm = sp.latex(sp.sympify(self.LoadsCore.element_loads[self.dict_id]["load_data"]["normal_factor"], locals = sympy_LOCAL))
            if self.LoadsCore.element_loads[self.dict_id]["load_data"]["type"] == "polynomial_bezier":
                display_func = wrap_latex_plus_minus(latex_cleaned = display_func, max_len = 100)
            clean_latex = (
                            rf"$\begin{{gathered}}"
                            rf"Q_B = {sympy_base}, \quad Q_{{\xi}} = {sympy_ax} \cdot Q_B, \quad Q_{{\eta}} = {sympy_norm} \cdot Q_B \\"
                            rf"q_{{{self.dict_id}}}(\xi) = {display_func}"
                            rf"\end{{gathered}}$"
                        )
        def render_latex(use_tex = True):
            with plt.rc_context({
                "text.usetex": use_tex,
                "font.family": "serif",
                "text.latex.preamble": r"\usepackage{amsmath} \usepackage{amssymb}"
            }):
                self.FuncCanvas.axes.clear()
                self.FuncCanvas.axes.axis("off")
                self.FuncCanvas.axes.text(
                    0.5, 0.5,
                    clean_latex,
                    fontsize=self.textFuncSize,
                    ha="center",
                    va="center",
                    transform=self.FuncCanvas.axes.transAxes
                )
                self.FuncCanvas.draw()
        try:
            render_latex(use_tex = True)
        except Exception:
            render_latex(use_tex = False)
        return

    # funkcja pobierająca odpowiadający słownik:
    def get_visual_dict(self, type = "thicc"):
        if type == "thicc":
            return {
                "linewidth": self.thicc_line,
                "alpha": self.thicc_transparency,
                "color": self.thicc_line_color,
                "linestyle": self.thicc_linestyle
            }
        elif type == "thinn":
            return {
                "linewidth": self.thinn_line,
                "alpha": self.thinn_transparency,
                "color": self.thinn_line_color,
                "linestyle": self.thinn_linestyle
            }
        elif type == "text":
            return {
                "fontsize": self.text_sizeCanvas,
                "color": self.text_colorCanvas,
                "alpha": self.text_tansparencyCanvas
            }
        elif type == "hatch":
            return {
                "linewidth": self.thinn_line,
                "alpha": self.thinn_transparency,
                "color": self.thinn_line_color,
                "linestyle": "-"
            }
        
    # funkcja rysująca strzałkę:
    def draw_arrow(self, length, theta, base_point, type):
        # tworzenie strzałki:
        x_div = 10 if type == "hatch" else 6
        z_div  = 35 if type == "hatch" else 8
        tip_x = np.array([length - length/x_div, length, length - length/x_div])
        tip_z = np.array([length/z_div, 0, -length/z_div])
        line_x = np.array([0, length])
        line_z = np.array([0, 0])
        # rotacja:
        tip_x_f = tip_x * np.cos(theta) - tip_z * np.sin(theta) + base_point[0]
        tip_z_f = tip_x * np.sin(theta) + tip_z * np.cos(theta) + base_point[1]
        line_x_f = line_x * np.cos(theta) - line_z * np.sin(theta) + base_point[0]
        line_z_f = line_x * np.sin(theta) + line_z * np.cos(theta) + base_point[1]
        
        # rysowanie:
        vis_dict = self.get_visual_dict(type = type)
        arrow_tip = self.LoadsCanvas.axes.plot(tip_x_f, tip_z_f, 
                                                linestyle = vis_dict["linestyle"], 
                                                linewidth = vis_dict["linewidth"], 
                                                color = vis_dict["color"], 
                                                alpha = vis_dict["alpha"])
        
        arrow_line = self.LoadsCanvas.axes.plot(line_x_f, line_z_f, 
                                                linestyle = vis_dict["linestyle"], 
                                                linewidth = vis_dict["linewidth"], 
                                                color = vis_dict["color"], 
                                                alpha = vis_dict["alpha"])
        return

    # narzędzie do rysowania teskstu
    def write_text(self, x, z, text = "", bbox = False):
        bbox_alpha = bbox if bbox else 0.0
        vis_dict = self.get_visual_dict(type = "text")
        label = self.LoadsCanvas.axes.text(x, z, f"{text}",
                                            color = vis_dict["color"],
                                            ha = 'center',
                                            va = 'center',
                                            fontsize = vis_dict["fontsize"],
                                            alpha = vis_dict["alpha"],
                                            bbox = dict(
                                                    boxstyle = 'round,pad=0.15',
                                                    fc = 'white',
                                                    ec = 'none',
                                                    alpha = bbox_alpha))
        return

    # funkcja sterująca rysowaniem:
    def compose_canvas(self):
        self.canvas_settings()
        if self.dialog_mode == "edit":
            if not self.disable_info:
                self.draw_base_intensity()
                self.draw_direction()
            self.draw_element()
            self.plot_distribution()
        # refreshowanie
        self.LoadsCanvas.draw()

    # rysowanie strzałki base intensity:
    def draw_base_intensity(self):
        QB_float = self.LoadsCore.validate_val(val = self.LoadsCore.element_loads[self.dict_id]["load_data"]["base_intensity"], sym_key = "distributed_load")
        QB_text = rf"Base Intensity = {QB_float}"
        theta = np.pi / 2 if QB_float >= 0 else  - np.pi / 2
        text_z = 1.1
        base_point = [-0.15, 0] if QB_float >= 0 else [-0.15, 1]
        length = 1
        arrow = self.draw_arrow(length, theta, base_point, "thicc")
        label = self.write_text(-0.1, text_z, QB_text)
        stretch = self.LoadsCanvas.axes.plot([0, 0], [0, 1.15], linestyle = "-", alpha = 0.0)

    # rysowanie strzałki direction:
    def draw_direction(self):
        q_ax = self.LoadsCore.validate_val(val = self.LoadsCore.element_loads[self.dict_id]["load_data"]["axial_factor"], sym_key = "dimensionless")
        q_nm = self.LoadsCore.validate_val(val = self.LoadsCore.element_loads[self.dict_id]["load_data"]["normal_factor"], sym_key = "dimensionless")
        theta = np.arctan2(q_nm, q_ax)
        label_text = f"Direction\nq_ax = {round(q_ax, 3)}\nq_norm = {round(q_nm, 3)}"
        text_z = 0.35 if theta >=0 else 0.65
        text_x = -0.55
        base_point = [-0.55, 0.5]
        length = 0.35
        arrow = self.draw_arrow(length, theta, base_point, "thicc")
        label = self.write_text(text_x, text_z, label_text)
        stretch = self.LoadsCanvas.axes.plot([text_x, text_x - 0.25], [0,0], linestyle = "-", alpha = 0.0)

    # rysowanie elementu:
    def draw_element(self):
        vis_dict = self.get_visual_dict(type = "thinn")
        x = [0, 0, 1, 1, 0]
        z = [0.03, -0.03, -0.03, 0.03, 0.03]
        element_box = self.LoadsCanvas.axes.plot(x, z, 
                                                linestyle = vis_dict["linestyle"], 
                                                linewidth = vis_dict["linewidth"], 
                                                color = vis_dict["color"], 
                                                alpha = vis_dict["alpha"])
        axis = self.LoadsCanvas.axes.plot([-0.05, 1.05], [0, 0], 
                                            linestyle = vis_dict["linestyle"], 
                                            linewidth = vis_dict["linewidth"], 
                                            color = vis_dict["color"], 
                                            alpha = vis_dict["alpha"])

    # rysowanie obciążenia:
    def plot_distribution(self):
        vis_dict = self.get_visual_dict(type = "thicc")
        t_list = np.linspace(0, 1, self.Resolution)
        sym_key = "distributed_load" if self.MainWindow.data_type == "symbolic" else None
        scalator = -1 if self.LoadsCore.validate_val(val = self.LoadsCore.element_loads[self.dict_id]["load_data"]["base_intensity"], sym_key = sym_key) <= 0 else 1
        if self.LoadsCore.element_loads[self.dict_id]["load_data"]["type"] == "piecewise_linear":
            x_list_float = []
            z_list_float = []
            for p_dict in self.LoadsCore.element_loads[self.dict_id]["load_data"]["points"]:
                t = self.LoadsCore.validate_val(val = p_dict["t"], sym_key = "dimensionless")
                val = self.LoadsCore.validate_val(val = p_dict["val"], sym_key = "dimensionless") * scalator
                x_list_float.append(t)
                z_list_float.append(val)
                self.write_text(x = t, z = val, text = "+")
            plot = self.LoadsCanvas.axes.plot(x_list_float, z_list_float, 
                                            linestyle = vis_dict["linestyle"], 
                                            linewidth = vis_dict["linewidth"], 
                                            color = vis_dict["color"], 
                                            alpha = vis_dict["alpha"])
        # generowanie kratkowania:
        x_list_float = []
        z_list_float = []
        # pobranie symbolu zmiennej, zakładamy że jest jeden symbol xi_e
        xi_e = None
        for s in self.numerical_distribution.free_symbols:
            if s.name == "xi_e":
                xi_e = s

        for i, xi in enumerate(t_list):      
            z_val = float(self.numerical_distribution.subs(xi_e, xi) if xi_e is not None else self.numerical_distribution) * scalator
            x_list_float.append(xi)
            z_list_float.append(z_val)
            if xi in (0.0, 1.0) or i % self.hatch_d == 0:
                theta = -np.pi / 2 if z_val < 0 else np.pi / 2
                self.draw_arrow(length = np.abs(z_val), base_point = [xi, 0.0], theta = theta, type = "hatch")

        # rysowanie jeśli jest to wielomian
        if self.LoadsCore.element_loads[self.dict_id]["load_data"]["type"] == "polynomial_bezier":
            plot = self.LoadsCanvas.axes.plot(x_list_float, z_list_float, 
                                            linestyle = vis_dict["linestyle"], 
                                            linewidth = vis_dict["linewidth"], 
                                            color = vis_dict["color"], 
                                            alpha = vis_dict["alpha"])
        
        # zapisywanie punktów
        self.LoadsCore.element_loads[self.dict_id]["drawing_points"] = {"x": x_list_float, "z": z_list_float}
    
        return
    # ===================================
    
    # Funkcja refreshująca
    def Refresh_GUI(self, intense_only = False, distribution_only = False):
        # funkcja usuwająca widgety i layouty:
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item
        if intense_only:
            clear_layout(self.Intense_lt)
            self.build_intencityGUI()
        elif distribution_only:
            clear_layout(self.distribution_lt)
            self.build_distributionGUI()
        else:
            clear_layout(self.Main_params_lt)
            self.build_intencityGUI()
            self.build_distributionGUI()
        return

    # Narzędzie do tworzenia poziomego Gui:
    def make_param_widget(self, parent_lt = None, widget = None, label_txt = "", font_size = 9, stretch = True, list = None, current_text = lambda: None):
        local_lt = QHBoxLayout()
        parent_lt.addLayout(local_lt)
        local_widget = widget
        label = QLabel(f"{label_txt}")
        label_font = label.font()
        label_font.setPointSize(font_size)
        label.setFont(label_font)
        local_lt.addWidget(label)
        local_lt.addWidget(local_widget)
        if stretch:
            local_lt.addStretch()
        if list:
            local_widget.addItems(list)
            try:
                current_txt = current_text() if callable else current_text
                local_widget.setCurrentText(current_txt)
            except Exception:
                pass
        return local_widget

    # Funkcja tworząca gui Intensity/DIrection
    def build_intencityGUI(self):
        self.Intense_lt = QVBoxLayout()
        Intense_label = QLabel("Distribution base intensity (Q):")
        Intense_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Intense_label_font = Intense_label.font()
        Intense_label_font.setPointSize(12)
        Intense_label.setFont(Intense_label_font)
        self.Intense_lt.addWidget(Intense_label)
        self.Main_params_lt.insertLayout(0, self.Intense_lt)
        # pobranie ornientacji elementu:
        self.global_element_angle = self.canvas.get_element_vector(self.element_id, MessageBox = False, log = False, angle_only = True)
        self.global_element_angle = np.rad2deg(self.global_element_angle)

        # Ustawienie odpowiedniego reimu:
        if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
            if self.canvas.elements[self.element_id]["type"] in {"2N4DOF_EB", "2N4DOF_T_EX", "2N4DOF_T_FI", "2N4DOF_T_RI", "2N6DOF_EB_Q"}:
                direction_label_txt = f"Load Direction method:\n({self.canvas.elements[self.element_id]["type"]}, PBA topology beam element)"
                direction_type_list = ["Normal"]
            elif self.canvas.elements[self.element_id]["type"] in {"2N2DOF_Bar", "Spring"}:
                direction_label_txt = f"Load Direction method:\n({self.canvas.elements[self.element_id]["type"]}, axial element)"
                direction_type_list = ["Axial"]
        else:
            if self.canvas.elements[self.element_id]["type"] in {"2N4DOF_Truss", "Spring_2D"}:
                direction_label_txt = f"Load Direction method:\n({self.canvas.elements[self.element_id]["type"]}, axial element)"
                direction_type_list = ["Axial"]
            else:
                direction_label_txt = "Load Direction method: "
                direction_type_list = ["Normal", "Axial", "at_angle", "factor_XZ"]

        if self.dialog_mode == "edit" and self.current_direction_type is None:
            self.current_direction_type = self.LoadsCore.element_loads[self.dict_id]["intensity_settings"]["d_type"]

        self.Base_intensity_line = self.make_param_widget(parent_lt = self.Intense_lt, widget = QLineEdit(),
                                                          label_txt = "Base intensity (q₀ [Force/distance]):", font_size = 10)
        self.Direction_type_box = self.make_param_widget(parent_lt = self.Intense_lt, widget = QComboBox(),
                                                         label_txt = direction_label_txt, font_size = 10,
                                                         list = direction_type_list, 
                                                         current_text = lambda: self.current_direction_type)
        
        

        if self.Direction_type_box.currentText() == "at_angle":
            self.Distribution_angle_line = self.make_param_widget(parent_lt = self.Intense_lt, widget = QLineEdit(),
                                                                  label_txt = f"Load angle (relative to element axis)\nElement global orientation: {self.global_element_angle:.3f}°")
        elif self.Direction_type_box.currentText() == "factor_XZ":
            local_XZ_lt = QHBoxLayout()
            self.Intense_lt.addLayout(local_XZ_lt)
            self.X_intensity_line = self.make_param_widget(parent_lt = local_XZ_lt, widget = QLineEdit(),
                                                           label_txt = "Scale factor (Axial):")
            self.Z_intensity_line = self.make_param_widget(parent_lt = local_XZ_lt, widget = QLineEdit(),
                                                            label_txt = "Scale factor (Normal):")
        elif self.Direction_type_box.currentText() == "Normal":
            local_XZ_lt = QHBoxLayout()
            self.Intense_lt.addLayout(local_XZ_lt)
            self.X_intensity_line = self.make_param_widget(parent_lt = local_XZ_lt, widget = QLabel("0"),
                                                            label_txt = "Scale factor (Axial):")
            self.Z_intensity_line = self.make_param_widget(parent_lt = local_XZ_lt, widget = QLineEdit(),
                                                            label_txt = "Scale factor (Normal):")
        elif self.Direction_type_box.currentText() == "Axial":
            local_XZ_lt = QHBoxLayout()
            self.Intense_lt.addLayout(local_XZ_lt)
            self.X_intensity_line = self.make_param_widget(parent_lt = local_XZ_lt, widget = QLineEdit(),
                                                            label_txt = "Scale factor (Axial):")
            self.Z_intensity_line = self.make_param_widget(parent_lt = local_XZ_lt, widget = QLabel("0"),
                                                            label_txt = "Scale factor (Normal):")

        local_final_intensity_lt = QHBoxLayout()
        self.Intense_lt.addLayout(local_final_intensity_lt)
        self.X_base_intensity_label = QLabel("Axial intensity: (not calculated)")
        self.Z_base_intensity_label = QLabel("Normal intensity: (not calculated)")
        local_final_intensity_lt.addWidget(self.X_base_intensity_label)
        local_final_intensity_lt.addWidget(self.Z_base_intensity_label)
            
        # Refresh GUI po zmianie typu:
        def change_direction_type():
            self.current_direction_type = self.Direction_type_box.currentText()
            self.Refresh_GUI(intense_only = True)

        self.Direction_type_box.currentTextChanged.connect(change_direction_type)

        # wypełnianie
        if self.dialog_mode == "edit" and self.Direction_type_box.currentText() == self.LoadsCore.element_loads[self.dict_id]["intensity_settings"]["d_type"]:
            try:
                self.fill_intencity_GUI()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occured while reading load distribution data:\n{e}")

    # funkcja walidująco podkreślająca:
    def validate_widget_val(self, widget = None, sym_key = None, flag = False, return_val = False, raw_val = False, force_sympy = False):
        str_val = widget.text()
        abs_val, val_flag = self.LoadsCore.validate_val(str_val, sym_key, flag = True, return_raw = raw_val, force_sympy = force_sympy)
        if val_flag:
            widget.setStyleSheet("")
        else:
            widget.setStyleSheet("background-color: red; color: white")
        if flag and return_val:
            return abs_val, val_flag
        elif return_val:
            return abs_val
        elif flag:
            return val_flag
        else:
            return
    
    # Funkcja wypełniająca intencity:
    def fill_intencity_GUI(self):
        def validate_widgets():
            base_flag = True
            base_intensity, flag = self.validate_widget_val(widget = self.Base_intensity_line, sym_key = "distributed_load", flag = True, return_val = True, raw_val = True)
            if not flag:
                base_flag = False
            Ax_val, flag = self.validate_widget_val(widget = self.X_intensity_line, sym_key = "dimensionless", flag = True, return_val = True, raw_val = True)
            if not flag:
                base_flag = False
            Norm_val, flag = self.validate_widget_val(widget = self.Z_intensity_line, sym_key = "dimensionless", flag = True, return_val = True, raw_val = True)
            if not flag:
                base_flag = False
            return base_intensity, Ax_val, Norm_val, base_flag

        direction_type = self.LoadsCore.element_loads[self.dict_id]["intensity_settings"]["d_type"]
        if direction_type != "at_angle":
            self.Base_intensity_line.setText(f"{self.LoadsCore.element_loads[self.dict_id]["load_data"]["base_intensity"]}")
            self.X_intensity_line.setText(f"{self.LoadsCore.element_loads[self.dict_id]["intensity_settings"]["Ax_factor"]}")
            self.Z_intensity_line.setText(f"{self.LoadsCore.element_loads[self.dict_id]["intensity_settings"]["Norm_factor"]}")
            base_intensity, Ax_val, Norm_val, base_flag = validate_widgets()
            if base_flag:
                if self.MainWindow.data_type == "symbolic":
                    self.X_base_intensity_label.setText(f"Axial intensity: {Ax_val}*{base_intensity}")
                    self.Z_base_intensity_label.setText(f"Normal intensity: {Norm_val}*{base_intensity}")
                else:
                    self.X_base_intensity_label.setText(f"Axial intensity: {Ax_val * base_intensity}")
                    self.Z_base_intensity_label.setText(f"Normal intensity: {Norm_val * base_intensity}")
        else:
            self.Base_intensity_line.setText(f"{self.LoadsCore.element_loads[self.dict_id]["load_data"]["base_intensity"]}")
            self.Distribution_angle_line.setText(f"{self.LoadsCore.element_loads[self.dict_id]["intensity_settings"]["L_angle"]}")
            base_flag = True
            base_intensity, flag = self.validate_widget_val(widget = self.Base_intensity_line, sym_key = "distributed_load", flag = True, return_val = True, raw_val = True)
            if not flag:
                base_flag = False
            L_angle, flag = self.validate_widget_val(widget = self.Distribution_angle_line, sym_key = "angle", flag = True, return_val = True)
            if not flag:
                base_flag = False
            if base_flag:
                if self.MainWindow.data_type == "symbolic":               
                    # Dokładny kąt w radianach:
                    angle_round = round(L_angle, 6)
                    angle_sym = sp.Rational(str(angle_round))
                    angle_rad = angle_sym / 180 * sp.pi
                    try:
                        base_intensity_str = sp.sympify(base_intensity, locals = sympy_LOCAL)
                        Ax_str = str(sp.cos(angle_rad) * base_intensity_str)
                        Norm_str = str(sp.sin(angle_rad) * base_intensity_str)
                    except Exception:
                        Ax_str = f"{str(sp.cos(angle_rad))}*{base_intensity}"
                        Norm_str = f"{str(sp.sin(angle_rad))}*{base_intensity}"
                else:
                    Ax_str = np.cos(np.deg2rad(L_angle)) * base_intensity
                    Norm_str = np.sin(np.deg2rad(L_angle)) * base_intensity
                self.X_base_intensity_label.setText(f"Axial intensity: {Ax_str}")
                self.Z_base_intensity_label.setText(f"Normal intensity: {Norm_str}")

        return

    # Tłumaczenie nazwy typu:
    def convert_type_name(self, name):
        if name == "Piecewise linear (trapezoidal / polyline)":
            return "piecewise_linear"
        elif name == "piecewise_linear":
            return "Piecewise linear (trapezoidal / polyline)"
        elif name == "Polynomial Bézier (smooth curve, deg N-1)":
            return "polynomial_bezier"
        elif name == "polynomial_bezier":
            return "Polynomial Bézier (smooth curve, deg N-1)"
    
    # Funkcja tworząca GUI load distribution:
    def build_distributionGUI(self):
        self.distribution_lt = QVBoxLayout()
        distribution_label = QLabel("Distributed load definition q(t):")
        distribution_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        distribution_label_font = distribution_label.font()
        distribution_label_font.setPointSize(12)
        distribution_label.setFont(distribution_label_font)
        self.distribution_lt.addWidget(distribution_label)
        self.Main_params_lt.insertLayout(-1, self.distribution_lt)

        if (self.dialog_mode == "edit" 
            and self.current_formula_type is None
            and self.current_n_points is None):
            self.current_formula_type = self.convert_type_name(self.LoadsCore.element_loads[self.dict_id]["load_data"]["type"])
            self.current_n_points = str(self.LoadsCore.element_loads[self.dict_id]["load_data"]["n_points"])

        # layout wyboru:
        self.Formula_type_box = self.make_param_widget(parent_lt = self.distribution_lt, widget = QComboBox(),
                                                       label_txt = "Interpolation method: ", 
                                                       list = ["Piecewise linear (trapezoidal / polyline)", "Polynomial Bézier (smooth curve, deg N-1)"],
                                                       current_text = lambda: self.current_formula_type)
        if hasattr(self, "current_formula_type") and self.current_formula_type is not None:
            self.Formula_type_box.setCurrentText(self.current_formula_type)
        
        if self.convert_type_name(self.Formula_type_box.currentText()) == "piecewise_linear":
            self.N_points_box = self.make_param_widget(parent_lt = self.distribution_lt, widget = QComboBox(),
                                                       label_txt = "Vertices (min. 2): ", list = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                                                       current_text = lambda: self.current_n_points)
            if hasattr(self, "current_n_points") and self.current_n_points is not None:
                self.N_points_box.setCurrentText(self.current_n_points)
            # Generowanie listy:
            n_points = int(self.N_points_box.currentText())
            self.Point_lines_dict = {}
            i = 1
            type_label = QLabel("Vertices:  t ∈ [0, 1] (rel. pos.)  |  f ∈ \u211D [-] (shape multiplier)")
            type_label_font = type_label.font()
            type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_label_font.setPointSize(10)
            type_label.setFont(type_label_font)
            self.distribution_lt.addWidget(type_label)
            while i <= n_points:
                self.Point_lines_dict[i] = {}
                self.Point_lines_dict[i]["lt"] = QHBoxLayout()
                self.Point_lines_dict[i]["lt"].addWidget(QLabel(f"Point {i}:"))
                self.distribution_lt.addLayout(self.Point_lines_dict[i]["lt"])
                if i == 1:
                    self.Point_lines_dict[i]["t"] = self.make_param_widget(parent_lt = self.Point_lines_dict[i]["lt"], widget = QLabel("0"), label_txt = "Rel. pos (t): ")
                elif i == n_points:
                    self.Point_lines_dict[i]["t"] = self.make_param_widget(parent_lt = self.Point_lines_dict[i]["lt"], widget = QLabel("1"), label_txt = "Rel. pos (t): ")
                else:
                    self.Point_lines_dict[i]["t"] = self.make_param_widget(parent_lt = self.Point_lines_dict[i]["lt"], widget = QLineEdit(), label_txt = "Rel. pos (t): ")
                self.Point_lines_dict[i]["f"] = self.make_param_widget(parent_lt = self.Point_lines_dict[i]["lt"], widget = QLineEdit(), label_txt = "Multiplier (f [-]): ", stretch = False)
                i += 1

        elif self.convert_type_name(self.Formula_type_box.currentText()) == "polynomial_bezier":
            self.N_points_box = self.make_param_widget(parent_lt = self.distribution_lt, widget = QComboBox(),
                                                       label_txt = "Control points (deg = N-1): ", list = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                                                       current_text = lambda: self.current_n_points)
            if hasattr(self, "current_n_points") and self.current_n_points is not None:
                self.N_points_box.setCurrentText(self.current_n_points)
            # Generowanie listy:
            n_points = int(self.N_points_box.currentText())
            self.Point_lines_dict = {}
            i = 1
            type_label = QLabel("Control points (deg N-1):  fᵢ ∈ \u211D [-] (shape weights)")
            type_label_font = type_label.font()
            type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            type_label_font.setPointSize(10)
            type_label.setFont(type_label_font)
            self.distribution_lt.addWidget(type_label)
            while i <= n_points:
                idx = i - 1
                if i == 1:
                    t_i = "0"
                elif i != n_points:
                    t_i = f"{idx}/{n_points - 1}"
                else:
                    t_i = "1"
                self.Point_lines_dict[i] = {}
                self.Point_lines_dict[i]["lt"] = QHBoxLayout()
                self.distribution_lt.addLayout(self.Point_lines_dict[i]["lt"])
                self.Point_lines_dict[i]["lt"].addWidget(QLabel(f"Ctrl Point {idx}:"))
                self.Point_lines_dict[i]["t"] = self.make_param_widget(parent_lt = self.Point_lines_dict[i]["lt"], widget = QLabel(f"{t_i}"), label_txt = f"Pos (t): ")
                self.Point_lines_dict[i]["f"] = self.make_param_widget(parent_lt = self.Point_lines_dict[i]["lt"], widget = QLineEdit(), label_txt = "Weight (f [-]): ", stretch = False)
                i += 1

        def alter_GUI_typeBox():
            self.current_formula_type = self.Formula_type_box.currentText()
            self.Refresh_GUI(distribution_only = True)
        def alter_GUI_nBox():
            self.current_n_points = self.N_points_box.currentText()
            self.Refresh_GUI(distribution_only = True)

        self.Formula_type_box.currentTextChanged.connect(alter_GUI_typeBox)
        self.N_points_box.currentTextChanged.connect(alter_GUI_nBox)
        
        # wypełnianie
        if self.dialog_mode == "edit":
            try:
                if self.convert_type_name(self.Formula_type_box.currentText()) == self.LoadsCore.element_loads[self.dict_id]["load_data"]["type"]:
                    if int(self.N_points_box.currentText()) == self.LoadsCore.element_loads[self.dict_id]["load_data"]["n_points"]:
                        self.fill_distributionGUI()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"An error occured while reading load distribution data:\n{e}")
            delete_btn = QPushButton("Delete Load Distribution")
            delete_btn.setStyleSheet("background-color: red; color: white")
            self.distribution_lt.addWidget(delete_btn)
            delete_btn.clicked.connect(lambda: self.save_changes(delete = True))



        return

    # Funkcja wypełniająca dystrybucję:
    def fill_distributionGUI(self):
        type = self.LoadsCore.element_loads[self.dict_id]["load_data"]["type"]
        # wypełnianie pozycji:
        if type == "piecewise_linear":
            for i, p_dict in enumerate(self.LoadsCore.element_loads[self.dict_id]["load_data"]["points"], 1):
                self.Point_lines_dict[i]["t"].setText(str(p_dict["t"]))
                self.Point_lines_dict[i]["f"].setText(str(p_dict["val"]))
        elif type == "polynomial_bezier":
            for i, p_dict in enumerate(self.LoadsCore.element_loads[self.dict_id]["load_data"]["points"], 1):
                self.Point_lines_dict[i]["f"].setText(str(p_dict["val"]))
        return

    # Funkcja walidująca inputy:
    def validate_inputs(self):
        master_log = []
        # walidacja punktów i tworzenie listy wartości absolutnych:
        abs_t_vals = []
        raw_t_vals = []
        abs_f_vals = []
        raw_f_vals = []
        for p_i, p_dict in self.Point_lines_dict.items():
            abs_t, t_ok = self.validate_widget_val(widget = p_dict["t"], sym_key = "dimensionless", flag = True, return_val = True, force_sympy = True)
            raw_t = self.validate_widget_val(widget = p_dict["t"], sym_key = "dimensionless", flag = False, return_val = True, raw_val = True, force_sympy = True)
            abs_t_vals.append(abs_t)
            raw_t_vals.append(raw_t)
            if not t_ok:
                master_log.append(f"Point {p_i}: failed float conversion (t = {raw_t})")

            abs_f, f_ok = self.validate_widget_val(widget = p_dict["f"], sym_key = "dimensionless", flag = True, return_val = True)
            raw_f = self.validate_widget_val(widget = p_dict["f"], sym_key = "dimensionless", flag = False, return_val = True, raw_val = True)
            abs_f_vals.append(abs_f)
            raw_f_vals.append(raw_f)
            if not f_ok:
                master_log.append(f"Point {p_i}: failed float conversion (f = {raw_f})")

        # Przerwanie pracy:
        if master_log:
            dialog = ListReportLog(self, title = "Load Distribution - Validation Error", 
                                   label_text = "The load distribution could not be applied due to invalid entries:", 
                                   display_list = master_log)
            dialog.exec()
            return False

        # Walidacja odległości punktów:
        num_of_pts = len(abs_t_vals)
        non_linear = 0
        for i, t_val in enumerate(abs_t_vals, 1):
            t_round = round(t_val, 13)
            if i != 1 and t_round == 0.0:
                master_log.append(f"Point {i}: t cannot be equal to 0")
            if i != num_of_pts and t_round == 1.0:
                master_log.append(f"Point {i}: t cannot be equal to 1")
            if 0.0 <= t_round <= 1.0:
                if 2 < i < num_of_pts:
                    prev_t_round = round(abs_t_vals[i - 2], 13)
                    if t_round < prev_t_round:
                        master_log.append(f"Points ({i - 1}, {i}): t value must increase")
                    if t_round == prev_t_round:
                        non_linear += 1
                    else:
                        non_linear = 0
                    if non_linear > 1:
                        master_log.append(f"Points ({i - 2}, {i - 1}, {i}): only two consecutive points can share the same t value")
            else:
                master_log.append(f"Point {i}: t must be within [0, 1] range")

        # Walidacja części intensity:
        if self.Direction_type_box.currentText() in {"Normal", "Axial", "factor_XZ"}:
            raw_val = True if self.MainWindow.data_type == "symbolic" else False
            base_intensity, flag = self.validate_widget_val(widget = self.Base_intensity_line, sym_key = "distributed_load", flag = True, return_val = True, raw_val = raw_val)
            if not flag:
                master_log.append(f"Invalid Base Density value: {base_intensity}, couldn't convert to float")
            Ax_val, flag = self.validate_widget_val(widget = self.X_intensity_line, sym_key = "dimensionless", flag = True, return_val = True, raw_val = raw_val)
            if not flag:
                master_log.append(f"Invalid Axial factor value: {Ax_val}, couldn't convert to float")
            Norm_val, flag = self.validate_widget_val(widget = self.Z_intensity_line, sym_key = "dimensionless", flag = True, return_val = True, raw_val = raw_val)
            if not flag:
                master_log.append(f"Invalid Normal factor value: {Norm_val}, couldn't convert to float")
            if master_log:
                dialog = ListReportLog(self, title = "Load Distribution - Validation Error", 
                                                    label_text = "The load distribution could not be applied due to invalid entries:", 
                                                    display_list = master_log)
                dialog.exec()
                return False
            intensity_settings = {"d_type": self.Direction_type_box.currentText(),
                                "Ax_factor": Ax_val,
                                "Norm_factor": Norm_val}
            
        elif self.Direction_type_box.currentText() == "at_angle":
            base_intensity, flag = self.validate_widget_val(widget = self.Base_intensity_line, sym_key = "distributed_load", flag = True, return_val = True, raw_val = True)
            if not flag:
                master_log.append(f"Invalid Base Density value: {base_intensity}, couldn't convert to float")
            L_angle, flag = self.validate_widget_val(widget = self.Distribution_angle_line, sym_key = "angle", flag = True, return_val = True)
            if not flag:
                master_log.append(f"Invalid Distribution Angle value: {L_angle}, couldn't convert to float")
            if master_log:
                dialog = ListReportLog(self, title = "Load Distribution - Validation Error", 
                                        label_text = "The load distribution could not be applied due to invalid entries:", 
                                        display_list = master_log)
                dialog.exec()
                return False
            
            if self.MainWindow.data_type == "symbolic":              
                # Dokładny kąt w radianach:
                L_angle_float = self.LoadsCore.validate_val(val = L_angle, sym_key = "angle")
                angle_round = round(L_angle_float, 6)
                angle_sym = sp.Rational(str(angle_round))
                angle_rad = angle_sym / 180 * sp.pi
                Ax_val = str(sp.cos(angle_rad))
                Norm_val = str(sp.sin(angle_rad))
            else:
                Ax_val = np.cos(np.deg2rad(L_angle))
                Norm_val = np.sin(np.deg2rad(L_angle))

            intensity_settings = {"d_type": self.Direction_type_box.currentText(),
                                "L_angle": L_angle,
                                "Ax_factor": Ax_val,
                                "Norm_factor": Norm_val}

        # tworzenie słownika zapisu
        if self.MainWindow.data_type == "symbolic":
            t_list = raw_t_vals
            f_list = raw_f_vals
        else:
            t_list = abs_t_vals
            f_list = abs_f_vals
        points = []
        for i, t_val in enumerate(t_list, 0):
            points.append({"t": t_val, "val": f_list[i]})

        load_data = {"type": self.convert_type_name(self.Formula_type_box.currentText()),
                    "n_points": num_of_pts,
                    "axial_factor": intensity_settings["Ax_factor"],
                    "normal_factor": intensity_settings["Norm_factor"],
                    "base_intensity": base_intensity,
                    "points": points}
        
        self.distribution_dict = {"origin": False,
                            "load_data": load_data,
                            "intensity_settings": intensity_settings}
        return True
        
    # Funkcja zapisująca zmiany:
    def save_changes(self, delete = False):
        # sprawdzenie czy inputy są poprawne:
        if not self.validate_inputs() and not delete:
            return
        if self.dialog_mode == "add":
            key = self.LoadsCore.generate_unique_key(self.LoadsCore.element_loads, self.dict_id)
            self.dialog_mode = "edit"
            self.dict_id = key
            self.setWindowTitle("Edit Element Load distribution")
            self.element_label.setText(f"Edit load distribution id: {self.dict_id}, Element ID: {self.LoadsCore.get_meshOBJ_id(self.dict_id)}")
            self.apply_btn.setText("Apply changes")
        else:
            key = self.dict_id
        if delete:
            self.dialog_mode = "add"
            self.dict_id = self.LoadsCore.get_meshOBJ_id(self.dict_id)
            self.element_label.setText(f"Apply load distribution to element ID: {self.dict_id}")
            self.setWindowTitle("New Element Load distribution")
            self.apply_btn.setText("Apply Load distribution")
            del self.LoadsCore.element_loads[key]
            self.numerical_distribution = None
            self.symbolic_distribution = None
            # wymazanie:
            self.canvas_settings()
            self.canvas.remove_visualOBJ(self.LoadsCore.drawn_loadOBJ["element"][key])
            self.LoadsCore.draw_load_selection(cancel = True)
        else:
            self.LoadsCore.element_loads[key] = copy.deepcopy(self.distribution_dict)
            sym_dict = None if self.MainWindow.data_type != "symbolic" else self.LoadsCore.load_symbol_substitutes
            self.Distribution_Class = FormulateDistribution(load_data = self.LoadsCore.element_loads[key]["load_data"], sym_dict = sym_dict, sympy_local = sympy_LOCAL)
            self.numerical_distribution = self.Distribution_Class.SymPy_dimensionless(numerical = True)
            self.symbolic_distribution = self.Distribution_Class.SymPy_dimensionless()
            # tutaj rysowanie
            self.compose_canvas()
            self.LoadsCore.draw_element_load(obj_id = self.dict_id, draw = True)
            self.LoadsCore.draw_load_selection(obj_type = "element_loads", obj_id = self.dict_id)

        # refreshowanie GUI i list
        self.Refresh_GUI()
        self.LoadsCore.generate_load_lists(e_load = True)

    def save_close(self):
        if not self.validate_inputs():
            return
        else:
            self.save_changes()
            self.close_dialog()

    def close_dialog(self):
        self.accept()


# ======================================== 
# Dialog okna manipulcaji obciążeniem regionalnym
# ======================================== EDYTOR OBCIĄŻEŃ
class RegionLoadManager(QDialog):
    def __init__(self, parent = None, canvas = None, LoadsCore = None, mode = "add", obj_id = None):
        super().__init__(parent)
        
        self.MainWindow = parent
        self.canvas = canvas
        self.LoadsCore = LoadsCore
        self.dialog_mode = mode
        self.dict_id = obj_id
        self.current_method = None

        if mode == "add":
            title = "New Region Load"
            label_txt = f"Define new Region Load"
            apply_txt = "Apply Region Load"
        else:
            title = "Edit Region Load"
            label_txt = f"Edit Region Load: {self.dict_id}"
            apply_txt = "Apply changes"

        self.setWindowTitle(f"{title}")
        self.setModal(False)
        self.setMaximumWidth(500)
        self.setMinimumHeight(350)

        # pobranie skrajnych indeksów elementów:
        self.first_el_id = next(iter(sorted(self.canvas.elements)))
        self.last_el_id = next(reversed(sorted(self.canvas.elements)))
        
        main_lt = QVBoxLayout(self)
        main_h_lt = QHBoxLayout()
        self.main_v_lt = QVBoxLayout()
        main_h_lt.addLayout(self.main_v_lt, 3)
        self.right_lt = QVBoxLayout()
        main_h_lt.addLayout(self.right_lt, 2)

        self.main_label = QLabel(f"{label_txt}")
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_label_font = self.main_label.font()
        main_label_font.setPointSize(14)
        self.main_label.setFont(main_label_font)
        self.main_v_lt.addWidget(self.main_label)
        main_lt.addLayout(main_h_lt)

        # Layout prawy z listą elementów:
        target_label = QLabel("Target Elements (ID)")
        target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        target_font = target_label.font()
        target_font.setPointSize(12)
        target_label.setFont(target_font)
        # lista:
        self.target_list = QListWidget()
        self.right_lt.addWidget(target_label)
        self.right_lt.addWidget(self.target_list)


        bottom_lt = QHBoxLayout()
        main_lt.addLayout(bottom_lt)
        self.apply_btn = QPushButton(f"{apply_txt}")
        apply_close = QPushButton("Apply & Close")
        close_btn = QPushButton("Close")
        bottom_lt.addWidget(self.apply_btn)
        bottom_lt.addWidget(apply_close)
        bottom_lt.addWidget(close_btn)
        close_btn.clicked.connect(self.close_dialog)
        apply_close.clicked.connect(self.save_close)
        self.apply_btn.clicked.connect(self.save_changes)
        # usuwanie focusa:
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.apply_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        apply_close.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # wywoływanie budowy reszty GUI:
        self.build_method_GUI()
        self.build_regionGUI()

    # Funkcja refreshująca
    def Refresh_GUI(self, upper = False, down = False):
        # funkcja usuwająca widgety i layouty:
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item
        if upper:
            clear_layout(self.method_lt)
            self.build_method_GUI()
        if down:
            clear_layout(self.region_lt)
            self.build_regionGUI()

        return

    # narzędzie tworzenia parametrowego widgetu:
    def make_param_widget(self, parent_lt, widget, label_txt = "", font_size = 9, stretch = True, list = None, current_text = lambda: None, return_lt = False):
        local_lt = QHBoxLayout()
        parent_lt.addLayout(local_lt)
        label = QLabel(f"{label_txt}")
        label_font = label.font()
        label_font.setPointSize(font_size)
        label.setFont(label_font)
        new_widget = widget
        local_lt.addWidget(label)
        local_lt.addWidget(new_widget)
        if stretch:
            local_lt.addStretch()
        if list:
            new_widget.addItems(list)
            try:
                item = current_text() if callable(current_text) else current_text
                if item:
                    new_widget.setCurrentText(str(item))
            except Exception:
                pass
        else:
            try:
                item = current_text() if callable(current_text) else current_text
                if item:
                    new_widget.setText(f"{item}")
            except Exception:
                pass
        if return_lt:
            return local_lt, new_widget
        return new_widget

    # funkcja tłumacząca klucze:
    def convert_names(self, source = "method", name = ""):
        if source == "method":
            if name == "Inherit from element Load":
                return "inherit_load"
            elif name == "Closed Contour":
                return "closed_contour"
            elif name == "inherit_load":
                return "Inherit from element Load"
            elif name == "closed_contour":
                return "Closed Contour"
            else:
                return None
            
        elif source == "element_load":
            name = str(name).strip()
            if name.split(";") == name:
                for l_name in self.LoadsCore.ELEMENT_LOAD_LIST:
                    if l_name.strip().split(";")[0] == name:
                        return l_name
            else:
                return name.strip().split(";")[0]
            return None
        
        elif source == "direction":
            if name == "At Angle":
                return "at_angle"
            elif name == "at_angle":
                return "At Angle"
            elif name == "Factor components (X, Z)":
                return "factor_xz"
            elif name == "factor_xz":
                return "Factor components (X, Z)"
    
    # Generowanie GUI typu:
    def build_method_GUI(self):
        def get_name(name):
            try:
                name = name() if callable(name) else name
                return name
            except Exception:
                return None
        
        def Load_method_change():
            self.current_method = self.convert_names("method", self.Load_methodBox.currentText())
            self.Refresh_GUI(upper = True, down = True)

        def direction_change():
            self.current_direction = self.directionBox.currentText()
            self.Refresh_GUI(upper = True)
        
        self.method_lt = QVBoxLayout()
        self.main_v_lt.addLayout(self.method_lt)
        if self.dialog_mode == "edit":
            self.current_method = get_name(lambda: self.LoadsCore.region_loads[self.dict_id]["method"])
            self.Reference_Load_id = get_name(lambda:self.convert_names("element_load", self.LoadsCore.region_loads[self.dict_id]["reference_load"]))
            self.current_intensity_line = get_name(lambda:self.LoadsCore.region_loads[self.dict_id]["load_data"]["intensity"])
            self.current_angle_line = get_name(lambda:self.LoadsCore.region_loads[self.dict_id]["load_data"]["angle"])
            self.current_x_fac_line = get_name(lambda:self.LoadsCore.region_loads[self.dict_id]["load_data"]["x_factor"])
            self.current_z_fac_line = get_name(lambda:self.LoadsCore.region_loads[self.dict_id]["load_data"]["z_factor"])

        self.Load_methodBox = self.make_param_widget(self.method_lt, QComboBox(), "Method: ", font_size = 12, 
                                                     list = ["Inherit from element Load", "Closed Contour"], 
                                                     current_text = lambda: self.convert_names(source = "method", name = self.current_method))
        self.current_method = self.convert_names(source = "method", name = self.Load_methodBox.currentText())
        self.Load_methodBox.currentTextChanged.connect(Load_method_change)

        if self.Load_methodBox.currentText() == "Inherit from element Load":
            label = QLabel("Assigns selected elements to inherit\nparameters from a reference load.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.method_lt.addWidget(label)
            self.RefElBox = self.make_param_widget(self.method_lt, QComboBox(), "Reference Load: ", font_size = 10, 
                                                     list = self.LoadsCore.ELEMENT_LOAD_LIST, stretch = False,
                                                     current_text = lambda: self.Reference_Load_id)
        else:
            label = QLabel("Defines a closed region by points and\napplies a continuous load to all enclosed elements.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.method_lt.addWidget(label)
            self.LoadIntensityLine = self.make_param_widget(self.method_lt, QLineEdit(), "Continuous load intencity: ", 10, 
                                                            current_text = lambda: self.current_intensity_line)
            
            self.directionBox = self.make_param_widget(self.method_lt, QComboBox(), "Load vector: ", font_size = 10, 
                                                        list = ["At Angle", "Factor components (X, Z)"], 
                                                        current_text = lambda: self.current_direction)
            self.directionBox.currentTextChanged.connect(direction_change)
            if self.directionBox.currentText() == "At Angle":
                if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                    ang_lt, self.Angle_Line = self.make_param_widget(self.method_lt, QLabel("90"), "angle (°): ", return_lt = True, stretch = False)
                    PBAlabel = QLabel("(PBA topology only supports vertical loads)")
                    PBAlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    ang_lt.addWidget(PBAlabel)
                    ang_lt.addStretch()
                else:
                    self.Angle_Line = self.make_param_widget(self.method_lt, QLineEdit(), "angle (°): ", current_text = lambda: self.current_angle_line)
            else:
                if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                    x_lt, self.X_factor_Line = self.make_param_widget(self.method_lt, QLabel("0"), "X factor:", return_lt = True, stretch = False)
                    self.Z_factor_Line = self.make_param_widget(self.method_lt, QLineEdit(), "Z factor: ", current_text = lambda: self.current_z_fac_line)
                    PBAlabel = QLabel("(PBA topology only supports vertical loads)")
                    PBAlabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    x_lt.addWidget(PBAlabel)
                    x_lt.addStretch()
                else:
                    self.X_factor_Line = self.make_param_widget(self.method_lt, QLineEdit(), "X factor: ", current_text = lambda: self.current_x_fac_line)
                    self.Z_factor_Line = self.make_param_widget(self.method_lt, QLineEdit(), "Z factor: ", current_text = lambda: self.current_z_fac_line)

        self.method_lt.addStretch()           
        return
    
    # Budowanie GUI dolnego:
    def build_regionGUI(self):
        self.region_lt = QVBoxLayout()
        self.main_v_lt.addLayout(self.region_lt)
        
        if self.dialog_mode == "edit":
            self.elements_id_list = self.LoadsCore.region_loads[self.dict_id]["range"]
            self.fill_target_list(self.elements_id_list)
        
        if self.current_method == "inherit_load":
            self.setMaximumHeight(350)
            def manage_set_mode(btn):
                if btn == "set":
                    self.ElSetMode = "set"
                    self.Set_line_1.setEnabled(True)
                    self.Set_line_2.setEnabled(True)
                    self.single_id_line.setEnabled(False)
                elif btn == "single":
                    self.ElSetMode = "single"
                    self.Set_line_1.setEnabled(False)
                    self.Set_line_2.setEnabled(False)
                    self.single_id_line.setEnabled(True)

            # label
            set_label = QLabel("Element Set Definition")
            set_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            set_label_font = set_label.font()
            set_label_font.setPointSize(11)
            set_label.setFont(set_label_font)
            self.region_lt.addWidget(set_label)
            # pokazanie skrajnych elementów
            self.region_lt.addWidget(QLabel(f"Element ID range in mesh file: {self.first_el_id} - {self.last_el_id}"))

            local_h_lt, self.Set_line_1 = self.make_param_widget(parent_lt = self.region_lt,
                                                               widget = QLineEdit(),
                                                               label_txt = "from: ",
                                                               return_lt = True,
                                                               stretch = False)
            set_btn = QPushButton("Element set")
            self.ElSetMode = "set"
            local_h_lt.insertWidget(0, set_btn)
            local_h_lt.addWidget(QLabel("ID"))
            self.Set_line_2 = self.make_param_widget(parent_lt = local_h_lt,
                                                    widget = QLineEdit(),
                                                    label_txt = "to: ",
                                                    stretch = False)
            local_h_lt.addWidget(QLabel("ID"))
            local_h_lt.addStretch()

            local_h_lt2, self.single_id_line = self.make_param_widget(parent_lt = self.region_lt,
                                                                    widget = QLineEdit(),
                                                                    label_txt = "ID: ",
                                                                    stretch = False,
                                                                    return_lt = True)
            single_btn = QPushButton("Single element:")
            self.single_id_line.setEnabled(False)
            local_h_lt2.insertWidget(0, single_btn)
            local_h_lt2.addStretch()

            # Sterowanie typem wprowadzenia:
            set_btn.clicked.connect(lambda: manage_set_mode("set"))
            single_btn.clicked.connect(lambda: manage_set_mode("single"))

            bottom_btns_lt = QHBoxLayout()
            self.region_lt.addLayout(bottom_btns_lt)
            add_btn = QPushButton("add")
            add_btn.clicked.connect(lambda: self.ModifyInheritList(mode = "add"))
            remove_btn = QPushButton("remove")
            remove_btn.clicked.connect(lambda: self.ModifyInheritList(mode = "remove"))
            clear_btn = QPushButton("clear all")
            clear_btn.clicked.connect(lambda: self.ModifyInheritList(mode = "clear"))
            bottom_btns_lt.addWidget(add_btn)
            bottom_btns_lt.addWidget(remove_btn)
            bottom_btns_lt.addWidget(clear_btn)
                   
        elif self.current_method == "closed_contour":
            if self.dialog_mode == "edit":
                self.polygon_points = self.LoadsCore.region_loads[self.dict_id]["points"]
            elif not hasattr(self, "polygon_points") or self.polygon_points is None:
                self.polygon_points = {"1": ["", ""], "2": ["", ""], "3": ["", ""]}

            def remove_point(n_pt):
                last_pt = max(self.polygon_points, key = int)
                # jeśli jest to ostatni punkt
                if last_pt == n_pt:
                    del self.polygon_points[n_pt]
                else:
                    for cur_pt in self.polygon_points.keys():
                        if int(n_pt) <= int(cur_pt) and cur_pt != last_pt:
                            moved_point = self.polygon_points[f"{int(cur_pt) + 1}"]
                            self.polygon_points[cur_pt] = moved_point
                    # usuwanie ostatniego:
                    del self.polygon_points[last_pt]
                self.Refresh_GUI(down = True)
            
            def make_points_lt(parent_lt, n_pt, delete = False):
                local_lt = QHBoxLayout()
                parent_lt.addLayout(local_lt)
                local_lt.addWidget(QLabel(f"Point {n_pt}: "))
                X_line = self.make_param_widget(local_lt, QLineEdit(), "X: ",
                                                stretch = False, current_text = lambda: self.polygon_points[n_pt][0])
                Z_line = self.make_param_widget(local_lt, QLineEdit(), "Z: ",
                                                                stretch = False, current_text = lambda: self.polygon_points[n_pt][1])
                if delete:
                    delete_btn = QPushButton("Del point")
                    delete_btn.setStyleSheet("background-color: red; color: white")
                    local_lt.addWidget(delete_btn)
                    delete_btn.clicked.connect(lambda: remove_point(n_pt))

                local_lt.addStretch()
                return {"X": X_line, "Z": Z_line}
                
            self.setMinimumHeight(650)

            # label
            set_label = QLabel("Boundary Definition")
            set_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            set_label_font = set_label.font()
            set_label_font.setPointSize(11)
            set_label.setFont(set_label_font)
            self.region_lt.addWidget(set_label)

            # generowanie listy punktów:
            self.region_points_lines = {}
            for n_pt in self.polygon_points.keys():
                self.region_points_lines[n_pt] = {}
                if int(n_pt) <= 3:
                    self.region_points_lines[n_pt] = make_points_lt(self.region_lt, n_pt, delete = False)
                else:
                    self.region_points_lines[n_pt] = make_points_lt(self.region_lt, n_pt, delete = True)

            # pobranie ostatniego punktu:
            max_index = int(max(self.polygon_points.keys(), key = int))
            if max_index >= 10:
                max_pt_label = QLabel("Maximum number of points reached (10)")
                max_pt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.region_lt.addWidget(max_pt_label)
            else:
                def add_point():
                    new_index = f"{max_index + 1}"
                    self.polygon_points[new_index] = ["", ""]
                    self.Refresh_GUI(down = True)

                add_pt_btn = QPushButton("Add point")
                self.region_lt.addWidget(add_pt_btn)
                add_pt_btn.clicked.connect(add_point)
            project_btn = QPushButton("Project points on Canvas")
            project_btn.clicked.connect(self.SavePolygonPts)
            self.region_lt.addWidget(project_btn)

        if self.dialog_mode == "edit":
            delete_btn = QPushButton("Delete Region Load")
            delete_btn.setStyleSheet("background-color: red; color: white")
            self.region_lt.addWidget(delete_btn)

        self.region_lt.addStretch()

        return

    # Funkcja wypłniająca listę:
    def fill_target_list(self, list):
        self.target_list.clear()
        el_list = []
        final_list = []
        if not list:
            return

        list_sorted = sorted(list)
        start_id = previous_id = list_sorted[0]
        if len(list_sorted) == 1:
            final_list = [f"{start_id}"]
        else:
            # grupowanie
            for e_id in list_sorted[1:]: # końcówka oznacza że zaczynamy od drugiego elementu listy:
                if int(e_id) == previous_id + 1:
                    previous_id = int(e_id)
                else:
                    el_list.append(f"[{start_id}]" if previous_id == start_id else f"[{start_id}; {previous_id}]")
                    start_id = previous_id = int(e_id)
            # zapisanie ostatniego przedziału:
            el_list.append(f"[{start_id}]" if previous_id == start_id else f"[{start_id}; {previous_id}]")

            # upakowanie do jednej linijki
            for i, row in enumerate(el_list, 0):
                if i % 3 == 0 or i == 0:
                    final_list.append(f"{row}")
                else:
                    final_list[-1] = f"{final_list[-1]} \u222a {row}"

        self.target_list.addItems(final_list)

    # Funkcja modyfikująca listę elementów:
    def ModifyInheritList(self, mode = None):
        # czyszczenie:
        if mode == "clear":
            ok_box = QMessageBox.information(self, "Clearing all affected elements",
                                             "This action is irreversable, do you want to proceed?",
                                             QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)
            if ok_box == QMessageBox.StandardButton.Ok:
                self.elements_id_list = []
                self.fill_target_list(self.elements_id_list)

            return
        
        # sprawdzenie czy id elementów istnieją:
        def check_int_val(widget):
            try:
                new_val = int(widget.text())
                widget.setStyleSheet("")
                return new_val
            except Exception:
                widget.setStyleSheet("background-color: red; color: white")
                return False
            
        def check_id(e_id, widget):
            if e_id in self.canvas.elements:
                return True
            else:
                widget.setStyleSheet("background-color: red; color: white")
                return False

        if self.ElSetMode == "set":
            error_log = []
            id_1 = check_int_val(self.Set_line_1)
            if not id_1:
                error_log.append(f"Error - provided element id: {self.Set_line_1.text()} cannot be converted to integer")
            else:
                if not check_id(id_1, self.Set_line_1):
                    error_log.append(f"Error - provided element id: {self.Set_line_1.text()} is not present in mesh file")

            id_2 = check_int_val(self.Set_line_2)
            if not id_2:
                error_log.append(f"Error - provided element id: {self.Set_line_2.text()} cannot be converted to integer")
            else:
                if not check_id(id_2, self.Set_line_2):
                    error_log.append(f"Error - provided element id: {self.Set_line_2.text()} is not present in mesh file")

            # sprawdzenie czy nie są te same wartości:
            if id_1 == id_2:
                error_log.append(f"Element IDs cannot be the same ({id_1} = {id_2})")
                self.Set_line_1.setStyleSheet("background-color: red; color: white")
                self.Set_line_2.setStyleSheet("background-color: red; color: white")

            if error_log:
                dialog = ListReportLog(self, title = "Invalid Element set definition", 
                                       label_text = "Error log:", 
                                       minimum_width = 300, minimum_height = 200, 
                                       display_list = error_log)
                dialog.exec()
                return
            # tworzenie zbiorów:
            new_el_ids = set()
            if id_1 < id_2:
                pass
            else:
                first_id = id_2
                id_2 = id_1
                id_1 = first_id
            
            while id_1 <= id_2:
                new_el_ids.add(id_1)
                id_1 += 1
            
        elif self.ElSetMode == "single":
            error_log = []
            s_id = check_int_val(self.single_id_line)
            if not s_id:
                error_log.append(f"Error - provided element id: {self.single_id_line.text()} cannot be converted to integer")
            else:
                if not check_id(s_id, self.single_id_line):
                    error_log.append(f"Error - provided element id: {self.single_id_line.text()} is not present in mesh file")
        
            if error_log:
                dialog = ListReportLog(self, title = "Invalid Element set definition", 
                                        label_text = "Error log:", 
                                        minimum_width = 300, minimum_height = 200, 
                                        display_list = error_log)
                dialog.exec()
                return
            new_el_ids = set()
            new_el_ids.add(s_id)    

        # konwertowanie listy do zbioru:
        if not hasattr(self, "elements_id_list") or self.elements_id_list is None:
            target_id_set = set()
        else:
            target_id_set = set(sorted(self.elements_id_list))

        # listy elementów w zbiorze
        in_set_list = []
        not_in_set_list = []
        for new_id in new_el_ids:
            if new_id in target_id_set:
                in_set_list.append(new_id)
            else:
                not_in_set_list.append(new_id)

        if mode == "add":
            if not not_in_set_list:
                QMessageBox.warning(self, "Invalid Element IDs",
                                    "Provided ID range is already present in\n"
                                    "affected element set")
                return
            else:
                target_id_set.update(new_el_ids)

                # konwersja do listy
                self.elements_id_list = list(target_id_set)

                # Wyświetlenie komunikatu:
                if in_set_list:
                    display_list = []
                    for i, in_id in enumerate(in_set_list, 0):
                        if i % 4 == 0 or i == 0:
                            display_list.append(f"{in_id}")
                        else:
                            display_list[-1] = f"{display_list[-1]}, {in_id}"

                    dialog = ListReportLog(self, title = "Note - overlapping element IDs", 
                                                    label_text = "Some IDs were already present in element set:", 
                                                    minimum_width = 300, minimum_height = 200, 
                                                    display_list = display_list)
                    dialog.exec()
        elif mode == "remove":
            if not in_set_list:
                QMessageBox.warning(self, "Invalid Element IDs",
                                    "Provided ID range is not present in\n"
                                    "affected element set")
                return
            else:
                # usuwanie elementów:
                target_id_set -= new_el_ids

                # konwersja do listy
                self.elements_id_list = list(target_id_set)

                # Wyświetlenie komunikatu:
                if not_in_set_list:
                    display_list = []
                    for i, in_id in enumerate(not_in_set_list, 0):
                        if i % 4 == 0 or i == 0:
                            display_list.append(f"{in_id}")
                        else:
                            display_list[-1] = f"{display_list[-1]}, {in_id}"

                    dialog = ListReportLog(self, title = "Note - element IDs not present", 
                                                    label_text = "Some IDs are not present in element set:", 
                                                    minimum_width = 300, minimum_height = 200, 
                                                    display_list = display_list)
                    dialog.exec()
        # aktualizowanie listy:
        self.fill_target_list(self.elements_id_list)
        if self.ElSetMode == "set":
            self.Set_line_1.setText("")
            self.Set_line_2.setText("")
        elif self.ElSetMode == "single":
            self.single_id_line.setText("")

    # funkcja walidująca widget:
    def validate_widget(self, widget, sym_key = None, return_val = True):
        val = widget.text()
        val, flag = self.LoadsCore.validate_val(val = val, sym_key = sym_key, flag = True)
        if not flag:
            widget.setStyleSheet("background-color: red; color: white")
        else:
            widget.setStyleSheet("")
        if return_val:
            return val, flag
        return flag
    
    # Funkcja zapisująca słownik punktów i rysująca je:
    def SavePolygonPts(self):
        if hasattr(self, "drawnPolygonPts") and self.drawnPolygonPts is not None:
            self.canvas.remove_visualOBJ(self.drawnPolygonPts)
            self.canvas.draw()
        # walidacja punktów:
        error_log = []
        new_pt_dict = {}
        seen_points = set()
        x_list = []
        z_list = []
        for n_pt, lt_dict in self.region_points_lines.items():
            X_val, flag = self.validate_widget(lt_dict["X"], "length", True)
            if not flag:
                error_log.append(f"Couldnt convert to float X: {X_val}, pt: {n_pt}")
            Z_val, flag = self.validate_widget(lt_dict["Z"], "length", True)
            if not flag:
                error_log.append(f"Couldnt convert to float Z: {Z_val}, pt: {n_pt}")
            if self.MainWindow.data_type == "symbolic":
                new_pt_dict[n_pt] = [lt_dict["X"].text(), lt_dict["Z"].text()]
            else:
                new_pt_dict[n_pt] = [X_val, Z_val]

            # sprawdzenie czy nie powtażają się wartości:
            if not error_log:
                pt = (round(X_val, 14), round(Z_val, 14))
            if pt in seen_points:
                error_log.append("Error - some points have the same coordinates")
                lt_dict["X"].setStyleSheet("background-color: red; color: white")
                lt_dict["Z"].setStyleSheet("background-color: red; color: white")
            else:
                seen_points.add(pt)
            
            x_list.append(round(X_val, 14))
            z_list.append(round(Z_val, 14))
            
        if error_log:
            dialog = ListReportLog(self, title = "Invalid point coordinates", label_text = "Invalid values:", 
                                   display_list = error_log, minimum_width = 250, minimum_height = 250)
            dialog.exec()
            return

        self.polygon_points = new_pt_dict

        # rysowanie:
        x_list.append(x_list[0])
        z_list.append(z_list[0])
        n_pts = len(x_list)
        vis_dict = self.LoadsCore.get_selection_visual_dict()
        # rysowanie linii:
        self.drawnPolygonPts = {}
        self.drawnPolygonPts["lines"] = self.canvas.axes.plot(x_list, z_list, linestyle = vis_dict["linestyle"], 
                                            linewidth = vis_dict["linewidth"], 
                                            color = vis_dict["color"], 
                                            alpha = vis_dict["transparency"])
        label_list = []
        for i, x_val in enumerate(x_list, 1):
            if i == n_pts:
                break
            label = self.canvas.axes.text(x_val, z_list[i - 1], f"Point {i}",
                                        color = vis_dict["text_color"],
                                        ha = 'center',  # wyśrodkowanie w poziomie
                                        va = 'center',  # wyśrodkowanie w pionie
                                        fontsize = vis_dict["text_size"],
                                        alpha = vis_dict["text_transparency"],
                                        bbox = dict(
                                                boxstyle = 'round,pad=0.15',
                                                fc = 'white',
                                                ec = 'none',
                                                alpha = vis_dict["textBOX_transparency"]))
            label_list.append(label)
        self.drawnPolygonPts["labels"] = label_list
        self.canvas.draw()


    def save_changes(self, delete = False):
        return

    def save_close(self):
        self.save_changes()
        self.close_dialog()
        return

    def close_dialog(self):
        self.accept()   


# ======================================== 
# Klasa matka odpowiedzialna za rysowanie i komponowanie słowników
# ======================================== EDYTOR OBCIĄŻEŃ
class LoadMeshEditorCore:
    def __init__(self, MainWindow, canvas):
        self.MainWindow = MainWindow
        self.canvas = canvas

        # Słownik podstawowych ustawień gradicznych:
        self.LoadsVisaul_dict = self.canvas.load_mesh_visual_settings
        # self.MainWindow.old_load_mesh

    # Funkcja dobierania nazwy klucza:
    def generate_unique_key(self, obj_dict, base_id):
        key = str(base_id)
        if key not in obj_dict:
            return key
        suffix = 1
        new_key = f"{key}_{suffix}"
        while new_key in obj_dict:
            suffix += 1
            new_key = f"{key}_{suffix}"
        return new_key

    # może się przyda
    def get_meshOBJ_id(self, load_key):
        if isinstance(load_key, int):
            return load_key
        else:
            return int(load_key.split('_')[0])

    # Walidacja wartości:
    def validate_val(self, val, sym_key, flag = False, return_raw = False, force_sympy = False):
        # Próba zamiana na float:
        try:
            abs_val = float(val)
            if flag:
                return abs_val, True
            return abs_val
        except Exception:
            if self.MainWindow.data_type != "symbolic" and not force_sympy:
                print(f"not sympy, {self.MainWindow.data_type}")
                if flag:
                    return val, False
                return val
            else:
                try:
                    sym_val = sp.sympify(val, locals = sympy_LOCAL)

                    if self.MainWindow.data_type == "symbolic":
                        abs_val = sym_val.subs(self.load_symbol_substitutes.get(sym_key, {}) | self.load_symbol_substitutes.get("dimensionless", {}))
                    else:
                        abs_val = sp.N(sym_val, 15)

                    abs_val = float(abs_val)
                    if flag and return_raw:
                        return val, True
                    elif flag:
                        return abs_val, True
                    elif return_raw:
                        return val
                    else:
                        return abs_val
                except Exception as e:
                    print(e)
                    if flag:
                        return val, False
                    return val

    # Funkcja generująca listy obciążeń:
    def generate_load_lists(self, n_load = False, e_load = False, r_load = False):
        # czyszczenie list:
        if n_load:
            self.NODE_LOAD_LIST = []
            # funkcja generowania listy węzłowych obciążeń:
            for l_id, l_dict in self.node_loads.items():
                # pobranie wartości:
                x_force, x_flag = self.validate_val(l_dict.get("X", "???"), "force", flag = True)
                z_force, z_flag = self.validate_val(l_dict.get("Z", "???"), "force", flag = True)
                ry_moment, r_flag = self.validate_val(l_dict.get("RY", "???"), "moment_of_force", flag = True)
                if x_flag and z_flag:
                    force = round(np.sqrt(x_force**2 + z_force**2), 6)
                else:
                    force = "CORRUPTED VALUE"
                if not r_flag:
                    ry_moment = "CORRUPTED VALUE"
                self.NODE_LOAD_LIST.append(f"{l_id}; |F| = {force}, R = {ry_moment}")
            # czyszczenie widgetu i wypełnianie go:
            self.MainWindow.node_load_list.clear()
            self.MainWindow.node_load_list.addItems(self.NODE_LOAD_LIST)

        if e_load:
            self.ELEMENT_LOAD_LIST = []
            # funkcja generowania listy węzłowych obciążeń:
            for l_id, l_dict in self.element_loads.items():
                # pobranie wartości:
                type = l_dict["load_data"]["type"]
                base_intensity = l_dict["load_data"]["base_intensity"]
                region_origin = l_dict.get("origin", False)
                if not region_origin:
                    self.ELEMENT_LOAD_LIST.append(f"{l_id}; {type}, base Q: {base_intensity}")
                elif region_origin.split("_")[0] == "ref":
                    self.ELEMENT_LOAD_LIST.append(f"{l_id}; ref for: {region_origin.split("_")[1]}")

             # czyszczenie widgetu i wypełnianie go:
            self.MainWindow.element_load_list.clear()
            self.MainWindow.element_load_list.addItems(self.ELEMENT_LOAD_LIST)

        if r_load:
            self.REGION_LOAD_LIST = []
            # funkcja generowania listy węzłowych obciążeń:
            for l_id, l_dict in self.region_loads.items():
                # pobranie wartości:
                type = l_dict.get("type", "???")
                self.REGION_LOAD_LIST.append(f"{l_id}; type: {type}")

                # czyszczenie widgetu i wypełnianie go:
            self.MainWindow.region_load_list.clear()
            self.MainWindow.region_load_list.addItems(self.REGION_LOAD_LIST)

        return

    # Funkcja wczytania siatki:
    def unpack_load_mesh(self):
        # wczytytanie summary:
        self.load_summary = self.MainWindow.old_load_mesh["load_summary"]
        if self.MainWindow.data_type == "symbolic":
            self.load_symbol_substitutes = self.MainWindow.old_load_mesh["load_symbol_substitutes"]
            if "length" not in self.load_symbol_substitutes:
                try:
                    self.load_symbol_substitutes["length"] = copy.deepcopy(self.canvas.symbol_substitutes["length"])
                except Exception:
                    pass
        self.node_loads = self.MainWindow.old_load_mesh["node_loads"]
        self.element_loads = self.MainWindow.old_load_mesh["element_loads"] 
        self.region_loads = self.MainWindow.old_load_mesh["region_loads"]
        # pobranie visualsów:
        self.usersOBJ_visuals = self.MainWindow.old_load_mesh.get("OBJ_visuals", {"node":{}, "element":{}, "region":{}})
        # generowanie list:
        self.generate_load_lists(True, True, True)
        # inicjowanie słownika narysowanych obiektów:
        self.drawn_loadOBJ = {"node":{}, "element":{}, "region":{}}
        self.drawnSelection_OBJ = None
        # rysowanie:
        self.draw_load_mesh()

    # funkcja rysująca obciążenia:
    def draw_load_mesh(self):
        for obj_id in self.node_loads.keys():
            self.draw_node_load(obj_id)

        # Po prostu dla infa, że długo się będzie wczytywała siatka
        self.el_draw_MessageBOX = False
        for obj_id in self.element_loads.keys():
            self.draw_element_load(obj_id)

        self.canvas.draw()


    # funkcja zapisywania siatki:
    def save_load_mesh(self, copy = False, float_converter = False, visuals = False):
        # Tworzenie odpowiednich słowników
        if float_converter:
            print("NOT IMPLEMENTED YET")
            return
        else:
            l_summary = self.load_summary
            n_loads_dict = self.node_loads
            e_loads_dict = self.element_loads
            r_loads_dict = self.region_loads


        # Ustalenie odpowiedniego kontenera do zapisania
        if float_converter is False and self.MainWindow.data_type == "symbolic":
            dump = {"load_summary": l_summary,
                    "load_symbol_substitutes": self.load_symbol_substitutes,
                    "node_loads": n_loads_dict,
                    "element_loads": e_loads_dict,
                    "region_loads": r_loads_dict}
        else:
            dump = {"load_summary": l_summary,
                    "node_loads": n_loads_dict,
                    "element_loads": e_loads_dict,
                    "region_loads": r_loads_dict}
        if visuals:
            dump.update({"OBJ_visuals": self.usersOBJ_visuals})

        # Pobranie lokalizacji dla siatki obciążeń:
        if not copy:
            load_mesh_path = self.MainWindow.load_mesh_full_path
            with open(load_mesh_path, "w", encoding="utf-8") as load_mesh:
                json.dump(dump, load_mesh, indent = 4)
        else:
            base_path = self.MainWindow.load_mesh_full_path.removesuffix("_Lmsh.json")
            load_mesh_path = base_path + "(copy)_Lmsh.json"
            saved = False
            while not saved:
                try:
                    with open(load_mesh_path, "x", encoding="utf-8") as load_mesh:
                        json.dump(dump, load_mesh, indent = 4)
                        saved = True
                except FileExistsError:
                    base_path = load_mesh_path.removesuffix("_Lmsh.json")
                    load_mesh_path = base_path + "_(copy)_Lmsh.json"

    # ========================== Rysowania
    # tworzenie podstawowego słownika wiaualnego:
    def get_default_visual_dict(self):
        return {"load_scale": self.LoadsVisaul_dict["load_scale"],
                "color": self.LoadsVisaul_dict["loads_color"],
                "text_color": self.LoadsVisaul_dict["text_color"],
                "linewidth": self.LoadsVisaul_dict["thicc_line"],
                "linewidth_thinn": self.LoadsVisaul_dict["thinn_line"],
                "transparency": self.LoadsVisaul_dict["loads_transparency"],
                "linestyle": self.LoadsVisaul_dict["loads_linestyle"],
                "text_size": self.LoadsVisaul_dict["text_size"],
                "text_transparency": self.LoadsVisaul_dict["text_transparency"],
                "textBOX_transparency": self.LoadsVisaul_dict["textBOX_transparency"]}

    # tworzenie słownika dla podkreśleń:
    def get_selection_visual_dict(self):
        return {"load_scale": self.LoadsVisaul_dict["load_scale"],
                "color": self.LoadsVisaul_dict["selection_color"],
                "text_color": self.LoadsVisaul_dict["text_color"],
                "linewidth": self.LoadsVisaul_dict["selection_thickness"],
                "linewidth_thinn": (self.LoadsVisaul_dict["thinn_line"] + self.LoadsVisaul_dict["selection_thickness"]) / 2,
                "transparency": self.LoadsVisaul_dict["selection_transparency"],
                "linestyle": self.LoadsVisaul_dict["loads_linestyle"],
                "text_size": self.LoadsVisaul_dict["text_size"],
                "text_transparency": self.LoadsVisaul_dict["text_transparency"],
                "textBOX_transparency": self.LoadsVisaul_dict["textBOX_transparency"],
                "marker_size": self.canvas.selection_size}

    # funkcja rysująca zaznaczenie:
    def draw_load_selection(self, obj_type = None, obj_id = None, cancel = False):
        if hasattr(self, "drawnSelection_OBJ") and self.drawnSelection_OBJ is not None:
            self.canvas.remove_visualOBJ(self.drawnSelection_OBJ)
            if cancel or obj_type not in {"node_loads", "element_loads", "region_load"}:
                self.canvas.draw()
                return
        if obj_type == "node_loads":
            self.draw_node_load(obj_id, selection = True)
        elif obj_type == "element_loads":
            self.draw_element_load(obj_id, selection = True)
        elif obj_type == "region_load":
            return
        self.canvas.draw()
        return
    
    # rysowanie strzałki:
    def draw_arrow(self, point_1 = [0,0], point_2 = [1,1], visual_dict = {}, type = None):
        def draw_arrow(vis_dict):
            color = vis_dict["color"]
            transparency = vis_dict["transparency"]
            linestyle = vis_dict["linestyle"]
            dx = point_2[0] - point_1[0]
            dz = point_2[1] - point_1[1]
            length = np.hypot(dx, dz)
            theta = np.arctan2(dz, dx)
            # tworzenie sprzałki:
            if type != "hatch":
                linewidth = vis_dict["linewidth"]
                tip_div = 5
                x_div = 2
                z_div = 3
            else:
                tip_div = 10
                x_div = 0.65
                z_div = 3
                linewidth = vis_dict["linewidth_thinn"]
            l_tip = length / tip_div
            # grot strzałki
            x_flat_tip = np.array([-l_tip/x_div, 0, -l_tip/x_div])
            z_flat_tip = np.array([l_tip/z_div, 0, -l_tip/z_div])
            # linia:
            x_flat = np.array([-length, 0])
            z_flat = np.array([0, 0])
            # obrót i przenoszenie
            x_origin = point_2[0]
            z_origin = point_2[1]
            x_tip_final = x_flat_tip * np.cos(theta) - z_flat_tip * np.sin(theta) + x_origin
            z_tip_final = x_flat_tip * np.sin(theta) + z_flat_tip * np.cos(theta) + z_origin
            x_final = x_flat * np.cos(theta) - z_flat * np.sin(theta) + x_origin
            z_final = x_flat * np.sin(theta) + z_flat * np.cos(theta) + z_origin
            # rysowanie:
            tip = self.canvas.axes.plot(x_tip_final, z_tip_final, 
                                        linestyle = linestyle, 
                                        linewidth = linewidth, 
                                        color = color, 
                                        alpha = transparency)
            line = self.canvas.axes.plot(x_final, z_final, 
                                        linestyle = linestyle, 
                                        linewidth = linewidth, 
                                        color = color, 
                                        alpha = transparency)
            return {"line": line, "tip": tip}

        try:
            drawn_arrow = draw_arrow(vis_dict = visual_dict)
        except Exception as e:
            print(f"An error occured while drawing arrow:\n{e}")
            vis_dict = self.get_default_visual_dict()
            drawn_arrow = draw_arrow(vis_dict = vis_dict)
        
        return drawn_arrow

    # Rysowanie obciążenia węzła:
    def draw_node_load(self, obj_id, selection = False, draw = False):
        # pobranie id węzła:
        n_id = self.get_meshOBJ_id(obj_id)
        # usuwanie starego dla braku selekcji:
        if not selection and obj_id in self.drawn_loadOBJ["node"]:
            self.canvas.remove_visualOBJ(self.drawn_loadOBJ["node"][obj_id])

        # pobranie koordynat węzła:
        x, z, no_coords_flag = self.canvas.get_node_coordinates(n_id, MessageBox = False, log = False)
        # pobranie wartości sił:
        X_force, flag_1 = self.validate_val(self.node_loads[obj_id]["X"], "force", flag = True)
        Z_force, flag_2 = self.validate_val(self.node_loads[obj_id]["Z"], "force", flag = True)
        R_moment, flag_3 = self.validate_val(self.node_loads[obj_id]["RY"], "moment_of_force", flag = True)



        # Rysowanie awaryjnego tekstu
        if False in {flag_1, flag_2, flag_3}:
            if selection:
                label = self.canvas.axes.text(x, z, f"nL_{n_id}: Corrupted load ({obj_id})",
                                                                color = "red",
                                                                ha = 'center',
                                                                va = 'center',
                                                                fontsize = 14,
                                                                alpha = 1,
                                                                bbox = dict(
                                                                        boxstyle = 'round,pad=0.15',
                                                                        fc = 'green',
                                                                        ec = 'none',
                                                                        alpha = 1))
                self.drawnSelection_OBJ = {"error": label}
            else:
                label = self.canvas.axes.text(x, z, f"nL_{n_id}: Corrupted load ({obj_id})",
                                                color = "red",
                                                ha = 'center',
                                                va = 'center',
                                                fontsize = 14,
                                                alpha = 1,
                                                bbox = dict(
                                                        boxstyle = 'round,pad=0.15',
                                                        fc = 'white',
                                                        ec = 'none',
                                                        alpha = 0.8))
                self.drawn_loadOBJ["node"][obj_id] = {"error": label}
            return

        # funkcja rysująca, musi wyznaczyć punkty dla strzałki
        def draw_load(vis_dict):
            # pobranie skali wielkości
            load_scale = 1 / vis_dict["load_scale"]
            x_1 = X_force * load_scale
            z_1 = Z_force * load_scale
            force_val = np.hypot(X_force, Z_force)
            lever = R_moment * load_scale
            lever_module = float(sp.Abs(lever))
            # punkty:
            p_1 = [x - x_1, z - z_1]
            p_2 = [x, z]
            # rysowanie strzałki:
            if force_val != 0.0:
                force_arrow = self.draw_arrow(point_1 = p_1, point_2 = p_2, visual_dict = vis_dict)
            else:
                force_arrow = None
            # rysowanie momentu:
            if R_moment != 0.0:
                # punkty dla strzałki:
                p_r1 = [lever/np.sqrt(2) + x, lever_module/np.sqrt(2) + z]
                p_r2 = [lever*(2/np.sqrt(2) - 1) + x, lever_module + z]
                # punkty dla ramienia:
                l_x = [x, x + lever/np.sqrt(2)]
                l_z = [z, z + lever_module/np.sqrt(2)]
                arm = self.canvas.axes.plot(l_x, l_z, linestyle = vis_dict["linestyle"], 
                                                        linewidth = vis_dict["linewidth"], 
                                                        color = vis_dict["color"], 
                                                        alpha = vis_dict["transparency"])
                momentum_arrow = self.draw_arrow(point_1 = p_r1, point_2 = p_r2, visual_dict = vis_dict)
            else:
                arm = momentum_arrow = None

            # rysowanie labelu:
            if selection:
                self.drawnSelection_OBJ = {"force_arrow": force_arrow, "momentum_arrow": momentum_arrow, "arm": arm}
                return
            else:
                if force_val != 0.0:
                    x_f = (p_1[0] + p_2[0]) / 2
                    z_f = (p_1[1] + p_2[1]) / 2
                elif R_moment != 0.0:
                    x_f = (l_x[0] + l_x[1]) / 2
                    z_f = (l_z[0] + l_z[1]) / 2
                else:
                    x_f = x
                    z_f = z
                label = self.canvas.axes.text(x_f, z_f, f"nL_{obj_id}",
                                               color = vis_dict["text_color"],
                                               ha = 'center',  # wyśrodkowanie w poziomie
                                               va = 'center',  # wyśrodkowanie w pionie
                                               fontsize = vis_dict["text_size"],
                                               alpha = vis_dict["text_transparency"],
                                               bbox = dict(
                                                       boxstyle = 'round,pad=0.15',
                                                       fc = 'white',
                                                       ec = 'none',
                                                       alpha = vis_dict["textBOX_transparency"]))
                self.drawn_loadOBJ["node"][obj_id] = {"force_arrow": force_arrow, "momentum_arrow": momentum_arrow, "arm": arm,  "label": label}
            return

        # bloki try/except:
        if obj_id in self.usersOBJ_visuals["node"]:
            vis_dict = self.usersOBJ_visuals["node"][obj_id]
        elif selection:
            vis_dict = self.get_selection_visual_dict()
        else:
            vis_dict = self.get_default_visual_dict()
        try:
            draw_load(vis_dict = vis_dict)
        except Exception as e:
            print(f"Error - drawing node load id {obj_id}:\n{e}")
            vis_dict = self.get_default_visual_dict()
            draw_load(vis_dict = vis_dict)
        if draw:
            self.canvas.draw()
        return

    # Rysowanie obciążenia elementu:
    def draw_element_load(self, obj_id, selection = False, draw = False, region = False, re_id = None):
        # pobranie id elementu:
        e_id = self.get_meshOBJ_id(obj_id)
        # usuwanie starego dla braku selekcji:
        if not selection and obj_id in self.drawn_loadOBJ["element"]:
            self.canvas.remove_visualOBJ(self.drawn_loadOBJ["element"][obj_id])

        # pobranie koordynat, długości i obrotu elementu:
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.canvas.get_element_vector(e_id, MessageBox = False, log = False, angle_only = False)
        # środek elementu:
        m_x = (x_1 + x_2) / 2
        m_z = (z_1 + z_2) / 2

        # pobranie wartości do rysowanie:
        Base_intensity, flag_1 = self.validate_val(self.element_loads[obj_id]["load_data"]["base_intensity"], "distributed_load", flag = True)
        flag_2 = True
        try:
            x_dimenless = self.element_loads[obj_id]["drawing_points"]["x"]
            z_dimenless = self.element_loads[obj_id]["drawing_points"]["z"]
            # konwersje na float (zabezpieczenie)
            x_dimenless = [float(x) for x in x_dimenless]
            z_dimenless = [float(z) for z in z_dimenless]
        except Exception:
            # Próba wyznaczenia punktów:
            
            if not self.el_draw_MessageBOX:
                QMessageBox.information(self.MainWindow,
                                        "Load Mesh Generation",
                                        "Some element load distributions do not have precomputed drawing points in the mesh file.\n\n"
                                        "Their distribution functions will now be reconstructed to generate the visualization. "
                                        "This process may take a moment.")
                self.el_draw_MessageBOX = True
            try:
                sym_dict = self.load_symbol_substitutes if self.MainWindow.data_type == "symbolic" else None
                Dist_class = FormulateDistribution(load_data = self.element_loads[obj_id]["load_data"], sym_dict = sym_dict, sympy_local = sympy_LOCAL)
                dist_func = Dist_class.SymPy_dimensionless(numerical = True)
                # pobranie symboli, zakładamy jeden xi_e
                xi_e = None
                for s in dist_func.free_symbols:
                    if s.name == "xi_e":
                        xi_e = s
                        break

                t_pts = np.linspace(0, 1, 20)
                x_dimenless = []
                z_dimenless = []
                for t in t_pts:
                    x_dimenless.append(t)
                    z_dimenless.append(float(dist_func.subs(xi_e, t) if xi_e is not None else dist_func))

                # zapisywanie nowych punktów
                self.element_loads[obj_id]["drawing_points"] = {}
                self.element_loads[obj_id]["drawing_points"]["x"] = x_dimenless
                self.element_loads[obj_id]["drawing_points"]["z"] = z_dimenless
            except Exception as e:
                print(e)
                flag_2 = False
            
        # Rysowanie awaryjnego tekstu
        if False in {flag_1, flag_2}:
            if selection:
                label = self.canvas.axes.text(m_x, m_z, f"eL_{e_id}: Corrupted load ({obj_id})",
                                                                color = "red",
                                                                ha = 'center',
                                                                va = 'center',
                                                                fontsize = 14,
                                                                alpha = 1,
                                                                bbox = dict(
                                                                        boxstyle = 'round,pad=0.15',
                                                                        fc = 'green',
                                                                        ec = 'none',
                                                                        alpha = 1))
                if region:
                    return {"error": label}
                self.drawnSelection_OBJ = {"error": label}
            else:
                label = self.canvas.axes.text(m_x, m_z, f"eL_{e_id}: Corrupted load ({obj_id})",
                                                color = "red",
                                                ha = 'center',
                                                va = 'center',
                                                fontsize = 14,
                                                alpha = 1,
                                                bbox = dict(
                                                        boxstyle = 'round,pad=0.15',
                                                        fc = 'white',
                                                        ec = 'none',
                                                        alpha = 0.8))
                if region:
                    return {"error": label}
                self.drawn_loadOBJ["element"][obj_id] = {"error": label}
            return

        # funkcja rysująca, musi wyznaczyć punkty dla strzałki
        def draw_load(vis_dict):
            # skalowanie osi:
            ax_scale = L # formalnie długość to 1, więc ax_scale = L / 1
            x_scaled = np.array([ax_scale * t for t in x_dimenless])
            # skalowanie wysokości:
            norm_scale = Base_intensity / vis_dict["load_scale"] / 3
            z_scaled = np.array([norm_scale * val for val in z_dimenless])
            # zagęszczenie kreskowania:
            n_pts = len(x_dimenless)
            if n_pts <= 15:
                hatch_d = 1
            elif n_pts <= 30:
                hatch_d = 2
            else:
                hatch_d = 3

            hatch_list = []
            # rysowanie kreskowania
            for i, x in enumerate(x_scaled, 1):
                if i in (1, n_pts) or i % hatch_d == 0:
                    h_x = np.array([x, x])
                    h_z = np.array([0, z_scaled[i - 1]])
                    h_x_f = h_x * np.cos(theta) - h_z * np.sin(theta) + x_1
                    h_z_f = h_x * np.sin(theta) + h_z * np.cos(theta) + z_1
                    hatch_arrow = self.draw_arrow(point_1 = [h_x_f[0], h_z_f[0]], point_2 = [h_x_f[1], h_z_f[1]],
                                                  visual_dict = vis_dict, type = "hatch")
                    hatch_list.append(hatch_arrow)

            # transformowanie:
            x_final = x_scaled * np.cos(theta) - z_scaled * np.sin(theta) + x_1
            z_final = x_scaled * np.sin(theta) + z_scaled * np.cos(theta) + z_1

            # rysowanie funkcji:
            func = self.canvas.axes.plot(x_final, z_final, linestyle = vis_dict["linestyle"], 
                                                    linewidth = vis_dict["linewidth"], 
                                                    color = vis_dict["color"], 
                                                    alpha = vis_dict["transparency"])
            
            if selection:
                if region:
                    return {"distribution": func, "hatch": hatch_list}
                self.drawnSelection_OBJ = {"distribution": func, "hatch": hatch_list}
                return
            else:
                # wstawianie tekstu
                # ustalenie pozycji:
                middle_pt = int(round(n_pts / 2, 0))
                m_z_func = z_final[middle_pt]
                m_x_func = x_final[middle_pt]
                x_txt = (m_x + m_x_func) / 2
                z_txt = (m_z + m_z_func) / 2
                label = self.canvas.axes.text(x_txt, z_txt, f"eL_{obj_id}",
                                                                color = vis_dict["text_color"],
                                                                ha = 'center',  # wyśrodkowanie w poziomie
                                                                va = 'center',  # wyśrodkowanie w pionie
                                                                rotation = np.rad2deg(theta),  # Kąt obrotu w stopniach
                                                                rotation_mode = "anchor",
                                                                fontsize = vis_dict["text_size"],
                                                                alpha = vis_dict["text_transparency"],
                                                                bbox = dict(
                                                                        boxstyle = 'round,pad=0.15',
                                                                        fc = 'white',
                                                                        ec = 'none',
                                                                        alpha = vis_dict["textBOX_transparency"]))
 
                if region:
                    return {"distribution": func, "hatch": hatch_list, "label": label}
                self.drawn_loadOBJ["element"][obj_id] = {"distribution": func, "hatch": hatch_list, "label": label}
                return

        # bloki try/except:
        if obj_id in self.usersOBJ_visuals["element"] and not region:
            vis_dict = self.usersOBJ_visuals["element"][obj_id]
        elif re_id in self.usersOBJ_visuals["region"] and region:
            vis_dict = self.usersOBJ_visuals["region"][re_id]
        elif selection:
            vis_dict = self.get_selection_visual_dict()
        else:
            vis_dict = self.get_default_visual_dict()
        try:
            if region:
                return draw_load(vis_dict = vis_dict)
            draw_load(vis_dict = vis_dict)
        except Exception as e:
            print(f"Error - drawing element load id {obj_id}:\n{e}")
            vis_dict = self.get_default_visual_dict()
            if region:
                return draw_load(vis_dict = vis_dict)
            draw_load(vis_dict = vis_dict)
        if draw:
            self.canvas.draw()
        return


    # ====================================






# ====================================================================================
# ==================================================================================== KLASY MANAGERA PROJEKTU

# ======================================== 
# Dialog okna tworzenia nowego projektu
# ======================================== MANAGER PROJEKTU
class NewProjectDialog(QDialog):
    def __init__(self, parent = None, directory = None):
        super().__init__(parent)

        self.MainWindow = parent
        self.setWindowTitle("New SciFEA project")
        self.setModal(True)
        self.directory = directory

        main_lt = QHBoxLayout(self)
        label = QLabel("Project name")
        self.line = QLineEdit("")
        btn = QPushButton("create project")
        main_lt.addWidget(label)
        main_lt.addWidget(self.line)
        main_lt.addWidget(btn)

        btn.clicked.connect(self.create_directories)
        
    # funkcja tworząca foldery:
    def create_directories(self):
        def highlignt_widget(widget, flag = True):
            if not flag:
                widget.setStyleSheet("background-color: red; color: white")
            else:
                widget.setStyleSheet("")

        prj_name = self.line.text()
        full_directory = os.path.join(self.directory, f"{prj_name}_SciFEAprj")
        # sprawdzenie czy nazwa nie jest pusta:
        if prj_name.strip() == "":
            QMessageBox.warning(self, "Invalid project name", "Project name was not provided")
            highlignt_widget(self.line, False)
            return
        try:
            os.makedirs(full_directory)
            loads_dir = os.path.join(full_directory, "Loads")
            results_dir = os.path.join(full_directory, "Results")
            os.makedirs(loads_dir)
            os.makedirs(results_dir)
        except Exception as e:
            QMessageBox.critical(self, "An error occured while creating directories", f"Error log:\n{e}")
            highlignt_widget(self.line, False)
            return
        
        highlignt_widget(self.line, True)
        self.MainWindow.PRJ_loader(get_dir = False, directory = full_directory)
        self.accept()
        return
        

# ======================================== 
# Dialog okna doboru siatki
# ======================================== MANAGER PROJEKTU
class MeshManagerDialog(QDialog):
    def __init__(self, parent = None, no_mesh = False):
        super().__init__(parent)

        self.MainWindow = parent
        self.setWindowTitle("Mesh manager")
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        if not no_mesh:
            edit_lt = QHBoxLayout()
            edit_lt.addWidget(QLabel("Modify assigned mesh:"))
            edit_mesh_btn = QPushButton("modify")
            edit_mesh_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            edit_lt.addWidget(edit_mesh_btn)
            main_layout.addLayout(edit_lt)
            edit_mesh_btn.clicked.connect(self.edit_mesh)

        label_txt = "Select mesh assignment procedure:" if no_mesh else "Replace existing mesh with:"
        main_layout.addWidget(QLabel(f"{label_txt}"))
        new_mesh_btn = QPushButton("New mesh file")
        new_mesh_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        select_mesh_btn = QPushButton("Existing mesh file")
        select_mesh_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        main_layout.addWidget(new_mesh_btn)
        main_layout.addWidget(select_mesh_btn)

        new_mesh_btn.clicked.connect(self.open_new_mesh_dialog)
        select_mesh_btn.clicked.connect(self.select_existing_mesh)

    # funkcja przenosząca nadmiar siatek:
    def move_old_mesh(self):
        mesh_dump = os.path.join(self.MainWindow.prj_directories["main"], "mesh_dump")
        if not os.path.exists(mesh_dump):
            os.makedirs(mesh_dump)
        for name in os.listdir(self.MainWindow.prj_directories["main"]):
            if name.endswith("_msh.json"):
                os.replace(os.path.join(self.MainWindow.prj_directories["main"], name), os.path.join(mesh_dump, name))
    
    # nowa siatka:
    def open_new_mesh_dialog(self):
        self.move_old_mesh()           
        self.MainWindow.new_mesh_route(file_path = self.MainWindow.prj_directories["main"], prj_manager = True)
        self.accept()

    def select_existing_mesh(self):
        self.move_old_mesh()
        self.MainWindow.assign_selected_mesh_to_prj()
        self.MainWindow.compose_prj_manager()
        self.accept()

    def edit_mesh(self):
        self.MainWindow.full_mesh_path
        if not self.MainWindow.full_mesh_path:
            QMessageBox.critical(self, "Error", "Couldnt locate mesh file")
            return
        self.accept() 
        self.MainWindow.edit_mesh_route(file_path = self.MainWindow.full_mesh_path, prj_manager = True)
        


# ====================================================================================
# ==================================================================================== KLASY EDYTORA SIATKI

# ======================================== 
# Dialog okna walidacji siatki
# ======================================== EDYTOR SIATKI
class ValidationDialog(QDialog):
    def __init__(self, parent = None, canvas = None):
        super().__init__(parent)

        self.MainWindow = parent
        self.canvas = canvas
        self.setWindowTitle("Validation setup")
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel("Choose reporting type: "))
        # checkboxy:
        self.check_full = QCheckBox("Full report")
        self.check_error = QCheckBox("Report errors only")
        main_layout.addWidget(self.check_full)
        main_layout.addWidget(self.check_error)
        self.check_group = QButtonGroup(self)
        self.check_group.addButton(self.check_full)
        self.check_group.addButton(self.check_error)
        self.check_group.setExclusive(True)
        self.check_full.setChecked(True)
        main_layout.addStretch()
        apply_btn = QPushButton("start mesh validation")
        main_layout.addWidget(apply_btn)
        apply_btn.clicked.connect(self.start_validation)

    def start_validation(self):
        if self.check_full.isChecked():
            full_raport = True
        elif self.check_error.isChecked():
            full_raport = False
        self.canvas.MASTER_validate(full_validation = full_raport)
        self.accept()


# ======================================== 
# Dialog okna tworzenia nowej siatki
# ======================================== EDYTOR SIATKI + MANAGER
class NewMeshFile(QDialog):
    def __init__(self, parent = None, directory = None):
        super().__init__(parent)

        self.setWindowTitle("New mesh file")
        self.setModal(True)
        self.file_directory = directory
        self.MainWindow = parent

        # Listy opcji:
        self.mesh_options = {
            'mesh_type': ["Generalized_Coordinate_Framing", "Parallel_Beam_Approach"],
            'data_type': ["numerical", "symbolic"]
        }

        # słownik do zwrotu:
        self.new_mesh = {}
        
        # Layouty:
        main_v_lt = QVBoxLayout(self)
        self.main_layout = QVBoxLayout()
        main_v_lt.addLayout(self.main_layout)

        # Sekcja podawania danych:
        self.mesh_name_line = self.create_h_lt(self.main_layout, "Mesh name: ", type = "line")
        self.mesh_type_box = self.create_h_lt(self.main_layout, "Mesh topology: ", type = "combo", list = self.mesh_options["mesh_type"])
        self.data_type_box = self.create_h_lt(self.main_layout, "Data type: ", type = "combo", list = self.mesh_options["data_type"])

        # Sekcja dolna:
        bottom_lt = QHBoxLayout()
        main_v_lt.addLayout(bottom_lt)
        create_mesh_btn = QPushButton("Create new mesh file")
        bottom_lt.addWidget(create_mesh_btn)
        create_mesh_btn.clicked.connect(self.accept_dialog)

    def create_h_lt(self, parent_lt = None, label_txt = "", type = "line", list = []):
        local_lt = QHBoxLayout()
        parent_lt.addLayout(local_lt)
        local_lt.addWidget(QLabel(f"{label_txt}"))
        if type == "line":
            widget = QLineEdit("")
        elif type == "combo":
            widget = QComboBox()
            widget.addItems(list)
        local_lt.addWidget(widget)
        local_lt.addStretch()
        return widget

    def save_mesh(self):
        if self.mesh_name_line.text().strip() == "":
            QMessageBox.warning(self, "Invalid mesh name", "Mesh name was not provided")
            return False
        mesh_name = self.mesh_name_line.text()
        mesh_type = self.mesh_type_box.currentText()
        data_type = self.data_type_box.currentText()
        mesh_name = f"{mesh_name}_msh.json"
        full_path = os.path.join(self.file_directory, mesh_name)
        # Przygotowanie słownika pod JSON:
        summary = {"model_summary" : {
            "mesh_name": mesh_name,
            "data_type": data_type,
            "mesh_type": mesh_type,
        },
        "nodes": [],
        "elements": []}
        self.MainWindow.mesh_summary = summary["model_summary"]
        # zapisywanie pliku:
        try:
            with open(full_path, "x", encoding = "utf-8") as mesh:
                json.dump(summary, mesh, indent = 4)
            self.MainWindow.mesh_name = mesh_name
            self.MainWindow.mesh_element_layout_type = mesh_type
            self.MainWindow.data_type = data_type 
            self.MainWindow.full_mesh_path = full_path 
            return True
        except Exception as e:
            QMessageBox.critical(self, "Mesh file writing error",
                                 "error log:\n"
                                 f"{e}")
            return False

    def accept_dialog(self):
        if self.save_mesh():
            self.accept()
        else:
            return


# ========================================
# Dialog zapisania siatki
# ======================================== EDYTOR SIATKI
class SaveAsDialog(QDialog):
    def __init__(self, parent = None, canvas = None, load_mesh = False, LoadsCore = None):
        super().__init__(parent)

        self.setModal(True)
        self.MainWindow = parent
        self.canvas = canvas
        self.LoadsCore = LoadsCore
        self.load_flag = load_mesh
        if self.load_flag:
            self.setWindowTitle("Save load mesh file")
        else:
            self.setWindowTitle("Save mesh file")
        
        # Layouty:
        main_v_lt = QVBoxLayout(self)
        self.main_layout = QVBoxLayout()
        main_v_lt.addLayout(self.main_layout)

        # Sekcja podawania danych:
        save_h_lt = QHBoxLayout()
        self.main_layout.addLayout(save_h_lt)
        save_h_lt.addWidget(QLabel("Save as:"))
        self.overwrite_box = QCheckBox("overwrite")
        self.save_as_copy_box = QCheckBox("copy")
        save_h_lt.addWidget(self.overwrite_box)
        save_h_lt.addWidget(self.save_as_copy_box)
        check_group = QButtonGroup(self)
        check_group.addButton(self.overwrite_box)
        check_group.addButton(self.save_as_copy_box)
        check_group.setExclusive(True)
        self.overwrite_box.setChecked(True)

        self.convert_box = QCheckBox("")
        self.convert_box.setChecked(False)
        if self.MainWindow.data_type == "symbolic":
            convert_h_lt = QHBoxLayout()
            self.main_layout.addLayout(convert_h_lt)
            if self.load_flag:
                text = "Convert symbolic load mesh to numerical:"
            else:
                text = "Convert symbolic mesh to numerical:"
            convert_h_lt.addWidget(QLabel(f"{text}"))
            convert_h_lt.addWidget(self.convert_box)

        visuals_lt = QHBoxLayout()
        self.main_layout.addLayout(visuals_lt)
        visuals_lt.addWidget(QLabel("Save visual preferences:"))
        self.visuals_box = QCheckBox("save visuals")
        self.visuals_box.setChecked(False)
        visuals_lt.addWidget(self.visuals_box)

        # Sekcja dolna:
        bottom_lt = QHBoxLayout()
        main_v_lt.addLayout(bottom_lt)
        save_mesh_btn= QPushButton("Save")
        bottom_lt.addWidget(save_mesh_btn)
        save_mesh_btn.clicked.connect(self.save_mesh)

    def save_mesh(self):
        if self.overwrite_box.isChecked():
            copy = False
        else:
            copy = True
        if self.convert_box.isChecked():
            float_converter = True
        else:
            float_converter = False
        if self.visuals_box.isChecked():
            visuals = True
        else:
            visuals = False
        try:
            if self.load_flag:
                self.LoadsCore.save_load_mesh(copy, float_converter, visuals)
            else:
                self.canvas.save_mesh_file(copy, float_converter, visuals)
        except Exception as e:
            if self.load_flag:
                name = "Load mesh"
            else:
                name = "Mesh"
            QMessageBox.warning(self, f"{name} file not saved!",
                                f"An error occured while writing {name.lower()} file:\n"
                                f"{e}")
            return
        self.accept()


# ========================================
# Dialog okna wedycji parametrów canvas
# ======================================== EDYTOR SIATKI
class CanvasOptionsDialog(QDialog):
    def __init__(self, parent = None, canvas = None, load_mesh = False, LoadsCore = None):
        super().__init__(parent)
        self.canvas = canvas # referencja do płótna
        self.load_mesh_flag = load_mesh
        self.MainWindow = parent
        self.LoadsCore = LoadsCore
        if self.load_mesh_flag:
            self.linewidth_prefix = "(Classic mesh theme) "
        else:
            self.linewidth_prefix = ""

        self.setWindowTitle("Canvas options")
        self.setModal(True)
        # Pomocniczy słownik, służy sprawdzeniu czy na pewno są te same funkcje co w słowniku canvas
        self.canvas_option_dict = {
                    'set_aspect': ['equal', 'auto'],
                    'margins' : 0.2,
                    'grid(True/False)' : True,
                    'grid_linestyle': {'dashed': '--', 'solid' : '-', 'dash-dot' : '-.', 'dotted' : ':'},
                    'grid_alpha' : 0.5,
                    'thinn_line' : 0.75,
                    'thicc_line' : 1.5
                }
        # Pomocnicza flaga dla przycisku włączającego kratkowanie, trochę nieładnie tak robić ale zrobiono tak by jedna funkcja (save_settings) 
        # służyła do zebrania wszystkich danych
        self.flag = self.canvas.canvas_settings_dict.get("grid(True/False)", True)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        if self.load_mesh_flag:
            Mesh_label = QLabel("General Mesh / Canvas settings")
            Mesh_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_font = Mesh_label.font()
            label_font.setPointSize(12)
            Mesh_label.setFont(label_font)
            self.main_layout.addWidget(Mesh_label)
        # Podlayout opcji gdzie uzupełnia się informacje:
        self.Form_layout  = QFormLayout()
        self.main_layout.addLayout(self.Form_layout)
        self.set_aspect_widget()
        self.grid_btn = QPushButton()
        self.Form_layout.addRow(QLabel("Grid"), self.grid_btn)
        self.set_grid_btn()
        self.grid_btn.clicked.connect(self.grid_btn_click)
        self.set_grid_linestyle_widget()
        self.Form_layout_2 = QFormLayout()
        self.main_layout.addLayout(self.Form_layout_2)
        self.set_LineEdit_widgets()
        if self.load_mesh_flag:
            self.loads_canvas_GUI()

        # Bottom layout
        H_layout = QHBoxLayout()
        self.main_layout.addLayout(H_layout)
        apply_btn = QPushButton("Apply changes")
        close_save_btn = QPushButton("Save an exit")
        refresh_canvas_btn = QPushButton("Refresh canvas")
        H_layout.addWidget(apply_btn)
        H_layout.addWidget(refresh_canvas_btn)
        H_layout.addWidget(close_save_btn)
        apply_btn.clicked.connect(self.apply_changes)
        refresh_canvas_btn.clicked.connect(self.refresh_canvas)
        close_save_btn.clicked.connect(self.close_save_dialog)

    # Funkcje wyświetlające widgety
    def set_aspect_widget(self):
        label = QLabel("Axes aspect ratio:")
        prop_list = self.canvas_option_dict['set_aspect']
        self.aspect_comboBox = QComboBox()
        self.aspect_comboBox.addItems(prop_list)
        self.Form_layout.addRow(label, self.aspect_comboBox)

    # Funkcja ustawiająca kolor i tekst przcisku podziałki
    def set_grid_btn(self):
        if self.flag == True:
            self.grid_btn.setText("ON")
            self.grid_btn.setStyleSheet("background-color: green; color: white;")
        else: 
            self.grid_btn.setText("OFF")
            self.grid_btn.setStyleSheet("background-color: red; color: white;")

    # Kliknięcie przycisku podziałki
    def grid_btn_click(self):
        if self.flag:
            self.flag = False
        else:
            self.flag = True
        self.set_grid_btn()
        
    # Tworzenie widgetu listy typów linii podziałki
    def set_grid_linestyle_widget(self):
        # Tworzenie listy dla combobox:
        label = QLabel("Grid linestyle:")
        self.linestyle_comboBox = QComboBox()
        combo_list = []
        self.combo_dict  = self.canvas_option_dict['grid_linestyle'].copy()
        for line_type in self.combo_dict.keys():
            combo_list.append(line_type)
        self.linestyle_comboBox.addItems(combo_list)
        self.Form_layout.addRow(label, self.linestyle_comboBox)
        
    # Tworzenie widgetów opartych o wpisywanie ręczne i formularz    
    def set_LineEdit_widgets(self):
        # Czyszczenie formularza:
        while self.Form_layout_2.count():
            item = self.Form_layout_2.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()
        self.margin_F = {'label' : QLabel("Canvas margins:"), 'val' : QLineEdit(str(self.canvas.canvas_settings_dict.get("margins", 0.2)))}
        self.alpha_F = {'label' : QLabel("Grid transparency:"), 'val' : QLineEdit(str(self.canvas.canvas_settings_dict.get("grid_alpha", 0.5)))}
        self.thinn_F = {'label' : QLabel(f"{self.linewidth_prefix}Thinn line thickness:"), 'val' : QLineEdit(str(self.canvas.canvas_settings_dict.get("thinn_line", 0.75)))}
        self.thicc_F = {'label' : QLabel(f"{self.linewidth_prefix}Thick line thickness:"), 'val' : QLineEdit(str(self.canvas.canvas_settings_dict.get("thicc_line", 1.5)))}
        self.selection_marker_size = {'label' : QLabel("Selection marker size:"), 'val' : QLineEdit(str(self.canvas.selection_size))}
        self.Form_layout_2.addRow(self.margin_F['label'], self.margin_F['val'])
        self.Form_layout_2.addRow(self.alpha_F['label'], self.alpha_F['val'])
        self.Form_layout_2.addRow(self.thinn_F['label'], self.thinn_F['val'])
        self.Form_layout_2.addRow(self.thicc_F['label'], self.thicc_F['val'])
        self.Form_layout_2.addRow(self.selection_marker_size['label'], self.selection_marker_size['val'])

    # Zapisywanie zmian:
    def apply_changes(self):
        # Przypisywanie nowych wartości, nie ma co patrzeć na sprawdzanie danych - robi to update canvas
        self.canvas.canvas_settings_dict['set_aspect'] = self.aspect_comboBox.currentText()
        self.canvas.canvas_settings_dict['grid(True/False)'] = self.flag
        self.canvas.canvas_settings_dict['grid_linestyle'] = self.combo_dict[self.linestyle_comboBox.currentText()]
        self.canvas.canvas_settings_dict['margins'] = self.margin_F['val'].text().strip()
        self.canvas.canvas_settings_dict['grid_alpha'] = self.alpha_F['val'].text().strip()
        self.canvas.canvas_settings_dict['thinn_line'] = self.thinn_F['val'].text().strip()
        self.canvas.canvas_settings_dict['thicc_line'] = self.thicc_F['val'].text().strip()
        try:
            self.canvas.selection_size = float(self.selection_marker_size["val"].text().strip())
            self.selection_marker_size["val"].setStyleSheet("")
        except Exception:
            QMessageBox.warning(self, "Invalid value", "Selection marker size must ba a float value")
            self.canvas.selection_size = 16.0
            self.selection_marker_size["val"].setStyleSheet("background-color: red; color: white")

        # Updateowanie płutna
        self.canvas.canvas_settings()
        self.canvas.draw()

        # W razie błędu przywraca się ustawienia formularza lineedit:
        self.set_LineEdit_widgets()

        # zapisanie ustawień siatki obciążeń (walidacja wewnątrz funkcji)
        self.save_loads_dicts()

    # narzędzie do robienia combobox_lt:
    def make_combobox_lt(self, parent_lt = None, label_txt = "", list = [], current_item = None):
        box_lt = QHBoxLayout()
        parent_lt.addLayout(box_lt)
        box_lt.addWidget(QLabel(f"{label_txt}"))
        new_box = QComboBox()
        new_box.addItems(list)
        if current_item:
            try:
                new_box.setCurrentText(current_item)
                if current_item not in list:
                    current_item = int(float(current_item))
                    new_box.setCurrentText(str(current_item))
            except Exception as e:
                print(e)
                pass
        box_lt.addWidget(new_box)
        box_lt.addStretch()
        return new_box

    # dodatkowe funkcje na potrzeby edytora obciążeń:
    def loads_canvas_GUI(self):
        main_layout = QHBoxLayout()
        left_lt = QVBoxLayout()
        right_lt = QVBoxLayout()
        main_layout.addLayout(left_lt)
        main_layout.addLayout(right_lt)


        Load_label = QLabel("Load mesh default visuals")
        Load_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        Load_font = Load_label.font()
        Load_font.setPointSize(12)
        Load_label.setFont(Load_font)
        left_lt.addWidget(Load_label)
        local_scale_lt = QHBoxLayout()
        left_lt.addLayout(local_scale_lt)
        local_scale_lt.addWidget(QLabel("Loads scaling: "))
        self.Load_scale = QLineEdit(f"{self.canvas.load_mesh_visual_settings["load_scale"]}")
        local_scale_lt.addWidget(self.Load_scale)
        local_scale_lt.addStretch()

        self.Load_color = self.make_combobox_lt(left_lt, "Load mesh - color: ", 
                                                    ["black", "blue", "green", "red", "gray", "pink"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["loads_color"]))
        self.Load_transparency = self.make_combobox_lt(left_lt, "Load mesh - transparency: ", 
                                                    ["0", "0.1", "0.25", "0.5", "0.75", "1.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["loads_transparency"]))
        self.Load_thicc = self.make_combobox_lt(left_lt, "Load mesh - thick line thickness: ", 
                                                    ["0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2", "3", "4", "5"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["thicc_line"]))
        self.Load_thinn = self.make_combobox_lt(left_lt, "Load mesh - thinn line thickness: ", 
                                                    ["0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["thinn_line"]))
        self.Load_linestyle = self.make_combobox_lt(left_lt, "Load mesh - linestyle: ", 
                                                    ['-', '--', '-.', ':'],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["loads_linestyle"]))
        self.Load_text_size = self.make_combobox_lt(left_lt, "Load mesh - font size: ", 
                                                    ["0", "2", "6", "8", "10", "12", "14", "16", "18", "20"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["text_size"]))
        self.Load_text_color = self.make_combobox_lt(left_lt, "Load mesh - text color: ", 
                                                    ["black", "blue", "green", "red", "gray", "pink"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["text_color"]))
        self.Load_text_transparency = self.make_combobox_lt(left_lt, "Load mesh - text transparency: ", 
                                                    ["0", "0.1", "0.25", "0.5", "0.75", "1.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["text_transparency"]))
        self.Load_textBOX_transparency = self.make_combobox_lt(left_lt, "Load mesh - textBOX_transparency: ", 
                                                    ["0", "0.1", "0.25", "0.5", "0.6", "0.75", "1.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["textBOX_transparency"]))
        self.Load_selection_thickness = self.make_combobox_lt(left_lt, "Load mesh - selection thickness: ", 
                                                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "12", "14", "16"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["selection_thickness"]))
        self.Load_selection_color = self.make_combobox_lt(left_lt, "Load mesh - selection color: ", 
                                                    ["black", "blue", "green", "red", "gray", "pink"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["selection_color"]))
        self.Load_selection_transparency = self.make_combobox_lt(left_lt, "Load mesh - selection transparency: ", 
                                                    ["0", "0.1", "0.25", "0.5", "0.75", "1.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["selection_transparency"]))
        self.Load_region_transparency = self.make_combobox_lt(left_lt, "Load mesh - Region load transparency: ", 
                                                    ["0", "0.1", "0.25", "0.5", "0.75", "1.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["region_transparency"]))
        left_lt.addStretch()
        
        simple_label = QLabel("Simplified mesh theme settings")
        simple_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        simple_font = simple_label.font()
        simple_font.setPointSize(12)
        simple_label.setFont(simple_font)
        right_lt.addWidget(simple_label)
        self.simple_linestyle = self.make_combobox_lt(right_lt, "Linestyle", 
                                                    ['--', '-', '-.', ':'],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["simplified_element_linestyle"]))
        self.simple_linewidth = self.make_combobox_lt(right_lt, "Line thickness", 
                                                    ["0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2", "3", "4", "5"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["simplified_element_linewidth"]))
        self.simple_color = self.make_combobox_lt(right_lt, "Mesh color", 
                                                    ["black", "blue", "green", "red", "gray", "pink"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["simplified_mesh_color"]))
        self.simple_transparency = self.make_combobox_lt(right_lt, "Mesh transparency", 
                                                    ["0", "0.25", "0.5", "0.75", "1.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["simplified_mesh_transparency"]))
        self.simple_node_size = self.make_combobox_lt(right_lt, "Node-mark size", 
                                                    ["0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "4.0", "5.0", "6.0", "7.0", "8.5", "10.0", "12.0", "14.0", "16.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["simplified_node_size"]))
        self.simple_label_size = self.make_combobox_lt(right_lt, "Label text size", 
                                                    ["0", "1.0", "1.5", "2.0", "2.5", "3.0", "4.0", "5.0", "6.0", "7.0", "8.5", "10.0"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["simplified_label_size"]))                              
        self.simple_draw_label = self.make_combobox_lt(right_lt, "Node/Element labels: ", 
                                                    ["Show", "Hide"],
                                                    current_item = str(self.canvas.load_mesh_visual_settings["draw_labels"]))
        right_lt.addStretch()

        self.main_layout.addLayout(main_layout)
        return

    def save_loads_dicts(self):
        if self.load_mesh_flag:
            try:
                scale = float(self.Load_scale.text())
                if not scale > 0:
                    QMessageBox.warning(self, "Invalid value", "Loads scale must be a positive float number.")
                else:
                    self.canvas.load_mesh_visual_settings["load_scale"] = scale
            except Exception:
                QMessageBox.warning(self, "Invalid value", "Loads scale must be a positive float number.")
            self.canvas.load_mesh_visual_settings["loads_color"] = self.Load_color.currentText()
            self.canvas.load_mesh_visual_settings["loads_transparency"] = float(self.Load_transparency.currentText())
            self.canvas.load_mesh_visual_settings["thicc_line"] = float(self.Load_thicc.currentText())
            self.canvas.load_mesh_visual_settings["thinn_line"] = float(self.Load_thinn.currentText())
            self.canvas.load_mesh_visual_settings["loads_linestyle"] = self.Load_linestyle.currentText()
            self.canvas.load_mesh_visual_settings["text_size"] = float(self.Load_text_size.currentText())
            self.canvas.load_mesh_visual_settings["text_color"] = self.Load_text_color.currentText()
            self.canvas.load_mesh_visual_settings["text_transparency"] = float(self.Load_text_transparency.currentText())
            self.canvas.load_mesh_visual_settings["textBOX_transparency"] = float(self.Load_textBOX_transparency.currentText())
            self.canvas.load_mesh_visual_settings["selection_thickness"] = float(self.Load_selection_thickness.currentText())
            self.canvas.load_mesh_visual_settings["selection_color"] = self.Load_selection_color.currentText()
            self.canvas.load_mesh_visual_settings["selection_transparency"] = float(self.Load_selection_transparency.currentText())
            self.canvas.load_mesh_visual_settings["region_transparency"] = float(self.Load_region_transparency.currentText())

            self.canvas.load_mesh_visual_settings["simplified_element_linestyle"] = self.simple_linestyle.currentText()
            self.canvas.load_mesh_visual_settings["simplified_element_linewidth"] = float(self.simple_linewidth.currentText())
            self.canvas.load_mesh_visual_settings["simplified_mesh_color"] = self.simple_color.currentText()
            self.canvas.load_mesh_visual_settings["simplified_mesh_transparency"] = float(self.simple_transparency.currentText())
            self.canvas.load_mesh_visual_settings["simplified_node_size"] = float(self.simple_node_size.currentText())
            self.canvas.load_mesh_visual_settings["simplified_label_size"] = float(self.simple_label_size.currentText())
            self.canvas.load_mesh_visual_settings["draw_labels"] = self.simple_draw_label.currentText()
            self.LoadsCore.draw_load_mesh()
            if self.canvas.simple_mesh_flag:
                self.canvas.clear_mesh()
                self.canvas.draw_simple_mesh()
                self.LoadsCore.draw_load_mesh()
            return
        else:
            return

    def refresh_canvas(self):
        self.canvas.clear_mesh()
        self.apply_changes()
        if self.load_mesh_flag:
            self.MainWindow.mesh_display_theme_btn.setText("Mesh theme - classic")
            self.LoadsCore.draw_load_mesh()
        self.canvas.draw_mesh()

    def close_save_dialog(self):
            self.apply_changes()
            self.accept()


# ========================================
# Dialog okna edycji obiektó wizualnych
# ======================================== EDYTOR SIATKI
class VisualObjEditDialog(QDialog): 
    # Dodajemy argument 'canvas', aby dialog miał dostęp do danych siatki
    def __init__(self, parent=None, canvas=None):
        super().__init__(parent)
        self.canvas = canvas # Zapisujemy referencję do płótna
        
        self.setWindowTitle("Visual object editor")
        self.setModal(False)

        # Ścieżki grafik
        self.element_image_name = {"2N4DOF_EB": "Beam",
                                   "2N6DOF_EB_Q": "Beam",
                                   "2N4DOF_T_EX": "Beam",
                                   "2N4DOF_T_FI": "Beam",
                                   "2N4DOF_T_RI": "Beam",
                                   "2N4DOF_T_EX": "Beam",
                                   "2N2DOF_Bar": "2N2DOF_Bar",
                                   "2N4DOF_Truss": "2N4DOF_Truss",
                                   "Spring": "Spring",
                                   "Spring_2D": "Spring_2D",
                                   "2N6DOF_EB": "Frame",
                                   "2N8DOF_EB_Q": "Frame",
                                   "2N6DOF_T_EX": "Frame",
                                   "2N6DOF_T_FI": "Frame",
                                   "2N6DOF_T_RI": "Frame",
                                   "2N6DOF_T_EX": "Frame",
        }
        skrypt_dir = os.path.dirname(__file__)
        self.image_folder = os.path.join(skrypt_dir, r"assets/images")
        default_image_path = os.path.join(self.image_folder, "xd.png")

        # GŁÓWNY LAYOUT (zapisany jako self, aby inne funkcje miały do niego dostęp)
        self.main_h_layout = QHBoxLayout(self)
        self.main_layout = QVBoxLayout()
        self.main_h_layout.addLayout(self.main_layout, stretch = 3)
        # Obrazek podpory
        self.image_box = QLabel(self)
        self.default_image = QPixmap(default_image_path)
        self.image_box.setPixmap(self.default_image)
        # Mówimy layoutowi, że QLabel ma ignorować oryginalny rozmiar 
        # obrazka i ma bezwzględnie słuchać podziału stretch (Ignored na szerokość, Ignored na wysokość)
        self.image_box.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # Ta linijka sprawia, że obrazek dostosuje się do rozmiaru QLabel:
        self.image_box.setScaledContents(True)
        self.image_box.setFixedSize(300, 300)
        self.main_h_layout.addWidget(self.image_box, stretch = 1)

        # Wyszukiwanie węzła
        H_layout_1 = QHBoxLayout()
        self.obj_id_line = QLineEdit()
        self.obj_id_line.setEnabled(True)
        set_node_btn = QPushButton("Load node visual parameters")
        set_node_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        set_node_btn.clicked.connect(lambda: self.load_obj_params(obj_type = "node"))
        set_element_btn = QPushButton("Load element visual parameters")
        set_element_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        set_element_btn.clicked.connect(lambda: self.load_obj_params(obj_type = "element"))
        # zapobieganie przed możliwością edycji złego węzła (zmiana tekstu powoduje brak dostępu do formularza do momentu kliknięcia load parameters)
        self.obj_id_line.textChanged.connect(self.clear_param_forms)
        
        H_layout_1.addWidget(QLabel("Provide object id:"))
        H_layout_1.addWidget(self.obj_id_line)
        H_layout_1.addWidget(set_node_btn)
        H_layout_1.addWidget(set_element_btn)
        self.main_layout.addLayout(H_layout_1)
        
        # Dynamiczne pola
        # Label formularza edycji obiektu
        self.OBJ_form_label = QLabel("No object selected")
        self.OBJ_form_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.OBJ_form_label)
        self.obj_params_layout = QFormLayout()
        # Label formularza edycji labelu
        self.label_params_label = QLabel("")
        self.label_params_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_params_layout = QFormLayout()
        self.main_layout.addLayout(self.obj_params_layout)
        self.main_layout.addWidget(self.label_params_label)
        self.main_layout.addLayout(self.label_params_layout)
        
        # Zapisywanie zmian / wyjście z okna
        exit_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.apply_btn.clicked.connect(self.save_and_accept)
        self.apply_btn.setEnabled(False) # Wyłączony, dopóki nie załadujemy węzła
        self.restore_to_default = QPushButton("Restore to default")
        self.restore_to_default.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.restore_to_default.setEnabled(False)
        self.restore_to_default.clicked.connect(self.set_to_default)
        self.close_btn = QPushButton("Save & close")
        self.close_btn.setEnabled(False)
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_btn.clicked.connect(self.close_dialog)
        self.reset_all_btn = QPushButton("Reset visuals for all objects")
        self.reset_all_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.reset_all_btn.clicked.connect(self.reset_visuals)
        exit_layout.addWidget(self.apply_btn)
        exit_layout.addWidget(self.restore_to_default)
        exit_layout.addWidget(self.reset_all_btn)
        exit_layout.addWidget(self.close_btn)
        self.main_layout.addLayout(exit_layout)
        
        

        # Zmienne do przechowywania danych
        self.loaded_id = None
        self.obj_line_edits = {} # Tutaj zapiszemy odwołania do wygenerowanych okienek tekstowych
        self.label_line_edits = {}

    # Funkcja reserująca słowniki wizualne:
    def reset_visuals(self):
        message = QMessageBox.warning(self, "Do you want to proceed?",
                                      "Reseting visual values will delete all custom visual preferences",
                                      QMessageBox.Ok | QMessageBox.Cancel)
        if message == QMessageBox.Ok:
            for n_dict in self.canvas.nodeOBJ_visuals.values():
                n_dict["visual_parameters"] = self.canvas.support_type[n_dict['support_type']]["v_params"]
            for e_dict in self.canvas.elementOBJ_visuals.values():
                e_dict["visual_parameters"] = self.canvas.element_type[e_dict['element_type']]["v_params"]
            self.canvas.draw_mesh(Raport_dialog = False)
        else:
            return
    
    # Funkcja ładująca parametry do okna
    def clear_param_forms(self):
        def clear_form(form):  
            while form.count():
                item = form.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        clear_form(self.obj_params_layout)
        clear_form(self.label_params_layout)
        self.label_params_label.setText("")
        self.obj_line_edits.clear()
        self.label_line_edits.clear()
        # Zablokowanie zapisu i przywrócenie startowego obrazka jeśli przyciski (apply changes) i (close) są załadowane
        if hasattr(self, 'apply_btn'):
            self.apply_btn.setEnabled(False)
            self.close_btn.setEnabled(False)
            self.restore_to_default.setEnabled(False)
            self.OBJ_form_label.setText("No object selected")
            self.image_box.setPixmap(self.default_image)

    # Funkcja tworząca słowniki bazowe na podstawie których tworzone są ogólnikowe słowniki na bazie których działa dialog
    # Dodatkowo odpowiada za dobranie odpowiednich labeli oraz odpowiedniego obrazu
    def get_OBJ_dicts(self, obj_type):           
        if obj_type == "element":
            OBJ_dict = self.canvas.elementOBJ_visuals
            self.drawn_OBJ_dict = self.canvas.drawn_elementOBJ
        elif obj_type == "node":
            OBJ_dict = self.canvas.nodeOBJ_visuals
            self.drawn_OBJ_dict = self.canvas.drawn_nodeOBJ
        else:
            QMessageBox.critical(self,
                                 "Program architecture failure",
                                 "Nie wiem jak to się odjebało")
            return False
        try:
            obj_id = int(self.obj_id_line.text())
            if obj_id in self.drawn_OBJ_dict:
                self.loaded_obj_id = obj_id
                self.OBJ_dict = OBJ_dict[obj_id]
                if obj_type == "element":
                    element_type = self.canvas.elementOBJ_visuals[obj_id]['element_type']
                    try:
                        node_1 = int(self.canvas.elements[obj_id]['node_1_id'])
                    except ValueError:
                        node_1 = "???"
                    try:
                        node_2 = int(self.canvas.elements[obj_id]['node_2_id'])
                    except ValueError:
                        node_2 = "???"
                    default_params = self.canvas.element_type[element_type]["v_params"]
                    self.default_params = default_params.copy()
                    self.default_label_params = self.canvas.default_element_label_params.copy()
                    # Pobranie odpowiadającej funkcji rysującej
                    self.draw_func = self.canvas.draw_element
                    self.OBJ_form_label.setText(f"Element id: {obj_id}, type: {element_type}, connected node IDs: {node_1} -> {node_2}")
                    self.label_params_label.setText(f"Element id: {obj_id} Label parameters")
                    # Podmiana obrazu:
                    if element_type in self.element_image_name:
                        image_name = self.element_image_name[element_type]
                    else:
                        image_name = "unknown_element"
                    new_image = QPixmap(os.path.join(self.image_folder, f"{image_name}.png"))
                    self.image_box.setPixmap(new_image) # Wsztrzyknięcie do QLabel (boxa) obrazu
                elif obj_type == "node":
                    # Dodanie napisu węzła nad form layout
                    node_type = self.canvas.nodeOBJ_visuals[obj_id]['support_type']
                    default_params = self.canvas.support_type[node_type]["v_params"]
                    self.default_params = default_params.copy()
                    self.default_label_params = self.canvas.default_node_label_params.copy()
                    constraint = self.canvas.nodes[obj_id]['constraint'].copy()
                    self.draw_func = self.canvas.draw_node
                    def text_converter(val):
                        val_str = str(val).strip().lower()
                        if val is False or val_str == "false":
                            return "fixed"
                        elif val is True or val_str == "true":
                            return "free"
                        else:
                            return "???"
                    t_ux = text_converter(constraint['UX'])
                    t_uz = text_converter(constraint['UZ'])
                    t_ry = text_converter(constraint['RY'])
                    constraint_text = f"[UX: {t_ux}, UZ: {t_uz}, RY: {t_ry}]"
                    self.OBJ_form_label.setText(f"Node id: {obj_id}, constraint type: {node_type}, {constraint_text}")
                    self.label_params_label.setText(f"Node id: {obj_id} Label parameters")
                    # Podmiana obrazu:
                    new_image = QPixmap(os.path.join(self.image_folder, f"{node_type}.png"))
                    self.image_box.setPixmap(new_image) # Wsztrzyknięcie do QLabel (boxa) obrazu
                return True
            else:
                QMessageBox.warning(self, "Error", f"{obj_type} ID not found on canvas.")
                # Powrót do domyślnego labelu
                self.OBJ_form_label.setText(f"No object selected")
                # Powrót do domyślnego obrazu
                self.image_box.setPixmap(self.default_image)
                # Wyłączenie przycisku
                self.apply_btn.setEnabled(False)
                self.close_btn.setEnabled(False)
                self.restore_to_default.setEnabled(False)
                return False
        except ValueError:
            QMessageBox.warning(self, "Error", f"Please provide a valid integer for {obj_type} ID.")
            # Wyłączenie przycisku
            self.apply_btn.setEnabled(False)
            self.close_btn.setEnabled(False)
            self.restore_to_default.setEnabled(False)
            return False

    # Funkcja sczytująca i tworząca listę parametrów w Form_Layout obiektów node/elementOBJ_visuals:
    def create_form_layout(self):
        def make_layout(param_layout, visual_dict):
            reference_dict = {}
            for param, val in visual_dict.items():
                # Zmieniamy wartość na string, żeby weszła do QLineEdit
                line_edit = QLineEdit(str(val)) 
                param_layout.addRow(str(param), line_edit) # w form layout pierwsza opcja (param) jest QLabel
                # Zapisujemy referencję do okienka pod kluczem, żeby odczytać ją przy zapisie
                reference_dict[param] = line_edit
            return reference_dict
        # Pobieranie słowników  na formularze
        obj_params_to_use = self.OBJ_dict.get("visual_parameters", self.default_params)
        label_params_to_use = self.OBJ_dict.get("label", self.default_label_params)
        # Tworzenie słowników LineEdit formularzy oraz samo wypełnienie formularzy:
        self.obj_line_edits = make_layout(self.obj_params_layout, obj_params_to_use)
        self.label_line_edits = make_layout(self.label_params_layout, label_params_to_use)
        return

    # Zbiera do kupy wszystkie funkcje odpowiedzialne za generowanie słownikó i formularzy
    def load_obj_params(self, obj_type):
        self.obj_type = obj_type # Tworzona na potrzeby przycisku restore to default -> musi od nowa wczytać wtedy funkcję load_obj_params(obj_type)
        # Czyszczenie poprzednich pól (jeśli użytkownik wpisałby nowe ID)
        self.clear_param_forms()
        flag = self.get_OBJ_dicts(obj_type)
        if flag:
            self.create_form_layout()
            # Włączenie przycisku
            self.apply_btn.setEnabled(True)
            self.close_btn.setEnabled(True)
            self.restore_to_default.setEnabled(True)
        else:
            pass
        return

    # Funkcja przywracająca ustawienia domyślne:
    def set_to_default(self):
        self.OBJ_dict['visual_parameters'] = self.default_params
        self.OBJ_dict['label'] = self.default_label_params
        self.clear_param_forms()
        self.load_obj_params(self.obj_type)

    # Funkcja zatwierdzająca zmiany
    def save_and_accept(self):
        # Uniwersalna funkcja sczytująca dane z formularza:
        def read_params(form_dict):
            new_params = {}
            for param, line_edit in form_dict.items():
                # Usunięcie białych znaków z widgetu LineEdit formularza
                new_val = line_edit.text().strip()
                # Detekcja liczby (uwzględnia kropkę dziesiętną i ujemne wartości)
                if new_val.replace('.', '', 1).replace('-', '', 1).isdigit():
                    new_val = float(new_val) if '.' in new_val else int(new_val)   
                new_params[param] = new_val
            return new_params

        # Zapisanie parametrów wizualnych obiektu, referencja słownika została ustalona w funkcji get_OBJ_dicts
        new_obj_params = read_params(self.obj_line_edits)
        new_label_params = read_params(self.label_line_edits)
        # Przypisanie nowo ustalonych parametrów do słowników OBJ_visuals
        self.OBJ_dict['visual_parameters'] = new_obj_params
        self.OBJ_dict['label'] = new_label_params
            
        # Wywołanie funkcji rysującej węzeł ustalonej przez get_OBJ_dicts
        self.draw_func(self.loaded_obj_id, refresh_canvas = True)
        
    # Funkcja zamykająca okno
    def close_dialog(self):
        self.save_and_accept()
        self.accept()


# ========================================
# Dialog dodawania węzłów
# ======================================== EDYTOR SIATKI
class NewNodeDialog(QDialog):
    def __init__(self, parent = None, canvas = None):
        super().__init__(parent)
        self.canvas = canvas

        self.setWindowTitle("Add new node")
        self.setModal(True)

        # GŁÓWNY LAYOUT (zapisany jako self, aby inne funkcje miały do niego dostęp)
        self.main_h_layout = QHBoxLayout(self)
        self.main_layout = QVBoxLayout()
        self.main_h_layout.addLayout(self.main_layout, stretch = 3)

        # Layout dolny:
        bottom_bar_lt = QHBoxLayout()
        self.main_layout.addLayout(bottom_bar_lt)
        self.add_node_btn = QPushButton("Add node")
        self.add_exit_btn = QPushButton("Add and exit")
        self.add_node_btn.setEnabled(False)
        self.add_exit_btn.setEnabled(False)
        bottom_bar_lt.addWidget(self.add_node_btn)
        bottom_bar_lt.addWidget(self.add_exit_btn)
        self.add_node_btn.clicked.connect(self.add_draw_node)
        self.add_exit_btn.clicked.connect(self.add_exit)

        # Layout środkowy, musi się pojawić później aby w pamięci były przyciski add_node:
        self.add_node_GUI()

    # Funkcja budująca layout dodawania węzłą:
    def add_node_GUI(self):
        def get_new_id():
            try:
                last_id = max(self.canvas.nodes)# Pobieramy ostatnie id węzła:
                self.new_id = last_id + 1 # nowe id:
                return True
            except ValueError:
                self.new_id = 1
                return True
        # Tworzenie layoutu środkowego:
        if get_new_id():
            # informacja o id nowego węzła:
            self.new_node_id_label = QLabel(f"New node id: {self.new_id}")
            self.main_layout.insertWidget(0, self.new_node_id_label) # wstawiamy na samej górze

            # blok podawani koordynatów:
            self.coords_lt = QHBoxLayout()
            self.main_layout.insertLayout(1, self.coords_lt) # Wstawiamy na środku
            self.coords_X_line = QLineEdit("")
            self.coords_Z_line = QLineEdit("")
            self.coords_lt.addWidget(QLabel("Coordinates:"))
            self.coords_lt.insertWidget(1, QLabel("X: "))
            self.coords_lt.insertWidget(2, self.coords_X_line)
            self.coords_lt.insertWidget(3, QLabel("Z: "))
            self.coords_lt.insertWidget(4, self.coords_Z_line)
            # DOdanie przycisku managementu symbolami jeśli mamy siatkę symboliczną
            if self.canvas.data_type == "symbolic":
                open_symbol_maganer_btn = QPushButton("Symbols manager")
                self.coords_lt.addWidget(open_symbol_maganer_btn)
                open_symbol_maganer_btn.clicked.connect(self.open_symbol_subs_dialog)
            
            # Blok podawania uwiązania:
            self.constraint_lt = QHBoxLayout()
            self.main_layout.insertLayout(2, self.constraint_lt) # Wstawiamy na środku
            constraint_list = ["free", "fixed", "???"]
            self.const_UX_box = QComboBox()
            self.const_UX_box.addItems(constraint_list)
            self.const_UZ_box = QComboBox()
            self.const_UZ_box.addItems(constraint_list)
            self.const_RY_box = QComboBox()
            self.const_RY_box.addItems(constraint_list)
            self.constraint_lt.addWidget(QLabel("Constraints:"))
            self.constraint_lt.insertWidget(1, QLabel("UX: "))
            self.constraint_lt.insertWidget(2, self.const_UX_box)
            self.constraint_lt.insertWidget(3, QLabel("UZ: "))
            self.constraint_lt.insertWidget(4, self.const_UZ_box)
            self.constraint_lt.insertWidget(5, QLabel("RY: "))
            self.constraint_lt.insertWidget(6, self.const_RY_box)
            self.add_node_btn.setEnabled(True)
            self.add_exit_btn.setEnabled(True)

    # Funkcja czyszczenia layoutu:
    def clear_GUI(self):
        # funkcja czyszcząca layouty
        def clean_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        # Czyszczenie layoutów:
        clean_layout(self.coords_lt)
        self.coords_lt.deleteLater()
        clean_layout(self.constraint_lt)
        self.constraint_lt.deleteLater()
        # usuwanie labelu:
        self.new_node_id_label.deleteLater()

    # Funkcja zapisująca nowy węzeł do słownika:
    def save_to_dict(self):
        # Konwersja tekstu combobox na wartość liczbową:
        def convert_text_to_constraint(c_text):
            if c_text == "free":
                return True
            elif c_text == "fixed":
                return False
            else:
                return "???"
        # Fallback do pobrania koordynatów
        def get_cords_val():
            try:
                if self.canvas.data_type == "symbolic":
                    self.X_coords = str(self.coords_X_line.text())
                    self.Z_coords = str(self.coords_Z_line.text())
                else:
                    self.X_coords = float(self.coords_X_line.text())
                    self.Z_coords = float(self.coords_Z_line.text())
                return True
            except (ValueError, TypeError, AttributeError):
                self.coords_Z_line.setText("float value needed")
                self.coords_X_line.setText("float value needed")
                QMessageBox.warning(self,
                                    "Coordinate value Error",
                                    "Coordinate values must be a float number")
                return False
        # Sprawdzenie czy wartości koordynatów są poprawne:
        if get_cords_val():
            # Pobranie wartości z combobox
            UX_constr = convert_text_to_constraint(self.const_UX_box.currentText())
            UZ_constr = convert_text_to_constraint(self.const_UZ_box.currentText())
            RY_constr = convert_text_to_constraint(self.const_RY_box.currentText())
            # Tworzenie nowego klucza self.canvas.nodes:
            self.canvas.nodes[self.new_id] = {
                'id': self.new_id,
                'constraint': {"UX": UX_constr, "UZ": UZ_constr, "RY": RY_constr},
                'coordinates': {"X": self.X_coords, "Z": self.Z_coords}
            }
            # Tworzenie nowego słownika OBJ_visuals:
            support_type = self.canvas.map_node_constraints(self.new_id)
            raw_params = self.canvas.support_type[support_type]['v_params']
            v_params = raw_params.copy()
            # Zapisanie kompletnego stanu do pamięci płótna
            self.canvas.nodeOBJ_visuals[self.new_id] = {
                    'support_type': support_type,
                    'visual_parameters': v_params
                    }
            return True
        else:
            return False

    # Funkcja zbiorcza rysowania nowego węzła i aktualizowania dialogu:
    def add_draw_node(self):
        if self.save_to_dict():
            self.canvas.draw_node(self.new_id, refresh_canvas = True)
            # Updateowanie listy:
            self.canvas.make_OBJ_lists()
            # Refreshowanie GUI
            self.clear_GUI()
            self.add_node_GUI()

    # Funkcja otwierająca dialog edycji słownika substytutów
    def open_symbol_subs_dialog(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas, initial_symbol_directory = "length")
        dialog.exec()

    # zapis i wyjście:
    def add_exit(self):
        self.add_draw_node()
        self.accept()


# ========================================
# Dialog edycji węzłów
# ======================================== EDYTOR SIATKI
class EditNodeDialog(QDialog):
    def __init__(self, parent = None, canvas = None):
        super().__init__(parent)
        self.canvas = canvas

        self.setWindowTitle("Node editor")
        self.setModal(True)

        # Layout główny:
        self.main_h_layout = QHBoxLayout(self) # w razie jakby chciano dodać po boku zdjęcia
        self.main_layout = QVBoxLayout() # de facto główny layout wertykalny
        self.main_h_layout.addLayout(self.main_layout, stretch = 3)

        # Pasek szukania węzła:
        serach_bar_lt = QHBoxLayout()
        self.main_layout.addLayout(serach_bar_lt)
        self.nodeID_line = QLineEdit("")
        self.load_node_ID_btn = QPushButton("Load node parameters")
        # Dodanie do layoutu paska szukania
        serach_bar_lt.addWidget(QLabel("Enter node ID:"))
        serach_bar_lt.addWidget(self.nodeID_line)
        serach_bar_lt.addWidget(self.load_node_ID_btn)
        # Łączenie przycisku potwierdzenia wyboru
        self.load_node_ID_btn.clicked.connect(self.build_nodeGUI)
        # Zabezpieczenie w postaci czyszczenia formularzy w momencie zmiany wyboru id:
        self.nodeID_line.textChanged.connect(self.clear_forms)

        # Layout formulażowy parametrów węzła:
        self.picked_node_id = QLabel("Selected node ID: node not selected")
        self.main_layout.addWidget(self.picked_node_id)
        # formularz informacyjny węzłą
        self.node_info_form = QFormLayout()
        # formularz edycji węzła:
        self.node_edit_form = QFormLayout()
        # Pozycionowanie formularzy
        self.current_param_label = QLabel("")
        self.current_param_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit_param_label = QLabel("")
        self.edit_param_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.current_param_label)
        self.main_layout.addLayout(self.node_info_form)
        self.main_layout.addWidget(self.edit_param_label)
        self.main_layout.addLayout(self.node_edit_form)


        # Layout dolnego paska:
        exit_bar_lt = QHBoxLayout()
        self.apply_btn = QPushButton("Apply changes")
        self.sync_elements_btn = QPushButton("Sync connected elements")
        self.close_btn = QPushButton("Save & close")
        exit_bar_lt.addWidget(self.apply_btn)
        exit_bar_lt.addWidget(self.sync_elements_btn)
        exit_bar_lt.addWidget(self.close_btn)
        self.apply_btn.setEnabled(False)
        self.sync_elements_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        # Wymuszenie dolnej pozycji przycisków powrotnych
        self.main_layout.addStretch()
        self.main_layout.addLayout(exit_bar_lt)
        # Połączenie przycisków:
        self.apply_btn.clicked.connect(self.save_changes)
        self.close_btn.clicked.connect(self.close_dialog)
        self.sync_elements_btn.clicked.connect(self.refresh_connected_elements)
        # Parametry, zmienne:
        self.loaded_id = None
        self.new_params = {}

    # Funkcja czyszcząca formularze:
    def clear_forms(self):
        self.loaded_id = None
        self.new_params = {}
        # usuwanie części formulażowej:
        def clear_form_list(form_list):
            while form_list.count():
                item = form_list.takeAt(0)
                widget = item.widget()
                layout = item.layout()
                if widget is not None:
                    widget.deleteLater()  # To usuwa widżet (np. QLineEdit, QLabel)
                elif layout is not None:
                    clear_form_list(item.layout()) # Rekurencja, jeśli w środku był inny layout (na przykład HBoxLayout)
                else:
                    del item
        # Czyszczenie przycisków:
        self.picked_node_id.setText("Selected node ID: node not selected")
        self.current_param_label.setText("")
        self.edit_param_label.setText("")
        # Czyszczenie formularzy:
        clear_form_list(self.node_info_form)
        clear_form_list(self.node_edit_form)
        # Blokowanie przycisków
        self.apply_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.sync_elements_btn.setEnabled(False)

    # Funkcja sprawdzająca czy wybrany węzeł jest obecny w słowniku i zwracająca referencje słowników:
    def get_nodes_dict(self):
        try:
            n_id = int(self.nodeID_line.text())
            if n_id in self.canvas.nodes:
                self.loaded_id = n_id
                self.constraint_dict = self.canvas.nodes[self.loaded_id]['constraint']
                self.coordinates_dict = self.canvas.nodes[self.loaded_id]['coordinates']
                self.visual_dict = self.canvas.nodeOBJ_visuals[self.loaded_id]
                return True
            else:
                QMessageBox.warning(self, "Error", f"Node ID {n_id} not found on canvas.")
                # Powrót do domyślnego labelu
                self.picked_node_id.setText("Selected node ID: node not selected")
                return False
        except ValueError:
            QMessageBox.warning(self, "Error", f"Please provide a valid integer for node ID.")
            return False

    # Funkcja budująca interfejs po kliknięciu przycisku, zbiera wszystko do kupy:
    def build_nodeGUI(self):
        # czyścimy formularze
        self.clear_forms()
        if self.get_nodes_dict(): # sprawdzamy czy udało się pobrać dane węzła:
            self.build_current_properties_form()
            self.build_node_edit_form()
            # Włączanie przycisków
            self.apply_btn.setEnabled(True)
            self.close_btn.setEnabled(True)
            self.sync_elements_btn.setEnabled(True)
        else:
            # Wyłączanie przycisków
            self.apply_btn.setEnabled(False)
            self.close_btn.setEnabled(False)
            self.sync_elements_btn.setEnabled(False)
            # Powrót do domyślnego labelu
            self.picked_node_id.setText("Selected node ID: node not selected")

    # Funkcja budująca formularz obecnych włąściwości węzła
    def build_current_properties_form(self):
        self.current_param_label.setText("Selected node parameters:")
        current_label_font = self.current_param_label.font()
        current_label_font.setPointSize(12)
        self.current_param_label.setFont(current_label_font)
        self.picked_node_id.setText(f"Selected node ID: {self.loaded_id}")
        coordinates_label = QLabel("current coordinates:")
        constraint_label = QLabel("current constraint:")
        # Pobranie wartości
        val_X_cord = self.coordinates_dict['X']
        val_Z_cord = self.coordinates_dict['Z']
        val_UX_constr = self.convert_constraint_to_text(self.constraint_dict['UX'])
        val_UZ_constr = self.convert_constraint_to_text(self.constraint_dict['UZ'])
        val_RY_const = self.convert_constraint_to_text(self.constraint_dict['RY'])
        # Wyznaczanie koordynatów jakie widzi canvas
        absolute_x, absolute_z, no_coords_flag = self.canvas.get_node_coordinates(self.loaded_id, MessageBox = False)
        if no_coords_flag:
            coords_stat = "INVALID COORDINATES"
            absolute_x = f"{absolute_x}???"
            absolute_z = f"{absolute_z}???"
        else:
            coords_stat = "No errors encountered"
        if self.canvas.data_type == "symbolic":
            coordinates_info = QLabel(f"X: {val_X_cord} , absolute value: {absolute_x}\nZ: {val_Z_cord} , absolute value: {absolute_z}\ncoordinates value status: {coords_stat}")
        else:
            coordinates_info = QLabel(f"X: {absolute_x}  |   Z: {absolute_z}\n coordinates value status: {coords_stat}")
        constraint_info = QLabel(f"UX: {val_UX_constr}  |   UZ: {val_UZ_constr}   |   RY: {val_RY_const}")
        # Dodanie do layoutu:
        self.node_info_form.addRow(coordinates_label, coordinates_info)
        self.node_info_form.addRow(constraint_label, constraint_info)

    # Funkcja budująca formularz edycyjny węzła
    def build_node_edit_form(self):
        # Funkcja budowania combobox
        def create_ComboBox(constraint):
            combo_list = ["free", "fixed", "???"]
            combo_box = QComboBox()
            combo_box.addItems(combo_list)
            combo_box.setCurrentText(self.convert_constraint_to_text(constraint))
            return combo_box
        # Ustawienie labelu
        self.edit_param_label.setText("Provide new node parameters:")
        edit_label_font = self.edit_param_label.font()
        edit_label_font.setPointSize(12)
        self.edit_param_label.setFont(edit_label_font)
        # Layout wewnątrz formularza:
        coords_lt = QHBoxLayout()
        const_lt = QHBoxLayout()
        # koordynaty:
        self.new_X_cords = QLineEdit(f"{self.coordinates_dict['X']}")
        self.new_Z_cords = QLineEdit(f"{self.coordinates_dict['Z']}")
        # uwiązania:
        self.new_UX_constr = create_ComboBox(self.constraint_dict['UX'])
        self.new_UZ_constr = create_ComboBox(self.constraint_dict['UZ'])
        self.new_RY_constr = create_ComboBox(self.constraint_dict['RY'])
        # komponowanie layoutów
        coords_lt.addWidget(QLabel("X:"))
        coords_lt.addWidget(self.new_X_cords)
        coords_lt.addWidget(QLabel("Z:"))
        coords_lt.addWidget(self.new_Z_cords)
        # Wstawienie przycisku edycji słowników symboli
        if self.canvas.data_type == "symbolic":
            self.open_symbol_subs_dialog_btn = QPushButton("Symbols manager")
            coords_lt.addWidget(self.open_symbol_subs_dialog_btn)
            self.open_symbol_subs_dialog_btn.clicked.connect(self.open_symbol_subs_dialog)
        coords_lt.addStretch()

        const_lt.addWidget(QLabel('UX'))
        const_lt.addWidget(self.new_UX_constr)
        const_lt.addWidget(QLabel('UZ'))
        const_lt.addWidget(self.new_UZ_constr)
        const_lt.addWidget(QLabel('RY'))
        const_lt.addWidget(self.new_RY_constr)
        const_lt.addStretch()
        # dodanie do formularza:
        self.node_edit_form.addRow(QLabel("new coordinates:"), coords_lt)
        self.node_edit_form.addRow(QLabel("new constraint:"), const_lt)
        # tworzenie przycisku usunięcia węzła:
        delete_row_lt = QHBoxLayout()
        self.delete_node_btn = QPushButton("Delete node")
        self.delete_node_btn.setStyleSheet("background-color: red; color: white;")
        # Wymaganie potwierdzenia akcji:
        def deleting_confirmation():
            confirm = QMessageBox.information(self, "Node removal cosenquences", 
                                                "Deleting node can corrupt element connected to it.\n"
                                                f"Proceed with deleting node id: {self.loaded_id}",
                                                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if confirm == QMessageBox.StandardButton.Ok:
                self.delete_node()
                return
            else:
                return
        # Informacja dla urzytkownika:
        def deleting_message():
            QMessageBox.information(self, "Node removal cosenquences", 
                                    "Deleting node can corrupt element connected to it.\n"
                                    "Assigning new node to the element can be done via element edit dialog")
        info_btn = QPushButton()
        # Pobieramy wbudowaną ikonę ostrzeżenia z systemu
        exclamation_icon = info_btn.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        info_btn.setIcon(exclamation_icon)
        info_btn.clicked.connect(deleting_message)
        self.delete_node_btn.clicked.connect(deleting_confirmation)
        delete_row_lt.addWidget(self.delete_node_btn)
        delete_row_lt.addWidget(info_btn)
        self.node_edit_form.addRow(QLabel("--------------"), delete_row_lt)
        
    # Funkcje konwertujące oznaczenia uwiązań:
    def convert_constraint_to_text(self, constraint):
        val_str = str(constraint).strip().lower()
        if constraint is True or val_str == "true":
            return "free"
        elif constraint is False or val_str == "false":
            return "fixed"
        else:
            return "???"

    def convert_text_to_constraint(self, c_text):
        if c_text == "free":
            return True
        elif c_text == "fixed":
            return False
        else:
            return "???"

    # Funkcja szukająca id elementu który jest połączony z węzłem
    def locate_connected_elements(self):
        connected_elements = {}
        for e_id, params in self.canvas.elements.items():
            if params['node_1_id'] == self.loaded_id:
                connected_elements[e_id] = "node_1_id"
            elif params['node_2_id'] == self.loaded_id:
                connected_elements[e_id] = "node_2_id"
        return connected_elements

    # Funkcja odświeżania elementów które są połączone z węzłem:
    def refresh_connected_elements(self):
        # tworzenie słownika połączonych elementów:
        connected_elements = self.locate_connected_elements()
        # Pętla rysująca elementy połączone z węzłem:
        for e_id in connected_elements.keys():
            self.canvas.draw_element(e_id, refresh_canvas = True)

    # Funkcja usuwająca węzeł:
    def delete_node(self):
        # Przypisywanie połączonym elementom nieznanego węzła:
        disconnected_list = []
        connected_elements = self.locate_connected_elements()
        for e_id, connected_node in connected_elements.items():
            self.canvas.elements[e_id][connected_node] = "???"
            disconnected_list.append(f"Element id: {e_id}")
            # Rysowanie elementów połączonych z usuniętym węzłem:
            self.canvas.draw_element(e_id, refresh_canvas = True)
        QMessageBox.information(self,
                                "Disconnected elements report\n",
                                "Elements with no assigned node:"
                                f"{disconnected_list}")
        # Wymazanie z MatPlotLib:
        for item in self.canvas.drawn_nodeOBJ[self.loaded_id].values():
            self.canvas.remove_visualOBJ(item) # Funkcja usuwająca elementy MatPlotLib
        # Odświerzenie płutna matplotlib aby widać było, że usunięto węzeł
        self.canvas.draw()
        # Tworzenie listy id powyżej usuwanego
        n_id_to_sort = []
        for n_id in self.canvas.nodes.keys():
            if n_id > self.loaded_id:
                n_id_to_sort.append(n_id)
        # Właściwe sortowanie:
        for n_id in n_id_to_sort:
            nodes_dict = self.canvas.nodes[n_id]
            nodeOBJ_dict = self.canvas.drawn_nodeOBJ[n_id]
            nodeOBJ_visuals_dict = self.canvas.nodeOBJ_visuals[n_id]
            new_n_id = int(n_id) - 1
            nodes_dict["id"] = new_n_id
            self.canvas.nodes[new_n_id] = nodes_dict.copy()
            self.canvas.drawn_nodeOBJ[new_n_id] = nodeOBJ_dict.copy()
            self.canvas.nodeOBJ_visuals[new_n_id] = nodeOBJ_visuals_dict.copy()
            # Rysowanie węzłów ze zmienionym id:
            self.canvas.draw_node(new_n_id, refresh_canvas = True)
        # Usuwanie ostatniego, najwyższego klucza słownika nodes:

        if n_id_to_sort: # Warunek sprawdza czy lista nie jest pusta
            last_id = n_id_to_sort[-1] # Wartość [-1] daje ostatnią pozycję słownika czyli najwyższe id
        else: # Wywołuje się wtedy kiedy usuwamy ostatni węzeł, lista robi się pusta dlatego trzeba dać taki warunek
            last_id = self.loaded_id
        del self.canvas.nodes[last_id]
        del self.canvas.drawn_nodeOBJ[last_id]
        del self.canvas.nodeOBJ_visuals[last_id]
        # Sortowanie słownika elementów, wymagana edycja id poołączonych węzłów:
        for e_id, e_params in self.canvas.elements.items():
            node_1_id = None
            node_2_id = None # dawane warto,sci none żeby potem ify nie wywalały błędów
            try:
                node_1_id = int(e_params["node_1_id"])  
            except ValueError:
                pass
            try:
                node_2_id = int(e_params["node_2_id"]) 
            except ValueError:
                pass
            if node_1_id is not None and node_1_id > self.loaded_id:
                e_params["node_1_id"] = node_1_id - 1
            if node_2_id is not None and node_2_id > self.loaded_id:
                e_params["node_2_id"] = node_2_id - 1
        # Zamykanie GUI edycji węzła:
        self.clear_forms()
        # Updateowanie listy:
        self.canvas.make_OBJ_lists()

    # Funkcja otwierająca dialog edycji słownika substytutów
    def open_symbol_subs_dialog(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas, initial_symbol_directory = "length")
        dialog.exec()

    # Funkcja zapisania zmian do słownika self_nodes:
    def save_changes(self):
        # Tworzenie nowego słownika jaki zostanie przypisany pod self.canvas.nodes[n_id]
        # sczytywanie koordynat:
        try:
            # Jeśli mamy doczyniania z symbolami, musi być string:
            if self.canvas.data_type == "symbolic":
                new_coords_X = str(self.new_X_cords.text())
                new_coords_Z = str(self.new_Z_cords.text())
            else:
                new_coords_X = float(self.new_X_cords.text())
                new_coords_Z = float(self.new_Z_cords.text())
        except ValueError:
            QMessageBox.warning(self, "Unrecognised coords value",
                                "Ensure provided coordinates are convertable to float value")
            return
        # sczytywanie uwiązań:
        new_constr_X = self.convert_text_to_constraint(self.new_UX_constr.currentText())
        new_constr_Z = self.convert_text_to_constraint(self.new_UZ_constr.currentText())
        new_constr_RY = self.convert_text_to_constraint(self.new_RY_constr.currentText())
        # Przypisywanie nowych wartości słownikom, należy użyć update, jak wstawi się znak równości to po prostu nadpisze
        # to jeden słownik self.coordinates_dict bez dotykania self.canvas.nodes
        self.coordinates_dict.update({'X': new_coords_X, 'Z': new_coords_Z})
        self.constraint_dict.update({'UX': new_constr_X, 'UZ': new_constr_Z, 'RY': new_constr_RY})
        # Przypisywanie nowego uwiązania do słowika wizualnego: 
        new_support_type = self.canvas.map_node_constraints(self.loaded_id)
        new_visuals = self.canvas.support_type[new_support_type]["v_params"]
        self.visual_dict['support_type'] = new_support_type
        self.visual_dict['visual_parameters'] = new_visuals.copy()
        # przywołanie funkcji rysującej węzeł:
        self.canvas.draw_node(self.loaded_id, refresh_canvas = True)
        # Updateowanie listy:
        self.canvas.make_OBJ_lists()
        # restartowanie GUI aby odnowiły się wartości w sekcji current propertues:
        self.build_nodeGUI()
        return

    def close_dialog(self):
        self.save_changes()
        self.refresh_connected_elements()
        self.accept()


# ========================================
# Dialog dodawania elementów
# ======================================== EDYTOR SIATKI
class NewElementDialog(QDialog):
    def __init__(self, parent = None, canvas = None):
        super().__init__(parent)
        self.canvas = canvas
        self.MainWindow = parent

        self.setWindowTitle("Add new element")
        self.setModal(True)

        # Słownik dostępnych elementów:
        # Słownik zależności parametrów od typu siatki:
        self.available_elements = {
            'Generalized_Coordinate_Framing' :[
                "2N6DOF_EB",
                "2N6DOF_T_EX",
                "2N6DOF_T_FI",
                "2N6DOF_T_RI",
                "2N8DOF_EB_Q",
                "2N4DOF_Truss",
                "Spring_2D",
                "unknown_element"
            ],
            'Parallel_Beam_Approach':[
                "2N4DOF_EB",
                "2N4DOF_T_EX",
                "2N4DOF_T_FI",
                "2N4DOF_T_RI",
                "2N6DOF_EB_Q",
                "2N2DOF_Bar",
                "Spring", 
                "unknown_element"     
            ]
        }
        

        # GŁÓWNY LAYOUT (zapisany jako self, aby inne funkcje miały do niego dostęp)
        self.main_v_layout = QVBoxLayout(self)
        self.main_layout = QVBoxLayout()
        self.main_v_layout.addWidget(QLabel(f"*Available element types depends on mesh type, selected mesh type: {self.MainWindow.mesh_element_layout_type}*"))
        self.main_v_layout.addLayout(self.main_layout)

        # budowanie GUI
        self.build_GUI()
        
        # Layout dolnych przycisków:
        bottom_lt = QHBoxLayout()
        self.main_v_layout.addLayout(bottom_lt)
        add_element_btn = QPushButton("Add element")
        add_element_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        bottom_lt.addWidget(add_element_btn)
        close_btn = QPushButton("close")
        close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        bottom_lt.addWidget(close_btn)
        close_btn.clicked.connect(self.close_dialog)
        add_element_btn.clicked.connect(self.add_element)
        
    # Funkcja czyszczenia:
    def clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)
                child_layout.deleteLater()

    # Funkcja budowania GUI
    def build_GUI(self):
        self.clear_layout(self.main_layout)
        # Pobranie skrajnego id elementu:
        try:
            last_e_id = max(self.canvas.elements)
        except ValueError:
            last_e_id = 0
        self.new_eid = int(last_e_id) + 1
        # label:
        element_id_label = QLabel(f"Add new element ID: {self.new_eid}")
        self.main_layout.addWidget(element_id_label)
        # funkcja tworząca combobox:
        def make_combobox_lt(label_txt, list):
            local_lt = QHBoxLayout()
            self.main_layout.addLayout(local_lt)
            local_lt.addWidget(QLabel(f"{label_txt}"))
            combobox = QComboBox()
            combobox.addItems(list)
            local_lt.addWidget(combobox)
            return local_lt, combobox

        # tworzenie boxa z typami elementów:
        e_type_lt, self.element_type_box = make_combobox_lt("Element Type: ", self.available_elements[self.MainWindow.mesh_element_layout_type])
        try:
            self.element_type_box.setCurrentText(self.canvas.elements[last_e_id - 1]["type"])
        except Exception:
            pass
        e_type_lt.addStretch()
        # tworzenie sekcji połączonych węzłów:
        connected_nodes_lt = QHBoxLayout()
        self.main_layout.addLayout(connected_nodes_lt)
        connected_nodes_lt.addWidget(QLabel("Connected nodes: "))
        def make_line_edit(parent_lt, label_txt):
            local_lt = QHBoxLayout()
            parent_lt.addLayout(local_lt)
            local_lt.addWidget(QLabel(f"{label_txt}"))
            widget = QLineEdit("")
            local_lt.addWidget(widget)
            return local_lt, widget

        node_1_lt, self.node_1_line = make_line_edit(connected_nodes_lt, "node 1 ID: ")
        node_2_lt, self.node_2_line = make_line_edit(connected_nodes_lt, "node 2 ID: ")
        try:
            self.min_nodeID = min(self.canvas.nodes)
            self.max_nodeID = max(self.canvas.nodes)
        except ValueError:
            self.min_nodeID = 0
            self.max_nodeID = 0
        connected_nodes_lt.addWidget(QLabel(f"node ID range: [{self.min_nodeID} --- {self.max_nodeID}]"))
        connected_nodes_lt.addStretch()

        # tworzenie listy materiałów:
        material_lt = QHBoxLayout()
        self.main_layout.addLayout(material_lt)
        material_lt.addWidget(QLabel("Material: "))
        material_type_btn = QPushButton("")
        material_type_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.material_box = QComboBox()
        go_to_material_manager = QPushButton("open Material manager")
        go_to_material_manager.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        material_lt.addWidget(material_type_btn)
        material_lt.addWidget(self.material_box)
        material_lt.addWidget(go_to_material_manager)
        go_to_material_manager.clicked.connect(self.open_material_manager)
        material_lt.addStretch()
        # funkcja zmiany listy materiałów:
        def material_status(clicked = False):
            system_material_list = list(self.canvas.system_materials)
            user_material_list = list(self.canvas.user_defined_materials)
            if not hasattr(self, "material_type") or (hasattr(self, "material_type") and (self.material_type == "system materials" and clicked is False)):
                self.material_type = "system materials"
                material_type_btn.setText("system materials")
                self.material_box.clear()
                self.material_box.addItems(system_material_list)

            elif self.material_type == "system materials" and clicked is True:
                self.material_type = "user defined materials"
                material_type_btn.setText("user defined materials")
                self.material_box.clear()
                self.material_box.addItems(user_material_list)
            elif clicked is True:
                self.material_type = "system materials"
                material_type_btn.setText("system materials")
                self.material_box.clear()
                self.material_box.addItems(system_material_list)
            else:
                material_type_btn.setText("user defined materials")
                self.material_box.clear()
                self.material_box.addItems(user_material_list)
                 
        # wywołanie funkcji za pierwszym uruchomieniem:
        material_status()
        try:
            self.material_box.setCurrentText(self.canvas.elements[last_e_id - 1]["material"])
        except Exception:
            pass
        material_type_btn.clicked.connect(lambda: material_status(clicked = True))

        # Sekcja przekroju/sztywności:
        def build_sec_stif_GUI():
            if hasattr(self, "section_stiff_lt"):
                self.clear_layout(self.section_stiff_lt)
            
            if self.element_type_box.currentText() in ("Spring", "Spring_2D"):
                self.section_stiff_lt, self.stiffness_line = make_line_edit(self.main_layout, "Stiffness: ")
                if self.canvas.data_type == "symbolic":
                    open_symbols_btn = QPushButton("open Symbols manager")
                    open_symbols_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                    self.section_stiff_lt.addWidget(open_symbols_btn)
                    open_symbols_btn.clicked.connect(self.open_symbols_manager)
            else:
                section_list = list(self.canvas.cross_sections)
                self.section_stiff_lt, self.section_box = make_combobox_lt("Cross section ID: ", section_list)
                open_section_btn = QPushButton("open Section manager")
                open_section_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                self.section_stiff_lt.addWidget(open_section_btn)
                open_section_btn.clicked.connect(self.open_cross_section_manager)
                try:
                    self.section_box.setCurrentText(self.canvas.elements[last_e_id - 1]["section_id"])
                except Exception:
                    pass
            self.section_stiff_lt.addStretch()

        build_sec_stif_GUI()
        self.element_type_box.currentTextChanged.connect(build_sec_stif_GUI)

    # funkcja podkreślania:
    def highlight_widget(self, widget, flag):
        if flag is False:
            widget.setStyleSheet("background-color: red; color: white")
        else:
            widget.setStyleSheet("")

    # Funckcja dodawania elementu:
    def add_element(self):
        flag_log = []
        # sprawdzenie czy ID węzłów są zgodne:
        node_1_id = self.node_1_line.text()
        node_2_id = self.node_2_line.text()
        # sprawdzenie integerów
        n1_flag = True
        n2_flag = True
        try:
            node_1_id = int(node_1_id)
        except ValueError:
            n1_flag = False
            flag_log.append(f"Node 1 ID Invalid value - Node ID must be an integer number within range: [{self.min_nodeID} --- {self.max_nodeID}]")
        try:
            node_2_id = int(node_2_id)
        except ValueError:
            n2_flag = False
            flag_log.append(f"Node 2 ID Invalid value - Node ID must be an integer number within range: [{self.min_nodeID} --- {self.max_nodeID}]")
        # sprawdzenie czy węzły są w siatce:
        if node_1_id not in self.canvas.nodes:
            n1_flag = False
            flag_log.append(f"Node 1 ID outside range ({node_1_id}) - Node ID must be within range: [{self.min_nodeID} --- {self.max_nodeID}]")
        if node_2_id not in self.canvas.nodes:
            n2_flag = False
            flag_log.append(f"Node 2 ID outside range ({node_2_id}) - Node ID must be within range: [{self.min_nodeID} --- {self.max_nodeID}]")
        if node_1_id == node_2_id:
            n1_flag = False
            n2_flag = False
            flag_log.append(f"Node 1 ID ({node_1_id}) cannot be the same as Node 2 ID ({node_2_id})")
        # podkreślenie:
        self.highlight_widget(self.node_1_line, n1_flag)
        self.highlight_widget(self.node_2_line, n2_flag)

        # walidacja sztywności:
        if self.element_type_box.currentText() in ("Spring", "Spring_2D"):
            stiff_val = self.stiffness_line.text()
            abs_val, s_flag = self.canvas.validate_val(val = stiff_val, symbol_key = "stiffness")
            if s_flag is False:
                flag_log.append(f"Coulndt convert stiffness value ({stiff_val}) to float number")
            self.highlight_widget(self.stiffness_line, s_flag)

        if flag_log:
            dialog = ListReportLog(self, self.canvas, title = "Invalid New Element parameters", label_text = "Error Report:",  display_list = flag_log)
            dialog.exec()
            return
        # Kod dochodzi tutaj tylko po spełnieniu warunków, zapisywanie znanych wartości:
        e_type = self.element_type_box.currentText()
        self.canvas.elements[self.new_eid] = {
            "id": self.new_eid,
            "type": e_type,
            "node_1_id": node_1_id,
            "node_2_id": node_2_id,
            "material": self.material_box.currentText(),
        }
        if self.element_type_box.currentText() in ("Spring", "Spring_2D"):
            self.canvas.elements[self.new_eid]["stiffness"] = stiff_val
        else:
            self.canvas.elements[self.new_eid]["section_id"] = self.section_box.currentText()
        # Wypełnienie słownika ustawień graficznych:
        v_params = copy.deepcopy(self.canvas.element_type[e_type]["v_params"])
        self.canvas.elementOBJ_visuals[self.new_eid] = {
                                        'element_type' : e_type,
                                        'visual_parameters' : v_params 
                                    }
        # Odświerzenie GUI i rysowanie:
        self.canvas.draw_element(self.new_eid, refresh_canvas = True)
        # Updateowanie listy:
        self.canvas.make_OBJ_lists()
        # Odświerzenie GUI
        self.build_GUI()
        
    # Funkcja otwierająca menager materiałów:
    def open_material_manager(self):
        dialog = MaterialManager(self, self.canvas)
        if dialog.exec() == QDialog.Accepted:
            self.build_GUI()

    # Funkcja otwierająca manager symboli:
    def open_symbols_manager(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas, "stiffness")
        if dialog.exec() == QDialog.Accepted:
            self.build_GUI()

    # Funkcja otwierająca dialog menadżera symboli
    def open_cross_section_manager(self):
        dialog = SectionManager(self, self.canvas)
        if dialog.exec() == QDialog.Accepted:
            self.build_GUI()

    # Funkcja zamykająca okno
    def close_dialog(self):
        self.accept()


# ========================================
# Dialog edycji elementów
# ======================================== EDYTOR SIATKI
class EditElementDialog(QDialog):
    def __init__(self, parent = None, canvas = None):
        super().__init__(parent)
        self.canvas = canvas
        self.MainWindow = parent
        self.sectionmanager = SectionManager(self, self.canvas)

        # Słownik zależności parametrów od typu siatki:
        self.available_elements = {
            'Generalized_Coordinate_Framing' :[
                "2N6DOF_EB",
                "2N6DOF_T_EX",
                "2N6DOF_T_FI",
                "2N6DOF_T_RI",
                "2N8DOF_EB_Q",
                "2N4DOF_Truss",
                "Spring_2D",
                "unknown_element"
            ],
            'Parallel_Beam_Approach':[
                "2N4DOF_EB",
                "2N4DOF_T_EX",
                "2N4DOF_T_FI",
                "2N4DOF_T_RI",
                "2N6DOF_EB_Q",
                "2N2DOF_Bar",
                "Spring", 
                "unknown_element"     
            ]
        }

        self.setWindowTitle("Element editor")
        self.setModal(True)

        # GŁÓWNY LAYOUT (zapisany jako self, aby inne funkcje miały do niego dostęp)
        self.main_h_layout = QHBoxLayout(self)
        self.main_layout = QVBoxLayout()
        self.main_h_layout.addLayout(self.main_layout, stretch = 3)

        # Sekcja górna:
        top_layout = QHBoxLayout()
        self.main_layout.addLayout(top_layout)
        top_layout.addWidget(QLabel("Provide element id:"))
        self.elementID_line = QLineEdit("")
        top_layout.addWidget(self.elementID_line)
        load_e_id_params = QPushButton("Load physical parameters")
        top_layout.addWidget(load_e_id_params)
        self.main_layout.addWidget(QLabel(f"*Available element types depends on mesh type, selected mesh type: {self.MainWindow.mesh_element_layout_type}*"))
        # połączenia:
        load_e_id_params.clicked.connect(self.build_GUI)
        self.elementID_line.textChanged.connect(self.clear_GUI)

        # Sekcja pod wyszukiwaniem:
        self.selected_e_id = QLabel("Selected element ID: element not selected")
        self.main_layout.addWidget(self.selected_e_id)

        # Layout obecnych parametrów:
        self.current_parameters = QVBoxLayout()
        self.main_layout.addLayout(self.current_parameters)

        # Layout edycji
        self.edit_layout = QVBoxLayout()
        self.main_layout.addLayout(self.edit_layout)

        # Sekcja dolna:
        bottom_layout = QHBoxLayout()
        self.main_layout.addLayout(bottom_layout)
        self.apply_btn = QPushButton("Apply changes")
        self.apply_btn.setEnabled(False)
        bottom_layout.addWidget(self.apply_btn)
        self.close_btn = QPushButton("Save & close")
        self.close_btn.setEnabled(False)
        bottom_layout.addWidget(self.close_btn)
        # połączenia
        self.apply_btn.clicked.connect(self.apply_changes)
        self.close_btn.clicked.connect(self.apply_close_dialog)

        # Parametry, zmienne:
        self.loaded_id = None

    # Funkcja czyszcząca GUI
    def clear_GUI(self):
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item 
        # Czyszczenie formularzy:
        clear_layout(self.current_parameters)
        clear_layout(self.edit_layout)
        # Ustawienie przycisków:
        self.apply_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        # Przywrócenie labelów:
        self.selected_e_id.setText("Selected element ID: element not selected")

    # Funkcja znajdująca słownik elementu:
    def get_elements_dict(self):
            try:
                e_id = int(self.elementID_line.text())
                if e_id in self.canvas.elements:
                    self.loaded_id = e_id
                    self.element_dict = self.canvas.elements[self.loaded_id]
                    self.drawnOBJ_dict = self.canvas.drawn_elementOBJ[self.loaded_id] # w razie potrzeby usunięcia
                    self.visual_dict = self.canvas.elementOBJ_visuals[self.loaded_id]
                    return True
                else:
                    QMessageBox.warning(self, "Error", f"Element ID {e_id} not found on canvas.")
                    # Powrót do domyślnego labelu
                    self.selected_e_id.setText("Selected element ID: element not selected")
                    return False
            except ValueError:
                QMessageBox.warning(self, "Error", f"Please provide a valid integer for element ID.")
                return False

    # Funkcja tworząca layout obecnych parametrów:
    def build_current_param_GUI(self):
        # Informacja o wybranym id:
        self.selected_e_id.setText(f"Selected element ID: {self.loaded_id}")
        # Informacja o obecnym typie elementu:
        self.current_E_type = self.element_dict["type"]

        # Dodanie labelu:
        params_label = QLabel(f"Element ID {self.loaded_id} current properties:")
        label_font = params_label.font()
        label_font.setPointSize(12)
        params_label.setFont(label_font)
        self.current_parameters.addWidget(params_label)

        # Funkcja podkreślająca widget jeśli nie należy do słownika:
        def highlignt_widget(label_widget = QLabel(""), dict_key = "", dict_to_check = {}, additional_text = ""):
            if dict_key not in dict_to_check:
                label_widget.setStyleSheet("background-color: red; color: white")
                widget_text = label_widget.text()
                label_widget.setText(f"{widget_text}{additional_text}")
            else:
                label_widget.setStyleSheet("")
           
        # Mały layout typu elementu
        material_type_lt = QHBoxLayout()
        element_type_label = QLabel(f"{self.current_E_type}")
        material_type_lt.addWidget(QLabel("Element type: "))
        material_type_lt.addWidget(element_type_label)
        highlignt_widget(element_type_label, self.current_E_type, self.available_elements[self.MainWindow.mesh_element_layout_type], " (not supported)")
        # Mały layout materiału
        material_label = QLabel(f"{self.element_dict["material"]}")
        material_type_lt.addWidget(QLabel("|"))
        material_type_lt.addWidget(QLabel("Material: "))
        material_type_lt.addWidget(material_label)
        material_type_lt.addStretch()
        highlignt_widget(material_label, self.element_dict["material"], (self.canvas.system_materials | self.canvas.user_defined_materials), " (material not present in library)")
        # Łącznie typu i materiału w jedną linijkę
        self.current_parameters.addLayout(material_type_lt)

        # Informacja o połączonych węzłach
        connected_nodes_lt = QHBoxLayout()
        self.node_1_id = self.element_dict["node_1_id"]
        self.node_2_id = self.element_dict["node_2_id"]
        node_1_label = QLabel(f"{self.node_1_id}")
        node_2_label = QLabel(f"{self.node_2_id}")
        same_node_label = QLabel("")
        connected_nodes_lt.addWidget(QLabel("Connected nodes: "))
        connected_nodes_lt.addWidget(node_1_label)
        connected_nodes_lt.addWidget(QLabel("---->"))
        connected_nodes_lt.addWidget(node_2_label)
        connected_nodes_lt.addWidget(same_node_label)
        connected_nodes_lt.addStretch()
        highlignt_widget(node_1_label, self.node_1_id, self.canvas.nodes, " (not present in mesh)")
        highlignt_widget(node_2_label, self.node_2_id, self.canvas.nodes, " (not present in mesh)")
        if self.node_1_id == self.node_2_id:
            node_1_label.setStyleSheet("background-color: red; color: white")
            node_2_label.setStyleSheet("background-color: red; color: white")
            same_node_label.setText("One element connected to the same nodes")
        # Łączenie z layoutem:
        self.current_parameters.addLayout(connected_nodes_lt)

        # Informacja o przekroju:
        section_stiff_lt = QHBoxLayout()
        self.current_parameters.addLayout(section_stiff_lt)
        if self.element_dict["type"] in ("Spring", "Spring_2D"):
            stiff_widget = self.sectionmanager.create_property_row_fallback(parent_lt = section_stiff_lt, label_text = "Stiffness: ", widget_type = QLabel(""), 
                                                             symbol_key = "stiffness", val = lambda: self.element_dict["stiffness"])
        else:
            section_widget = self.sectionmanager.create_property_row_fallback(parent_lt = section_stiff_lt, label_text = "Cross Section: ", widget_type = QLabel(""), 
                                                             val = lambda: self.element_dict["section_id"], text_val = True, add_stretch = False)
            try:
                if self.element_dict["section_id"] not in self.canvas.cross_sections:
                    section_widget.setStyleSheet("background-color: red; color: white")
                    section_stiff_lt.addWidget(QLabel("(section not present in library)"))
                    section_stiff_lt.addStretch()
                else:
                    section_stiff_lt.addStretch()
                    section_widget.setStyleSheet("")
            except Exception:
                pass
                
    # Funkcja tworząca layout edycji:
    def build_edit_param_GUI(self):
        # Ustawienie labelu sekcji edycji
        edit_gui_label = QLabel(f"Edit element parameters:")
        label_font = edit_gui_label.font()
        label_font.setPointSize(12)
        edit_gui_label.setFont(label_font)
        self.edit_layout.addWidget(edit_gui_label)

        # Sekcja wyboru typu elementu:
        element_type_lt = QHBoxLayout()
        # zależność zawartości combobox od typu siatki:
        combo_box_list = self.available_elements.get(self.MainWindow.mesh_element_layout_type, ["Selected mesh layout does not support any element"])
        self.element_type_box = QComboBox()
        self.element_type_box.addItems(combo_box_list)
        self.element_type_box.setCurrentText(self.current_E_type)
        element_type_lt.addWidget(QLabel("Element type: "))
        element_type_lt.addWidget(self.element_type_box)
        element_type_lt.addStretch()
        self.edit_layout.addLayout(element_type_lt)
        
        # Tworzenie sekcji wybrania węzłów
        connected_nodes_layout = QHBoxLayout()
        self.node_1_line = QLineEdit(f"{self.node_1_id}")
        self.node_2_line = QLineEdit(f"{self.node_2_id}")
        
        # Szukanie najwyższego id węzła:
        def get_last_id():
            try:
                first_id = int(next(iter(self.canvas.nodes))) # Pobieramy pierwsze id węzła
                last_id = int(next(reversed(self.canvas.nodes))) # Pobieramy ostatnie id węzła
            except ValueError:
                first_id = next(self.canvas.nodes)
                last_id = next(reversed(self.canvas.nodes))
                QMessageBox.warning(self,
                                    "Node index error",
                                    f"Some nodes may be unproperly indexed:{first_id}, {last_id}, integer number expected\n"
                                    "Fix node indexing in mesh file")
            return first_id, last_id
        self.first_id, self.last_id = get_last_id()
        connected_nodes_layout.addWidget(QLabel("Connected nodes:"))
        connected_nodes_layout.addWidget(QLabel("node 1 id:"))
        connected_nodes_layout.addWidget(self.node_1_line)
        connected_nodes_layout.addWidget(QLabel("node 2 id:"))
        connected_nodes_layout.addWidget(self.node_2_line)
        connected_nodes_layout.addWidget(QLabel(f"node range: [{self.first_id} --- {self.last_id}]  "))
        connected_nodes_layout.addStretch()
        self.edit_layout.addLayout(connected_nodes_layout)
        
        # Tworzenie sekcji edycji materiału:
        material_h_lt = QHBoxLayout()
        material_type_btn = QPushButton("system materials")
        self.material_box = QComboBox()
        open_material_manager_btn = QPushButton("open material manager")
        material_h_lt.addWidget(QLabel("Material:"))
        material_h_lt.addWidget(material_type_btn)
        material_h_lt.addWidget(self.material_box)
        material_h_lt.addWidget(open_material_manager_btn)
        material_h_lt.addStretch()
        self.edit_layout.addLayout(material_h_lt)
        # Ustawienie odpowiedniego tekstu przycisku materiału
        if self.element_dict["material"] in self.canvas.user_defined_materials:
            material_type_btn.setText("user defined materials")
        else:
            material_type_btn.setText("system materials")
        # Funkcja zieniająca typ materiałów:
        def change_material_type():
            if material_type_btn.text() == "system materials":
                material_type_btn.setText("user defined materials")
            else:
                material_type_btn.setText("system materials")
        # Funkcja tworząca listę i updateująca ComboBox:
        def material_comboBOX_list():
            if material_type_btn.text() == "system materials":
                material_dict = self.canvas.system_materials
            else:
                material_dict = self.canvas.user_defined_materials
            mat_list = []
            for mat_id in material_dict.keys():
                mat_list.append(mat_id)
            self.material_box.clear()
            self.material_box.addItems(mat_list)
        def open_material_manager():
            dialog = MaterialManager(self, self.canvas)
            if dialog.exec() == QDialog.Accepted:
                self.build_GUI()

        material_comboBOX_list() # Po to aby lista wyświetlała się przy pierwszym odpaleniu
        # Ustawienie odpowiedniego materiału jeżeli jest w bibliotece:
        if self.element_dict["material"] in (self.canvas.system_materials | self.canvas.user_defined_materials):
            self.material_box.setCurrentText(f"{self.element_dict["material"]}")
        material_type_btn.clicked.connect(change_material_type)
        material_type_btn.clicked.connect(material_comboBOX_list)
        open_material_manager_btn.clicked.connect(open_material_manager)

        # Tworzenie listy combobox sekcji przekrojów:
        sections_list = []
        for section_id in self.canvas.cross_sections.keys():
            sections_list.append(section_id)

        # likalna funkcja usuwania GUI:
        def delete_lt(lt):
            if lt is None:
                return  
            while lt.count():
                item = lt.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    delete_lt(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item 
        
        # Tworzenie sekcji przekroju poprzecznego:
        def open_section_manager():
            dialog = SectionManager(self, self.canvas)
            if dialog.exec() == QDialog.Accepted:
                self.build_GUI()

        # budowanie edycji sekcji:
        def build_section_GUI():
            self.section_stiff_lt = QHBoxLayout()
            self.section_box = QComboBox()
            self.section_box.addItems(sections_list)
            open_section_manager_btn = QPushButton("open Section Manager")
            self.section_stiff_lt.addWidget(QLabel("Cross section:"))
            self.section_stiff_lt.addWidget(self.section_box)
            self.section_stiff_lt.addWidget(open_section_manager_btn)
            self.section_stiff_lt.addStretch()
            self.edit_layout.insertLayout(4, self.section_stiff_lt)
            open_section_manager_btn.clicked.connect(open_section_manager)
            # wypełnienie comboboxa jeżeli jest info w elemencie:"
            try:
                self.section_box.setCurrentText(self.element_dict["section_id"])
            except Exception:
                pass

        # budowanie sztywności dla sprężyn
        def build_stifness_GUI():
            self.section_stiff_lt = QHBoxLayout()
            self.stiff_line = QLineEdit("")
            self.section_stiff_lt.addWidget(QLabel("Stifness: "))
            self.section_stiff_lt.addWidget(self.stiff_line)
            self.section_stiff_lt.addStretch()
            self.edit_layout.insertLayout(4, self.section_stiff_lt)
            # wypełnienie lineedit jeżeli jest info w elemencie:"
            try:
                self.stiff_line.setText(self.element_dict["stiffness"])
            except Exception:
                pass
            abs_val, val_flag = self.sectionmanager.validate_val(val = self.stiff_line.text(), symbol_key = "stiffness", widget_to_highlight = self.stiff_line)

        # zarządzanie rzędem:
        def make_section_stiff_row():
            if self.element_type_box.currentText() in ("Spring", "Spring_2D"):
                if hasattr(self, "section_stiff_lt"):
                    delete_lt(self.section_stiff_lt)
                build_stifness_GUI()
            else:
                if hasattr(self, "section_stiff_lt"):
                    delete_lt(self.section_stiff_lt)
                build_section_GUI()

        make_section_stiff_row()
        self.element_type_box.currentTextChanged.connect(make_section_stiff_row)
        
        # tworzenie przycisku usunięcia węzła:
        delete_row_lt = QHBoxLayout()
        if self.canvas.data_type == "symbolic":
            delete_row_lt.addStretch()
            open_symbols_btn = QPushButton("Open symbols manager")
            delete_row_lt.addWidget(open_symbols_btn)
            open_symbols_btn.clicked.connect(self.open_symbols_manager)
        self.delete_element_btn = QPushButton("Delete element")
        self.delete_element_btn.setStyleSheet("background-color: red; color: white;")
        
        # Wymaganie potwierdznia akcji
        def deleting_message():
            # Przekazujemy standardowe przyciski za pomocą operatora bitowego '|'
            clicked_btn = QMessageBox.information(
                self, 
                "Element removal information", 
                f"Proceed with deleting element id: {self.loaded_id}?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            # Sprawdzamy, która flaga została zwrócona
            if clicked_btn == QMessageBox.StandardButton.Ok:
                print(f"deleted element id: {self.loaded_id}")
                # funkcja usuwająca element:
                self.delete_element()
                return
            else:
                return
        self.delete_element_btn.clicked.connect(deleting_message)
        delete_row_lt.addStretch()
        delete_row_lt.addWidget(self.delete_element_btn)
        delete_row_lt.addStretch()
        self.edit_layout.addLayout(delete_row_lt)
    
    # Zbiorcza funkcja tworząca GUI:
    def build_GUI(self):
        # czyszczenie poprzednich layoutów:
        self.clear_GUI()
        if self.get_elements_dict():
            # Włączenie layoutów
            self.build_current_param_GUI()
            self.build_edit_param_GUI()
            # Włączenie przycisków:
            self.apply_btn.setEnabled(True)
            self.close_btn.setEnabled(True)
        else: 
            self.apply_btn.setEnabled(False)
            self.close_btn.setEnabled(False)
            self.selected_e_id.setText("Selected element ID: element not selected")

    # Funkcja usuwająca element:
    def delete_element(self):
        # Tworzenie listy elementów do zmiany id:
        elements_to_sort = []
        for e_id in self.canvas.elements.keys():
            if e_id > self.loaded_id:
                elements_to_sort.append(e_id)
        self.elements_to_sort = sorted(elements_to_sort)
        # Usuwanie z canvas obecnego elementu:
        for item in self.canvas.drawn_elementOBJ[self.loaded_id].values():
            # Funkcja usuwająca różne typy obiektów matplotlib
            self.canvas.remove_visualOBJ(item)
            self.canvas.draw() # Odświerzenie zmian canvas
        # rekompozycja słowników:
        for e_id in elements_to_sort:
            new_e_id = e_id - 1
            self.canvas.elements[new_e_id] = self.canvas.elements[e_id]
            self.canvas.elementOBJ_visuals[new_e_id] = self.canvas.elementOBJ_visuals[e_id]
            self.canvas.drawn_elementOBJ[new_e_id] = self.canvas.drawn_elementOBJ[e_id]
        # Usuwanie ostatniej pozycji:
        if elements_to_sort:
            e_last_id = elements_to_sort[-1]
        else:
            e_last_id = self.loaded_id
            self.elementID_line.setText(f"{e_last_id - 1}")
        # Usuwanie:
        del self.canvas.elements[e_last_id]
        del self.canvas.elementOBJ_visuals[e_last_id]
        del self.canvas.drawn_elementOBJ[e_last_id]
        # Refreshowanie canvasa:
        self.refresh_elements()
        # Updateowanie listy:
        self.canvas.make_OBJ_lists()
        # Konieczny refresh GUI:
        self.build_GUI()
        return

    # funkcja odświerzająca elementy:
    def refresh_elements(self):
        if hasattr(self, 'elements_to_sort') and self.elements_to_sort is not None:
            for e_id in self.elements_to_sort:
                id_to_refresh = e_id - 1
                self.canvas.draw_element(id_to_refresh, refresh_canvas = True)
                print(f"Redrawing element id: {id_to_refresh}")
                self.elements_to_sort = None
        return

    # Funkcja przypisująca nowe wartości do słowników:
    def update_element_dicts(self):
        # sczytywanie połączonych węzłów
        def read_node_IDs(node_line_1, node_line_2):
            try:
                node_id_1 = int(node_line_1.text())
                node_id_2 = int(node_line_2.text())
                if (node_id_1 not in self.canvas.nodes) or (node_id_2 not in self.canvas.nodes):
                    QMessageBox.warning(self,
                                        "Node ID is outside range",
                                        f"Node ID must be within provided range [{self.first_id} --- {self.last_id}] \n"
                                        f"Cannot assign provided IDs: node_1: {node_id_1}, node_2: {node_id_2}")
                    flag = False
                else:
                    flag = True                    
                return node_id_1, node_id_2, flag
            except ValueError:
                node_id_1 = node_line_1.text()
                node_id_2 = node_line_2.text()
                QMessageBox.warning(self,
                                    "Wrong node ID format",
                                    "Node ID must be an integer number\n"
                                    f"Cannot assign provided IDs: node_1: {node_id_1}, node_2: {node_id_2}")
                return node_id_1, node_id_2, False
        new_node_1, new_node_2, flag = read_node_IDs(self.node_1_line, self.node_2_line)
        if flag:
            # sczytywanie typu:
            new_E_type = self.element_type_box.currentText()
            new_material = self.material_box.currentText()
            # Przypisanie nowych wartości do słowników
            self.element_dict["type"] = new_E_type
            self.visual_dict["element_type"] = new_E_type
            self.element_dict["material"] = new_material
            self.element_dict["node_1_id"] = new_node_1
            self.element_dict["node_2_id"] = new_node_2
            if new_E_type in ("Spring_2D", "Spring"):
                self.element_dict["stiffness"] = self.stiff_line.text()
            else:
                self.element_dict["section_id"] = self.section_box.currentText()
            # Przypisywanie nowych parametrów wizualnych jeśli zmieniono typ elementu:
            if not (self.current_E_type == new_E_type):
                new_visuals = self.canvas.element_type[new_E_type]['v_params']
                self.visual_dict['visual_parameters'] = new_visuals.copy()
            return

    # Funkcja otwierająca dilog symboli:
    def open_symbols_manager(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas)
        if dialog.exec() == QDialog.Accepted:
            self.build_GUI()
    
    # Funkcja aplikowania zmian:
    def apply_changes(self):
        self.update_element_dicts()
        # Rysowanie elementu
        self.canvas.draw_element(self.loaded_id, refresh_canvas = True)
        # Updateowanie listy:
        self.canvas.make_OBJ_lists()
        # odświerzenie GUI
        self.build_GUI()
        
        
    # Funkcja zamykająca okno
    def apply_close_dialog(self):
        self.apply_changes()
        self.refresh_elements()
        self.accept()


# ========================================
# Dialog Edycji Symboli
# ======================================== EDYTOR SIATKI
class SymbolSubstitutesDialog(QDialog):
    def __init__(self, parent = None, canvas = None, initial_symbol_directory = "length", load_syms = False, LoadsCore = None):
        super().__init__(parent)
        self.canvas = canvas
        self.initial_symbol_directory = initial_symbol_directory
        # referencja do słownika symboli:
        self.symbols_dict = self.canvas.symbol_substitutes
        self.load_flag = load_syms
        # Lista typów symboli:
        self.sym_type_list = sorted(["area", "inertia_y", "length", "stiffness", "pressure", "density", "poissons_ratio", "zuravsky_static_y", "shear_correction_factor"])
        if load_syms:
            self.sym_type_list = sorted(["force", "moment_of_force", "dimensionless", "angle", "distributed_load", "length"])
            self.LoadsCore = LoadsCore
            self.initial_symbol_directory = "force"
            self.symbols_dict = self.LoadsCore.load_symbol_substitutes
        
        self.setWindowTitle("Symbols manager")
        self.setModal(False)

        # GŁÓWNY LAYOUT (zapisany jako self, aby inne funkcje miały do niego dostęp)
        self.main_v_layout = QVBoxLayout(self)
        self.main_layout = QVBoxLayout()
        self.main_v_layout.addLayout(self.main_layout)

        # Dolne przyciski:
        self.close_btn = QPushButton("Close")
        self.main_layout.addStretch()
        bottom_lt = QHBoxLayout()
        self.main_v_layout.addLayout(bottom_lt)
        if not load_syms:
            self.refresh_mesh_btn = QPushButton("Refresh mesh")
            self.refresh_mesh_btn.clicked.connect(self.Refresh_mesh)
            bottom_lt.addWidget(self.refresh_mesh_btn)    
        bottom_lt.addWidget(self.close_btn)
        # Połączenia:
        
        self.close_btn.clicked.connect(self.close_dialog)

        # Funkcje budujące GUI:
        # budowanie gui wyboru rodzaju zmiennej:
        self.build_symbol_type_GUI()
        self.build_edit_symbol_GUI()
        self.build_add_sym_GUI()
        
    # Funkcja czyszcząca GUI
    def clear_GUI(self):
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item 
        clear_layout(self.edit_v_layout)
        self.edit_v_layout.deleteLater()
        clear_layout(self.add_v_layout)
        self.add_v_layout.deleteLater()

    # Funkcja refreshująca GUI po doikonaniu zmian:
    def refresh_GUI(self):  
        self.clear_GUI()
        self.build_edit_symbol_GUI()
        self.build_add_sym_GUI()
    
    # Funkcja budująca GUI wybrania typu
    def build_symbol_type_GUI(self):
        symbol_type_lt = QHBoxLayout()
        self.main_layout.addLayout(symbol_type_lt)
        label = QLabel("Select symbol role:")
        self.symbol_type_box = QComboBox() # ROzwijana lista
        self.symbol_type_box.addItems(self.sym_type_list)
        self.symbol_type_box.setCurrentText(self.initial_symbol_directory)
        symbol_type_lt.addWidget(label)
        symbol_type_lt.addWidget(self.symbol_type_box)
        symbol_type_lt.addStretch()
        # Dostosowanie tekstu dolnego przycisku:
        def alter_refresh_btn_text():
            additional_info = ""
            if self.symbol_type_box.currentText() == "length":
                additional_info = f"\n(required after changeing length values)"
            self.refresh_mesh_btn.setText(f"Refresh mesh{additional_info}")

        if not self.load_flag:
            alter_refresh_btn_text()
            self.symbol_type_box.currentTextChanged.connect(alter_refresh_btn_text)
        # Połączenie z tworzeniem GUI edycji:
        # Ponieważ nie trzeba budować od nowa całego GUI wyboru typu - wystarczy tylko zmienić tekst jednego przycisku:   
        self.symbol_type_box.currentTextChanged.connect(self.clear_GUI)
        self.symbol_type_box.currentTextChanged.connect(self.build_edit_symbol_GUI)
        self.symbol_type_box.currentTextChanged.connect(self.build_add_sym_GUI)

    # Funkcja budująca GUI edycji parametru symbolu:
    def build_edit_symbol_GUI(self):
        self.edit_v_layout = QVBoxLayout()
        edit_h_layout = QHBoxLayout()
        edit_GUI_label = QLabel(f"Edit {self.symbol_type_box.currentText()} symbol values:")
        edit_font = edit_GUI_label.font()
        edit_font.setPointSize(12)
        edit_GUI_label.setFont(edit_font)
        self.edit_v_layout.addWidget(edit_GUI_label)
        self.edit_v_layout.addLayout(edit_h_layout)
        self.main_layout.addLayout(self.edit_v_layout)
        # elementy:
        edit_h_layout.addWidget(QLabel("Selected symbol:"))
        self.selected_symbol_box = QComboBox()
        edit_h_layout.addWidget(self.selected_symbol_box)
        edit_h_layout.addWidget(QLabel("value:"))
        self.symbol_edit_val_line = QLineEdit("")
        edit_h_layout.addWidget(self.symbol_edit_val_line)
        Apply_changes_btn = QPushButton("apply changes")
        edit_h_layout.addWidget(Apply_changes_btn)
        Delete_symbol_btn = QPushButton("Delete symbol")
        Delete_symbol_btn.setStyleSheet("background-color: red; color: white;")
        self.edit_v_layout.addWidget(Delete_symbol_btn)
        # Blok ustalania listy dostępnych symboli:
        available_symbols_list = []
        if self.symbol_type_box.currentText() in self.symbols_dict:
            for sym_name in self.symbols_dict[self.symbol_type_box.currentText()].keys():
                available_symbols_list.append(sym_name)
        # Tworzenie słownika aby nie było afery
        else:
            self.symbols_dict[self.symbol_type_box.currentText()] = {}
        # Komunikat o braku symboli:
        if not available_symbols_list:
            edit_h_layout.addWidget(QLabel(f"No {self.symbol_type_box.currentText()} role symbols detected"))
            Delete_symbol_btn.setEnabled(False)
            Delete_symbol_btn.setText("Delete symbol (No symbols)")
        # Sortowanie alfabetyczne symboli, "key=str.lower" - omija znaczenie wielkich liter normalnie mają pierszeństwo przed małymi
        available_symbols_list = sorted(available_symbols_list, key = str.lower) 
        self.selected_symbol_box.addItems(available_symbols_list)
        # Funkcja przypisania wartości:
        def assign_sym_val():
            if self.selected_symbol_box.currentText() in self.symbols_dict[self.symbol_type_box.currentText()]:
                self.symbol_edit_val_line.setText(f"{self.symbols_dict[self.symbol_type_box.currentText()][self.selected_symbol_box.currentText()]}")
                try:
                    float(self.symbol_edit_val_line.text())
                    self.symbol_edit_val_line.setStyleSheet("background-color: white; color: black;")
                except Exception:
                    self.symbol_edit_val_line.setStyleSheet("background-color: red; color: white;")
        # wykonujemy funkcję przy pierwszym otwarciu
        assign_sym_val()
        # Jeśli zmieniliśmy symbol - dostosowujemy wartość:
        self.selected_symbol_box.currentTextChanged.connect(assign_sym_val)
        # Połączenie z funkcją zapisywania zmian:
        Apply_changes_btn.clicked.connect(lambda: self.apply_changes(new_sym = False))
        # Połączenie z funkcją usuwającą:
        Delete_symbol_btn.clicked.connect(self.delete_symbol)

    # Funkcja wyświetlania GUI dodawania symbolu:
    def build_add_sym_GUI(self):
        self.add_v_layout = QVBoxLayout()
        add_h_layout = QHBoxLayout()
        add_label = QLabel(f"Add new {self.symbol_type_box.currentText()} role symbol:")
        add_font = add_label.font()
        add_font.setPointSize(12)
        add_label.setFont(add_font)
        self.add_v_layout.addWidget(add_label)
        self.new_symbol_line = QLineEdit("")
        self.new_symbol_val_line = QLineEdit("")
        Add_sym_btn = QPushButton("add symbol")
        add_h_layout.addWidget(QLabel("Symbol:"))
        add_h_layout.addWidget(self.new_symbol_line)
        add_h_layout.addWidget(QLabel("value:"))
        add_h_layout.addWidget(self.new_symbol_val_line)
        add_h_layout.addWidget(Add_sym_btn)
        # Dodawanie layoutów:
        self.add_v_layout.addLayout(add_h_layout)
        self.main_layout.addLayout(self.add_v_layout)
        # Połączenie z funkcją dodającą:
        Add_sym_btn.clicked.connect(lambda: self.apply_changes(new_sym = True))

    # Funkcja aktualizowania słownika:
    def apply_changes(self, new_sym = False):
        # sprawdzanie czy wartości są poprawne:
        def val_checker(sym_line, sym_val, new_sym, sym_line_widget, val_line_widget):
            # Sprawdzanie czy nazwa symbolu jest poprawna, tylko dla tworzenia nowego symbolu i pustego combobox w edycji wartości:
            def _validate_name(sym_line, new_sym):
                # Popranie nazwy bez białych znaków na początku lub końcu (strip nie usuwa znaków ze środka):
                sym_name = sym_line.strip()
                # Sprawdzenie czy nie nazwa nie jest "pusta":
                if sym_name == "":
                    QMessageBox.warning(self,
                                        "Invalid symbol name",
                                        f"Symbol name was not provided")
                    return False
                if new_sym:
                    # Sprawdzenie czy nazwa jest poprawnie sformatowana, (Nazwa złożolna z wielkich/małych liter)_(Indeks złożony z małych/wielkich liter / znaków)
                    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*(_[A-Za-z0-9]+)*", sym_name):
                        QMessageBox.warning(self,
                                            "Invalid Symbol Name",
                                            f"The symbol name '{sym_name}' is invalid.\n\n"
                                            "Rules for a valid symbol name:\n"
                                            "• Must start with one or more letters (e.g., \"MySymbol123\")\n"
                                            "• Can optionally end with an underscore and any letters/numbers (e.g., \"MySymbol_123\")\n\n"
                                            "Examples of valid names: \"BaseName\", \"BaseName_123\", \"BaseName_Name2\", \"Youngs_modulus_E_1\"")
                        return False
                    # Sprawdzenie czy nazwa nie zabiera funkcji sympy:
                    new_symbol = sp.sympify(sym_name, locals = self.canvas.LOCAL) # Konwersja na symbol, self.canvas.LOCAL jest słownikiem wyłączającym konwersje I oraz E na liczbę urojoną/eulera  
                    if not isinstance(new_symbol, sp.Symbol): # Sprawdzamy czy sp.sympify nie zainterpretowało nazwy jako sp.func lub sp.pi itd
                        sympy_type = type(new_symbol).__name__ # Pobieramy czym jest new_symbol
                        QMessageBox.warning(self,
                                            "Invalid Symbol Name",
                                            f"The symbol name '{sym_name}' is invalid.\n\n"
                                            f"Symbol names cannot match Python SymPy library expressions \n(detected SymPy match: {sympy_type})\n"
                                            f"The symbol's value must be readily convertible to a float.\n\n"
                                            "Examples of reserved SymPy expressions:\n"
                                            "\"pi\", \"oo\", \"zoo\", \"nan\", \"sin\", \"cos\", \"tan\", \"exp\", \"log\", \"sqrt\"\n\n"
                                            "If you need to use these expressions, enter them into the value fields for mesh objects instead. "
                                            "For example:\n"
                                            "• Node coordinates:\n"
                                            "       X: \"yourSymbol_x*cos(pi/3) - z_symbol*sin(pi/3)\"\n"
                                            "       Z: \"yourSymbol_x*sin(pi/3) + z_symbol*cos(pi/3)\"\n\n"
                                            "This setup assumes that 'z_symbol' and your custom symbol (yourSymbol_x) are existing length symbols with valid float values.")
                        return False
                    # Sprawdzenie duplikatów:
                    if sym_name in self.symbols_dict[self.symbol_type_box.currentText()]:
                        QMessageBox.warning(self,
                                    "Invalid symbol name",
                                    f"Provided symbol name \"{sym_name}\" is already present in {self.symbol_type_box.currentText()} dictionary")
                        return False
                return True
            # Funkcja walidacji wartości
            def _validate_value(sym_val):
                try:
                    float_val = float(sym_val.strip())
                    if not math.isfinite(float_val):
                        QMessageBox.warning(self,
                            "Invalid symbol value",
                            f"Provided symbol value \"{sym_val}\" is not valid\n"
                            "symbol value cannot be infinite")
                        return False, None
                    if float_val < 0:
                        QMessageBox.warning(self,
                            "Invalid symbol value",
                            f"Provided symbol value \"{sym_val}\" is not valid\n"
                            "symbol value cannot be negative")
                        return False, None
                    return True, float_val
                except (ValueError, TypeError, AttributeError):
                    QMessageBox.warning(self,
                                "Invalid symbol value",
                                f"Provided symbol value \"{sym_val}\" is not valid\n"
                                "symbol value must be a positive float number")
                    return False, None
            # Właściwa część funkcji:
            ok = _validate_name(sym_line, new_sym)
            if not ok:
                sym_line_widget.setStyleSheet("background-color: red; color: white;")
                return None
            sym_line_widget.setStyleSheet("background-color: white; color: black;")
            ok, value = _validate_value(sym_val)
            if not ok:
                val_line_widget.setStyleSheet("background-color: red; color: white;")
                return None
            val_line_widget.setStyleSheet("background-color: white; color: black;")
            return value

        if new_sym:
            sym_line = self.new_symbol_line.text()
            sym_val = self.new_symbol_val_line.text()
            sym_val = val_checker(sym_line, sym_val, new_sym, self.new_symbol_line, self.new_symbol_val_line)
            if sym_val is not None:
                self.symbols_dict[self.symbol_type_box.currentText()][sym_line.strip()] = sym_val
                self.refresh_GUI()
        else:
            sym_line = self.selected_symbol_box.currentText()
            sym_val = self.symbol_edit_val_line.text()
            sym_val = val_checker(sym_line, sym_val, new_sym, self.selected_symbol_box, self.symbol_edit_val_line)
            if sym_val is not None:
                self.symbols_dict[self.symbol_type_box.currentText()][sym_line.strip()] = sym_val
                self.refresh_GUI()

    # Funkcja usuwania symbolu:
    def delete_symbol(self):
        message_box = QMessageBox.warning(self,
                            "Symbol Removal Consequences",
                            "Deleting this symbol may corrupt mesh object values that contain it.\n\n"
                            "The mesh will be refreshed and validated after deletion to check for errors.\n\n"
                            "Do you want to proceed with the symbol removal?",
                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if message_box == QMessageBox.StandardButton.Ok:
            del self.symbols_dict[self.symbol_type_box.currentText()][self.selected_symbol_box.currentText()]
            self.refresh_GUI()
            self.Refresh_mesh()
            return
        else:
            return

    # Funkcja rysująca od nowa siatkę:
    def Refresh_mesh(self):
        self.canvas.clear_mesh()
        self.canvas.draw_mesh()
        self.canvas.canvas_settings()
        self.canvas.draw()

    # Funkcja zamykająca okno
    def close_dialog(self):
        self.accept()

# ========================================
# Dialog Edycji Materiałów
# ======================================== EDYTOR SIATKI
class MaterialManager(QDialog):
    def __init__(self, parent = None, canvas = None):
        super().__init__(parent)
        self.canvas = canvas
        # Ustawienia interakcji:
        self.setModal(False)
        self.setWindowTitle("Material manager")
        # Layouty:
        Outline_layout = QVBoxLayout(self) # Główny layout, po to aby przyciski dolne były zawsze w tym samym miejscu
        self.main_layout = QVBoxLayout() # Layout gdzie wrzucane będą GUI poszczegówlnych sekcji dialogu
        Outline_layout.addLayout(self.main_layout)

        # Przyciski dolne:
        bottom_lt = QHBoxLayout()
        Outline_layout.addLayout(bottom_lt)
        #close_btn.clicked.connect(self.close_dialog)
        if self.canvas.data_type == "symbolic":
            symbol_manager_btn = QPushButton("Open Symbols manager")
            bottom_lt.addWidget(symbol_manager_btn)
            symbol_manager_btn.clicked.connect(self.Go_to_symbols_manager)
        close_btn = QPushButton("close")
        bottom_lt.addWidget(close_btn)
        close_btn.clicked.connect(self.close_dialog)

        # Wywołanie funkcji tworzących poszczególne GUI:
        self.user_mat_list = [] # Tylko po to aby cała klasa widziała podczas programowania
        self.new_vals = {}
        self.edit_vals = {}
        self.selected_propetries_mat = next(iter(self.canvas.system_materials)) # pobranie domyślnego wyboru parametrów
        self.build_material_properties_GUI()
        self.build_edit_material_GUI()
        self.build_new_material_GUI()
    
    def Refresh_GUI(self):
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item 
        clear_layout(self.main_layout)
        self.build_material_properties_GUI()
        self.build_edit_material_GUI()
        self.build_new_material_GUI()

    # Funkcja tworząca dialog przeglądania parametrów:
    def build_material_properties_GUI(self):
        # Tworzenie Labelu
        Label = QLabel("Search material properties")
        # Powiększenie czcionki
        Label_font = Label.font()
        Label_font.setPointSize(12)
        Label.setFont(Label_font)
        # Ogólny layout
        self.main_layout.addWidget(Label)
        main_H_lt = QHBoxLayout()
        select_mat_lt = QVBoxLayout()
        properties_lt = QVBoxLayout()
        main_H_lt.addLayout(select_mat_lt)
        main_H_lt.addLayout(properties_lt)
        self.main_layout.addLayout(main_H_lt)
        # Układ selekcji:
        change_mat_btn_label = QLabel("Switch material source:")
        change_mat_type_btn = QPushButton("")
        mat_btn_lt = QHBoxLayout()
        mat_btn_lt.addWidget(change_mat_btn_label)
        mat_btn_lt.addWidget(change_mat_type_btn)
        mat_btn_lt.addStretch() # Dociśnięcie przycisku do labelu
        material_box = QComboBox()
        select_mat_lt.addLayout(mat_btn_lt)
        select_mat_lt.addWidget(material_box)
        # Tworzenie list materiałów:
        def get_list(mat_dict):
            list = []
            for mat_id in mat_dict.keys():
                list.append(mat_id)
            return list
        system_mat_list = get_list(self.canvas.system_materials)
        self.user_mat_list = sorted(get_list(self.canvas.user_defined_materials))
        # Ustawienie odpowiedniej konfiguracji przy inicjacji funkcji, w celu zachowania tego samego wyboru po odświerzeniu layoutu
        if self.selected_propetries_mat in self.canvas.user_defined_materials:
            material_box.addItems(self.user_mat_list)
            material_box.setCurrentText(self.selected_propetries_mat)
            change_mat_type_btn.setText("user defined materials")
        elif self.selected_propetries_mat in self.canvas.system_materials:
            material_box.addItems(system_mat_list)
            material_box.setCurrentText(self.selected_propetries_mat)
            change_mat_type_btn.setText("system materials")
        else:
            material_box.addItems(system_mat_list)
            change_mat_type_btn.setText("system materials")
        # Funkcja zmieniająca listę w zależności od przycisku:
        def change_mat_type():
            if change_mat_type_btn.text() == "system materials":
                change_mat_type_btn.setText("user defined materials")
                material_box.clear()
                material_box.addItems(self.user_mat_list)
            else:
                change_mat_type_btn.setText("system materials")
                material_box.clear()
                material_box.addItems(system_mat_list)
        
        # Layout właściwości
        prop_label = QLabel()
        prop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label = QLabel()
        density_label = QLabel()
        youngs_modulus_label = QLabel()
        poissons_ratio_label = QLabel()
        properties_lt.addWidget(prop_label)
        properties_lt.addWidget(prop_label)
        properties_lt.addWidget(name_label)
        properties_lt.addWidget(density_label)
        properties_lt.addWidget(youngs_modulus_label)
        properties_lt.addWidget(poissons_ratio_label)
        # Funkcja wczytująca properties:
        def build_properties_list():
            # Ustanienie nowego wyboru:
            self.selected_propetries_mat = material_box.currentText()
            # Fukcja sczytująca wartości dla materiału:
            def get_properties(mat_id, mat_dict):
                # Ominięcie zagnieżdżonego słownika
                def return_str(val):
                    try:
                        val = str(val)
                        return val
                    except (ValueError, TypeError, AttributeError):
                        return "???"
                # zaznaczenie błędnych wartości float:
                def check_float_conversion(val, val_widget, val_type):
                    try:
                        float(val)
                        val_widget.setStyleSheet("background-color: white; color: black;")
                        return val
                    except ValueError:
                        if self.canvas.data_type == "symbolic":
                            try:
                                absolute_val = sp.sympify(val, locals = self.canvas.LOCAL)
                                absolute_val = float(absolute_val.subs(self.canvas.symbol_substitutes[val_type]))
                                val_widget.setStyleSheet("background-color: white; color: black;")
                                val = f"{val}, absolute value: {absolute_val}"
                                return val
                            except Exception:
                                val_widget.setStyleSheet("background-color: red; color: white;")
                                val = f"{val}, absolute value: couldnt convert to float"
                                return val
                        val_widget.setStyleSheet("background-color: red; color: white;")
                        val = f"{val}, couldnt convert to float"
                        return val
                name = mat_dict[mat_id].get("name", "???")
                name = return_str(name)
                density = mat_dict[mat_id].get("density", "???")
                density = return_str(density)
                density = check_float_conversion(density, density_label, "density")
                youngs_modulus = mat_dict[mat_id].get("youngs_modulus", "???")
                youngs_modulus = return_str(youngs_modulus)
                youngs_modulus = check_float_conversion(youngs_modulus, youngs_modulus_label, "pressure")
                poissons_ratio = mat_dict[mat_id].get("poissons_ratio", "???")
                poissons_ratio = return_str(poissons_ratio)
                poissons_ratio = check_float_conversion(poissons_ratio, poissons_ratio_label, "poissons_ratio")
                return name, density, youngs_modulus, poissons_ratio

            # Label
            prop_label.setText((f"{self.selected_propetries_mat} properties:"))
            # Pobioeranie właściwego słownika:
            if change_mat_type_btn.text() == "system materials":
                try:
                    name, density, youngs_modulus, poissons_ratio = get_properties(self.selected_propetries_mat, self.canvas.system_materials)
                except KeyError:
                    return
            else:
                try:
                    name, density, youngs_modulus, poissons_ratio = get_properties(self.selected_propetries_mat, self.canvas.user_defined_materials)
                except KeyError:
                    return
            name_label.setText(f"Name / short description: {name}")
            density_label.setText(f"density: {density}")
            youngs_modulus_label.setText(f"Young's modulus: {youngs_modulus}")
            poissons_ratio_label.setText(f"Poissons ratio: {poissons_ratio}")
        # Wyzwolenie wyświetlenia właściwości przy pierwszym otworzeniu funkcji
        build_properties_list()
        
        # Połączenia z przyciskami:
        change_mat_type_btn.clicked.connect(change_mat_type)
        material_box.currentTextChanged.connect(build_properties_list)

    # Funkcja tworząca dialog edycji mteriału:
    def build_edit_material_GUI(self):
        # Słownik:
        self.edit_vals = {}
        # Ustawienie labelu:
        label = QLabel("Edit user defined material")
        label_text = label.font()
        label_text.setPointSize(12)
        label.setFont(label_text)
        self.main_layout.addWidget(label)
        # Główny layout panelu:
        edit_h_lt = QHBoxLayout()
        self.main_layout.addLayout(edit_h_lt)
        # Sekcja wybierania i zmiany nazwy:
        left_lt = QFormLayout()
        edit_h_lt.addLayout(left_lt)
        self.edit_selection_box = QComboBox()
        self.edit_selection_box.addItems(self.user_mat_list)
        # Ustawianie odpowiedniego wyboru:
        if hasattr(self, "selected_edit_mat_id"):
            self.edit_selection_box.setCurrentText(self.selected_edit_mat_id)
        self.edited_mat_id = QLineEdit("")
        self.edited_mat_name = QLineEdit("")
        left_lt.addRow(QLabel("Select material to edit: "), self.edit_selection_box)
        left_lt.addRow(QLabel("Edit material id: "), self.edited_mat_id)
        left_lt.addRow(QLabel("Edit material name: "), self.edited_mat_name)
        # Sekcja właściwości:
        right_lt = QFormLayout()
        edit_h_lt.addLayout(right_lt)
        self.edited_density = QLineEdit("")
        self.edited_youngs = QLineEdit("")
        self.edited_possion = QLineEdit("")
        right_lt.addRow(QLabel("density: "), self.edited_density)
        right_lt.addRow(QLabel("Young's modulus: "), self.edited_youngs)
        right_lt.addRow(QLabel("Poissons ratio: "), self.edited_possion)
        self.edit_vals["id"] = self.edited_mat_id
        self.edit_vals["name"] = self.edited_mat_name
        self.edit_vals["youngs"] = self.edited_youngs
        self.edit_vals["density"] = self.edited_density
        self.edit_vals["possion"] = self.edited_possion
        # Funkcja znajdywania wartości
        def get_current_properties(property = None):
            mat_id = self.edit_selection_box.currentText()
            if not mat_id:
                return "matetial id not selected"
            if property == "id":
                return mat_id
            if mat_id in self.canvas.user_defined_materials:
                val = self.canvas.user_defined_materials[mat_id].get(property, "???")
                return val
            else:
                return f"coldnt find {mat_id} in library"
        # Funkcja wypełniania LineEditów:
        def fill_line_edits():
            self.edited_mat_id.setText(f"{get_current_properties(property = "id")}")
            self.edited_mat_name.setText(f"{get_current_properties(property = "name")}")
            self.edited_density.setText(f"{get_current_properties(property = "density")}")
            self.edited_youngs.setText(f"{get_current_properties(property = "youngs_modulus")}")
            self.edited_possion.setText(f"{get_current_properties(property = "poissons_ratio")}")
        # Wywoływanie funkcji:
        fill_line_edits()
        self.edit_selection_box.currentTextChanged.connect(fill_line_edits)
        # DOdanie przycisku apply changes i delete:
        btn_lt = QVBoxLayout()
        apply_changes_btn = QPushButton("Apply changes")
        delete_btn = QPushButton("Delete material")
        delete_btn.setStyleSheet("background-color: red; color: white;")
        btn_lt.addWidget(apply_changes_btn)
        btn_lt.addWidget(delete_btn)
        edit_h_lt.addLayout(btn_lt)
        # Połączenia:
        apply_changes_btn.clicked.connect(lambda: self.apply_changes(new = False, delete = "rename"))
        delete_btn.clicked.connect(lambda: self.apply_changes(new = False, delete = "only"))

    # Funkcja tworząca dialog dodania nowego mteriału
    def build_new_material_GUI(self):
        # Label:
        # słownik wartości:
        self.new_vals = {}
        label = QLabel("Add new material")
        label_text = label.font()
        label_text.setPointSize(12)
        label.setFont(label_text)
        self.main_layout.addWidget(label)
        # Główny layout:
        new_h_ly = QHBoxLayout()
        self.main_layout.addLayout(new_h_ly)
        # Sekcja nazwy i id:
        left_lt = QFormLayout()
        new_h_ly.addLayout(left_lt)
        self.new_mat_id = QLineEdit("")
        self.new_mat_name = QLineEdit("")
        left_lt.addRow(QLabel("ID: "), self.new_mat_id)
        left_lt.addRow(QLabel("Name: "), self.new_mat_name)
        # Sekcja wartości fizycznych:
        right_lt = QFormLayout()
        new_h_ly.addLayout(right_lt)
        self.new_density = QLineEdit("")
        self.new_youngs = QLineEdit("")
        self.new_possion = QLineEdit("")
        right_lt.addRow(QLabel("density: "), self.new_density)
        right_lt.addRow(QLabel("Young's modulus: "), self.new_youngs)
        right_lt.addRow(QLabel("Poissons ratio: "), self.new_possion)
        self.new_vals["id"] = self.new_mat_id
        self.new_vals["name"] = self.new_mat_name
        self.new_vals["youngs"] = self.new_youngs
        self.new_vals["density"] = self.new_density
        self.new_vals["possion"] = self.new_possion
        # Sekcja przycisku:
        add_btn = QPushButton("Add material")
        new_h_ly.addWidget(add_btn)
        # Połączenia
        add_btn.clicked.connect(lambda: self.apply_changes(new = True))
        return
    
    # Funkcja zapisująca zmiany:
    def apply_changes(self, new = False, delete = False):
        if new and delete:
            print("ERROR - CANNOT SIMUTAINOUSLY CREATE AND DELETE MATERIAL: apply_changes(new = True, delete = True) <-----")
            return
        if new:
            values = self.new_vals.copy()
            if not values["id"].text():
                QMessageBox.warning(self,
                            "Invalid material id",
                            f"Material ID not provided")
                return
            if values["id"].text() in self.canvas.user_defined_materials:
                QMessageBox.warning(self,
                            "Invalid new material id",
                            f"Material ID: {values["id"].text()} is already present in user's materials library")
                return
            if values["id"].text() in self.canvas.system_materials:
                QMessageBox.warning(self,
                            "Invalid new material id",
                            f"Material ID: {values["id"].text()} is already present in system materials library")
                return
        else:
            values = self.edit_vals.copy()
            old_id = self.edit_selection_box.currentText()
            if values["id"].text() in self.canvas.user_defined_materials and values["id"].text() != old_id:
                QMessageBox.warning(self,
                            "Invalid new material id",
                            f"Material ID: {values["id"].text()} is already present in user's materials library")
                return
            # Przypisywanie wszystkim elementom nowe ID jeżeli doszło do zmiany:
            if old_id != values["id"]:
                for e_id, e_dict in self.canvas.elements.items():
                    if e_dict["material"] == old_id:
                        e_dict["material"] = values["id"].text()
            if not values["id"].text():
                            QMessageBox.warning(self,
                                        "Invalid edited material id",
                                        f"Material ID not provided")
                            return
            if old_id in self.canvas.user_defined_materials:
                if delete == "only":
                        del self.canvas.user_defined_materials[old_id]
                        self.Refresh_GUI()
                        return
            else:
                return
            if values["id"].text() in self.canvas.system_materials:
                QMessageBox.warning(self,
                            "Invalid edited material id",
                            f"Material ID: {values["id"].text()} is already present in system materials library")
                return
        # Usuwanie sterego materiału
        if delete == "rename":
            del self.canvas.user_defined_materials[old_id]
        # Przypisywanie nowego/edytowanego materiału:
        if not values["name"].text():
            values["name"].setText("name not provided")
        if self.canvas.data_type == "symbolic":
            self.canvas.user_defined_materials[values["id"].text()] = {
                                    "name": values["name"].text(),
                                    "youngs_modulus": values["youngs"].text(), 
                                    "poissons_ratio": values["possion"].text(),
                                    "density": values["density"].text(),    
                                    }
        else:
            self.error_flag = False
            def convert_to_float(val_line):
                try:
                    val = float(val_line.text())
                    val_line.setStyleSheet("background-color: white; color: black;")
                    return val
                except Exception:
                    val_line.setStyleSheet("background-color: red; color: white;")
                    QMessageBox.warning(self,
                                        "Invalid value",
                                        f"Couldnt convert '{val_line.text()}' to float")
                    self.error_flag = True
                    return val_line.text()
            
            values["youngs"] = convert_to_float(values["youngs"])
            values["density"] = convert_to_float(values["density"])
            values["possion"] = convert_to_float(values["possion"])
            
            if not self.error_flag:
                self.canvas.user_defined_materials[values["id"].text()] = {
                                    "name": values["name"].text(),
                                    "youngs_modulus": values["youngs"] ,
                                    "poissons_ratio": values["possion"],
                                    "density": values["density"], 
                                    }
            if self.error_flag:
                return
        # Ustawianie odpowiedniego wybranego do przeglądu properties materiału aby sekcja szukania zadziałała jako walidacja warotści
        self.selected_propetries_mat = values["id"].text()
        self.selected_edit_mat_id = values["id"].text()  
        self.Refresh_GUI()

    # Funkcja otwierająca dialog edycji symboli
    def Go_to_symbols_manager(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas, initial_symbol_directory = "pressure")
        if dialog.exec() == QDialog.Accepted:
            self.Refresh_GUI()

    # Funkcja zamykająca okno
    def close_dialog(self):
        self.accept()


# ========================================
# Dialog Edycji Przekrojów poprzecznych
# ======================================== EDYTOR SIATKI
class SectionManager(QDialog):
    def __init__(self, parent = None, canvas = None):
        super().__init__(parent)
        self.canvas = canvas
        self.setWindowTitle("Cross Section Manager")
        self.setModal(False)

        # Słownik szablonów przekrojów:
        self.shape_definer = {
                    # 1. Prostokąt
                    'rectangle': {
                        'drawing_function': self.draw_rectangle,
                        'inputs': ["width", "height"],
                        'area': lambda p: p["width"] * p["height"],
                        'max_z': lambda p: p["height"] / 2,
                        'inertia_y': lambda p: p["width"] * p["height"]**3 / 12,
                        'zuravsky_static_y': lambda p: p["width"] * p["height"]**2 / 8,
                        'mass_center': lambda p: [p["width"]/2, p["height"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "rectangle")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "rectangle")["shear_correction_factor"]
                    },

                    # 2. Kwadrat
                    'square': {
                        'drawing_function': self.draw_square,
                        'inputs': ["side"],
                        'area': lambda p: p["side"]**2,
                        'max_z': lambda p: p["side"] / 2,
                        'inertia_y': lambda p: p["side"]**4 / 12,
                        'zuravsky_static_y': lambda p: p["side"]**3 / 8,
                        'mass_center': lambda p: [p["side"]/2, p["side"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "square")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "square")["shear_correction_factor"]                        
                    },

                    # 3. Okrąg / wał pełny
                    'circle': {
                        'drawing_function': self.draw_circle,
                        'inputs': ["diameter"],
                        'area': lambda p: math.pi * p["diameter"]**2 / 4,
                        'max_z': lambda p: p["diameter"] / 2,
                        'inertia_y': lambda p: math.pi * p["diameter"]**4 / 64,
                        'zuravsky_static_y': lambda p: p["diameter"]**3 / 12,
                        'mass_center': lambda p: [p["diameter"]/2, p["diameter"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "circle")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "circle")["shear_correction_factor"]
                    },

                    # 4. Rura okrągła (profil rurowy)
                    'circular_tube': {
                        'drawing_function': self.draw_circular_tube,
                        'inputs': ["outer_diameter", "wall_thickness"],
                        'area': lambda p: math.pi * (p["outer_diameter"]**2 - (p["outer_diameter"] - 2 * p["wall_thickness"])**2) / 4,
                        'max_z': lambda p: p["outer_diameter"] / 2,
                        'inertia_y': lambda p: math.pi * (p["outer_diameter"]**4 - (p["outer_diameter"] - 2 * p["wall_thickness"])**4) / 64,
                        'zuravsky_static_y': lambda p: (p["outer_diameter"]**3 - (p["outer_diameter"] - 2 * p["wall_thickness"])**3) / 12,
                        'mass_center': lambda p: [p["outer_diameter"]/2, p["outer_diameter"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "circular_tube")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "circular_tube")["shear_correction_factor"]
                    },
                    # 5. Rura eliptyczna (profil rurowy)
                    'elliptical_tube': {
                        'drawing_function': self.draw_elliptical_tube,
                        'inputs': ["width", "height", "wall_thickness"],
                        'area': lambda p: math.pi * (p["width"] * p["height"] - (p["width"] - 2 * p["wall_thickness"]) * (p["height"] - 2 * p["wall_thickness"])) / 4,
                        'max_z': lambda p: p["height"] / 2,
                        'inertia_y': lambda p: math.pi * (p["width"] * p["height"]**3 - (p["width"] - 2 * p["wall_thickness"]) * (p["height"] - 2 * p["wall_thickness"])**3) / 64,
                        'zuravsky_static_y': lambda p: (p["width"] * p["height"]**2 - (p["width"] - 2 * p["wall_thickness"]) * (p["height"] - 2 * p["wall_thickness"])**2) / 12,
                        'mass_center': lambda p: [p["width"]/2, p["height"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "elliptical_tube")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "elliptical_tube")["shear_correction_factor"]
                    },
                    # 6. Profil zamknięty prostokątny (skrzynkowy / RHS)
                    'rectangular_tube': {
                        'drawing_function': self.draw_rectangular_tube,
                        'inputs': ["width", "height", "wall_thickness"],
                        'area': lambda p: p["width"] * p["height"] - (p["width"] - 2 * p["wall_thickness"]) * (p["height"] - 2 * p["wall_thickness"]),
                        'max_z': lambda p: p["height"] / 2,
                        'inertia_y': lambda p: (p["width"] * p["height"]**3 - (p["width"] - 2 * p["wall_thickness"]) * (p["height"] - 2 * p["wall_thickness"])**3) / 12,
                        'zuravsky_static_y': lambda p: (p["width"] * p["height"]**2 - (p["width"] - 2 * p["wall_thickness"]) * (p["height"] - 2 * p["wall_thickness"])**2) / 8,
                        'mass_center': lambda p: [p["width"]/2, p["height"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "rectangular_tube")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "rectangular_tube")["shear_correction_factor"]
                    },

                    # 7. Profil zamknięty kwadratowy (SHS)
                    'square_tube': {
                        'drawing_function': self.draw_square_tube,
                        'inputs': ["side", "wall_thickness"],
                        'area': lambda p: p["side"]**2 - (p["side"] - 2 * p["wall_thickness"])**2,
                        'max_z': lambda p: p["side"] / 2,
                        'inertia_y': lambda p: (p["side"]**4 - (p["side"] - 2 * p["wall_thickness"])**4) / 12,
                        'zuravsky_static_y': lambda p: (p["side"]**3 - (p["side"] - 2 * p["wall_thickness"])**3) / 8,
                        'mass_center': lambda p: [p["side"]/2, p["side"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "square_tube")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "square_tube")["shear_correction_factor"]
                    },

                    # 8. Dwuteownik symetryczny (I-beam: IPE, HEB itp.)
                    'i_beam': {
                        'drawing_function': self.draw_i_beam,
                        'inputs': ["height", "width", "flange_thickness", "web_thickness"],
                        'area': lambda p: 2 * p["width"] * p["flange_thickness"] + (p["height"] - 2 * p["flange_thickness"]) * p["web_thickness"],
                        'max_z': lambda p: p["height"] / 2,
                        'inertia_y': lambda p: (p["width"] * p["height"]**3 - (p["width"] - p["web_thickness"]) * (p["height"] - 2 * p["flange_thickness"])**3) / 12,
                        'zuravsky_static_y': lambda p: (p["width"] * p["height"]**2 - (p["width"] - p["web_thickness"]) * (p["height"] - 2 * p["flange_thickness"])**2) / 8,
                        'mass_center': lambda p: [p["width"]/2, p["height"]/2],
                        'shear_width': lambda p: self.additional_param(p, type = "i_beam")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "i_beam")["shear_correction_factor"]
                    },

                    # 9. Teownik (T-section)
                    't_beam': {
                        'drawing_function': self.draw_t_beam,
                        'inputs': ["height", "width", "flange_thickness", "web_thickness"],
                        'area': lambda p: self.t_beam_props(p)["area"],
                        'max_z': lambda p: self.t_beam_props(p)["max_z"],
                        'inertia_y': lambda p: self.t_beam_props(p)["inertia_y"],
                        'zuravsky_static_y': lambda p: self.t_beam_props(p)["zuravsky_static_y"],
                        'mass_center': lambda p: self.t_beam_props(p)["mass_center"],
                        'shear_width': lambda p: self.additional_param(p, type = "t_beam")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "t_beam")["shear_correction_factor"]
                    },

                    # 10. Ceownik
                    'u_channel': {
                        'drawing_function': self.draw_u_channel,
                        'inputs': ["width", "height", "flange_thickness", "web_thickness"],
                        'area': lambda p: self.u_channel_props(p)["area"],
                        'max_z': lambda p: self.u_channel_props(p)["max_z"],
                        'inertia_y': lambda p: self.u_channel_props(p)["inertia_y"],
                        'zuravsky_static_y': lambda p: self.u_channel_props(p)["zuravsky_static_y"],
                        'mass_center': lambda p: self.u_channel_props(p)["mass_center"],
                        'shear_width': lambda p: self.additional_param(p, type = "u_channel")["shear_width"],
                        'shear_correction_factor': lambda p: self.additional_param(p, type = "u_channel")["shear_correction_factor"]
                    },
                    # 11. Surowe wartości:
                    'direct_values' : {
                        'drawing_function' : self.draw_direct_values,
                        'inputs': ["area", "max_z", "inertia_y", "zuravsky_static_y", "shear_width", "shear_correction_factor"],
                        'area': lambda p: p["area"],
                        'max_z': lambda p: p["max_z"],
                        'inertia_y': lambda p: p["inertia_y"],
                        'zuravsky_static_y': lambda p: p["zuravsky_static_y"],
                        'mass_center': lambda p: [0, 0],
                        'shear_width': lambda p: p["shear_width"],
                        'shear_correction_factor': lambda p: p["shear_correction_factor"]      
                    }
                }

        # tworzenie listy typów kształtów:
        self.shape_type_list = []
        for shape_id in self.shape_definer.keys():
            self.shape_type_list.append(shape_id)
        
        # potrzebne rozdzielenie layoutów:
        self.main_horizontal_lt = QHBoxLayout(self)
        self.main_v_layout = QVBoxLayout()
        self.main_horizontal_lt.addLayout(self.main_v_layout)
        self.plotter_lt = QVBoxLayout()
        self.main_horizontal_lt.addLayout(self.plotter_lt)

        # Ustawienie sekcji ustawiania typy GUI:
        self.modify_gui_status = "edit" 

        # Ustawienie layoutu edycji:
        self.main_layout = QVBoxLayout() # koszyk dla layoutu edycji
        self.main_v_layout.addLayout(self.main_layout) # Trzeba podzielić na dwa aby dolne przyciski były na dole
        # budowanie layoutu za pierwszym otwarciem:
        self.selected_section_ID = next(iter(self.canvas.cross_sections), None)
        self.build_GUI()

        # Dolna belka:
        bottom_lt = QHBoxLayout()
        close_btn = QPushButton("close")
        if self.canvas.data_type == "symbolic":
            open_symbol_maneger_btn = QPushButton("open Symbols manager")
            bottom_lt.addWidget(open_symbol_maneger_btn)
            open_symbol_maneger_btn.clicked.connect(self.open_symbol_manager)
        bottom_lt.addWidget(close_btn)
        close_btn.clicked.connect(self.close_dialog)
        self.main_v_layout.addStretch() # Wymuszenie pozycji na samym dole
        self.main_v_layout.addLayout(bottom_lt)

        # Ustawienie layoutu canvas:
        self.AuxCanvas = AuxilaryCanvas(self, width = 4, height = 4)
        Canva_label = QLabel("Cross section visualization")
        canva_label_font = Canva_label.font()
        canva_label_font.setPointSize(12)
        Canva_label.setFont(canva_label_font)
        Canva_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plotter_lt.addWidget(Canva_label)
        # Ustwienie tego aby widget wykresu nie kurczył się:
        self.AuxCanvas.setMinimumWidth(450) # Ustawienie minimalnej szerokości, 350 pikseli wynika z testów
        self.AuxCanvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) # (rozszerzaj się, rozszerzaj się)
        self.plotter_lt.addWidget(self.AuxCanvas)
        # sekcja ustawień
        plot_settings_lt = QVBoxLayout()
        self.main_horizontal_lt.addLayout(plot_settings_lt)
        settings_label = QLabel("Visual settings")
        settings_label_font = settings_label.font()
        settings_label_font.setPointSize(10)
        settings_label.setFont(settings_label_font)
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plot_settings_lt.addWidget(settings_label)
        Thicc_line_thickness_lst = ["0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2", "3", "4", "5"]
        Thinn_line_thickness_lst = ["0.25", "0.5", "0.75", "1", "1.25", "1.5", "1.75", "2"]
        grid_linestyle_lst = ['None', '--', '-', '-.', ':']
        grid_line_opacity_lst = ["0", "0.25", "0.5", "0.75", "1"]
        set_aspect_lst = ['equal', 'auto']
        Thicc_line_clolor_lst = ["black", "blue", "green", "red", "gray", "pink"]
        Thinn_line_color_lst = ["black", "blue", "green", "red", "gray", "pink"]
        Thinn_line_opacity_lst = ["0", "0.25", "0.5", "0.75", "1"]
        Thicc_line_opacity_lst = ["0", "0.25", "0.5", "0.75", "1"]
        Text_size_list = ["0", "2", "6", "8", "10", "12", "14", "16", "18", "20"]
        Margin_lst = ["0", "0.1", "0.25", "0.5", "0.75", "1"]
        # Funkcja tworząca combo boxy
        def make_combobox_lt(parent_lt, label_text, list):
            local_lt = QHBoxLayout()
            parent_lt.addLayout(local_lt)
            local_lt.addWidget(QLabel(f"{label_text}"))
            comboBox = QComboBox()
            local_lt.addWidget(comboBox)
            comboBox.addItems(list)
            return comboBox

        self.thicc_line_box = make_combobox_lt(plot_settings_lt, "thick line width: ", Thicc_line_thickness_lst)
        self.thicc_line_box.setCurrentText("1.5")
        self.thicc_line_color_box = make_combobox_lt(plot_settings_lt, "thick line color: ", Thicc_line_clolor_lst)
        self.thicc_line_color_box.setCurrentText("black")
        self.thicc_line_opacity_box = make_combobox_lt(plot_settings_lt, "thick line transparency: ", Thicc_line_opacity_lst)
        self.thicc_line_opacity_box.setCurrentText("1")
        self.thinn_line_box = make_combobox_lt(plot_settings_lt, "thinn line width: ", Thinn_line_thickness_lst)
        self.thinn_line_box.setCurrentText("0.75")
        self.thinn_line_color_box = make_combobox_lt(plot_settings_lt, "thinn line color: ", Thinn_line_color_lst)
        self.thinn_line_color_box.setCurrentText("gray")
        self.thinn_line_opacity_box = make_combobox_lt(plot_settings_lt, "thinn line transparency: ", Thinn_line_opacity_lst)
        self.thinn_line_opacity_box.setCurrentText("1")
        self.grid_line_box = make_combobox_lt(plot_settings_lt, "grid linestyle: ", grid_linestyle_lst)
        self.grid_line_box.setCurrentText("--")
        self.grid_line_trans_box = make_combobox_lt(plot_settings_lt, "grid transparency: ", grid_line_opacity_lst)
        self.grid_line_trans_box.setCurrentText("0.5")
        self.aspect_box = make_combobox_lt(plot_settings_lt, "set aspect: ", set_aspect_lst)
        self.aspect_box.setCurrentText("equal")
        self.text_size_box = make_combobox_lt(plot_settings_lt, "set font size: ", Text_size_list)
        self.text_size_box.setCurrentText("10")
        self.margin_box = make_combobox_lt(plot_settings_lt, "set margin size: ", Margin_lst)
        self.margin_box.setCurrentText("0.1")
        # Przycisk zarządzania dodatkowymi informacjami:
        def axis_btn_status():
            if axis_btn.text() == "Showing additional info":
                axis_btn.setText("Hiding additional info")
                self.disable_info = True
            else:
                axis_btn.setText("Showing additional info")
                self.disable_info = False
        self.disable_info = False
        axis_btn = QPushButton("Showing additional info")
        plot_settings_lt.addWidget(axis_btn)
        apply_plot_settings_btn = QPushButton("Apply plot settings")
        plot_settings_lt.addStretch()
        plot_settings_lt.addWidget(apply_plot_settings_btn)
        # wywołanie ustawień canvasa:
        self.canvas_settings()
        # Połączenie
        apply_plot_settings_btn.clicked.connect(self.canvas_settings)
        apply_plot_settings_btn.clicked.connect(self.draw_section)
        axis_btn.clicked.connect(axis_btn_status)
        # wywołanie pierwszego rysowania funkcji:
        self.draw_section()
        
    # ========================================================
    
    # Funkcja oddzielna dla liczenia wartości t-ownika:
    def t_beam_props(self, p):
        w = p["width"]
        tf = p["flange_thickness"]
        h = p["height"]
        tw = p["web_thickness"]

        # 1. Pola składowe
        a_flange = w * tf
        a_web = (h - tf) * tw
        a_total = a_flange + a_web

        # 2. Położenie środka ciężkości z_c (od dolnej krawędzi pasa)
        z_flange = tf / 2
        z_web = tf + (h - tf) / 2
        z_c = (a_flange * z_flange + a_web * z_web) / a_total

        # 3. Moment bezwładności I_y (twierdzenie Steinera)
        iy_flange = (w * tf**3 / 12) + a_flange * (z_flange - z_c)**2
        iy_web = (tw * (h - tf)**3 / 12) + a_web * (z_web - z_c)**2
        inertia_y = iy_flange + iy_web

        # 4. Moment statyczny Żurawskiego S_y w osi obojętnej
        if z_c >= tf:
            # Odcięcie części środnika powyżej osi obojętnej
            zuravsky_static_y = tw * (h - z_c)**2 / 2
        else:
            # Odcięcie części pasa poniżej osi obojętnej
            zuravsky_static_y = w * z_c**2 / 2

        return {
            "area": a_total,
            "max_z": max(z_c, h - z_c),
            "inertia_y": inertia_y,
            "zuravsky_static_y": zuravsky_static_y,
            "mass_center": [w/2, z_c]
        }
    
    # Funkcja oddzielna dla liczenia wartości - c-ownika:
    def u_channel_props(self, p):
        w = p["width"]
        h = p["height"]
        tw = p["web_thickness"]
        tf = p["flange_thickness"]

        # 1. Pole powierzchni (pionowy środnik + 2 poziome półki)
        a_flanges = 2 * w * tf
        a_web = (h - 2 * tf) * tw
        area = a_flanges + a_web

        # 2. Położenie środka ciężkości
        # Oś pionowa z jest symetryczna:
        z_c = h / 2
        max_z = h / 2

        # Środek ciężkości w poziomie liczony od zewnętrznej krawędzi środnika (lewa strona):
        # Środnik ma środek w tw / 2, a obie półki w w / 2:
        y_c = (a_web * (tw / 2) + a_flanges * (w / 2)) / area

        # 3. Moment bezwładności I_y (względem poziomej osi obojętnej y)
        # Odpowiada to pełnemu prostokątowi (w x h) minus wycięcie (w - tw) x (h - 2*tf):
        inertia_y = (w * h**3 - (w - tw) * (h - 2 * tf)**3) / 12

        # 4. Moment statyczny Żurawskiego S_y (odcięcie w osi obojętnej z = h/2)
        # Górna połowa przekroju: pas górny + połowa środnika
        zuravsky_static_y = (w * h**2 - (w - tw) * (h - 2 * tf)**2) / 8

        return {
            "area": area,
            "max_z": max_z,
            "inertia_y": inertia_y,
            "zuravsky_static_y": zuravsky_static_y,
            "mass_center": [y_c, z_c]
        }

    # funkcja liczenia dodatkowych wsółczynników
    def additional_param(self, p, type = None):
        if type is None:
            return {
                "shear_width": 1,
                "shear_correction_factor": 1
            }

        elif type in ("rectangle", "square"):
            return {
                "shear_width": 1,
                "shear_correction_factor": 1
            }

        elif type == "circle":
                    return {
                        "shear_width": 1,
                        "shear_correction_factor": 1
                    }
        
        elif type == "circular_tube":
                    return {
                        "shear_width": 1,
                        "shear_correction_factor": 1
                    } 
        
        elif type == "elliptical_tube":
                    return {
                        "shear_width": 1,
                        "shear_correction_factor": 1
                    } 
        
        elif type in ("rectangular_tube", "square_tube"):
                    return {
                        "shear_width": 1,
                        "shear_correction_factor": 1
                    } 
        
        elif type == "i_beam":
                    return {
                        "shear_width": 1,
                        "shear_correction_factor": 1
                    } 
        
        elif type == "t_beam":
                    return {
                        "shear_width": 1,
                        "shear_correction_factor": 1
                    } 
        
        elif type == "u_channel":
                    return {
                        "shear_width": 1,
                        "shear_correction_factor": 1
                    } 

        else:
            return {
                "shear_width": 1,
                "shear_correction_factor": 1
            } 
    
    # ========================================================

    # funkcja usuwająca obiekt:
    def remove_vOBJ(self, vOBJ):
        if isinstance(vOBJ, (list, tuple, set)):
            for item in vOBJ:
                self.canvas.remove_visualOBJ(item)
        else:
            self.canvas.remove_visualOBJ(vOBJ)
    
    # Funkcja ustawień canvasa:
    def canvas_settings(self):
        # przypisanie ustawień stałych:
        self.thicc_line = float(self.thicc_line_box.currentText())
        self.thinn_line = float(self.thinn_line_box.currentText())
        self.thinn_line_color = self.thinn_line_color_box.currentText()
        self.thicc_line_color = self.thicc_line_color_box.currentText()
        self.thinn_opacity = float(self.thinn_line_opacity_box.currentText())
        self.thicc_opacity = float(self.thicc_line_opacity_box.currentText())
        self.text_size = float(self.text_size_box.currentText())

        # ustawienia samego płutna:
        self.AuxCanvas.axes.set_aspect(self.aspect_box.currentText())
        self.AuxCanvas.axes.margins(float(self.margin_box.currentText()))
        self.AuxCanvas.axes.autoscale_view()
        self.AuxCanvas.axes.grid(linestyle = self.grid_line_box.currentText(), alpha = float(self.grid_line_trans_box.currentText()))
        self.AuxCanvas.draw()
        return

    # Funkcja matka wywołująca funkcję rysującą:
    def draw_section(self):
        if hasattr(self, "drawn_sectionOBJ") and self.drawn_sectionOBJ is not None:
            self.remove_vOBJ(self.drawn_sectionOBJ)
        try:
            shape_type = self.canvas.cross_sections[self.selected_section_ID]["shape_type"]
            draw_func = self.shape_definer[shape_type]["drawing_function"]
            self.drawn_sectionOBJ = draw_func()
            self.manage_axis_center(disabled = self.disable_info)
            if self.drawn_sectionOBJ is None:
                self.drawn_sectionOBJ = self.AuxCanvas.axes.text(0.5, 0.5, "shape function not complete", transform = self.AuxCanvas.axes.transAxes, 
                                     ha = "center", va = "center", fontsize = 12, color = "black")
        except Exception as e:
            print(e)
            self.manage_axis_center(disabled = True)
            self.drawn_sectionOBJ = self.AuxCanvas.axes.text(0.5, 0.5, "SHAPE NOT DEFINED", transform = self.AuxCanvas.axes.transAxes, 
                                     ha = "center", va = "center", fontsize = 12, color = "red")
        # Updateowanie canvas z ustawieniem skalowanie
        self.AuxCanvas.axes.relim()
        self.AuxCanvas.axes.autoscale()
        self.AuxCanvas.axes.autoscale_view()
        self.AuxCanvas.draw()
    
    # Funkcja walidująca wartości i zwracająca słownik
    def get_shape_geometry(self):
        validation_flag = True
        try:
            shape_geo_dict = {}
            if self.canvas.cross_sections[self.selected_section_ID]["shape_type"] != "direct_values":
                for param_name, param_val in self.canvas.cross_sections[self.selected_section_ID]["shape_parameters"].items():
                    abs_val, val_flag = self.validate_val(param_val, "length", None)
                    if not val_flag:
                        validation_flag = False
                    shape_geo_dict[param_name] = abs_val
            else:
                 for param_name, param_val in self.canvas.cross_sections[self.selected_section_ID]["shape_parameters"].items():
                    sym_key = "length" if param_name in {"max_z", "shear_width"} else param_name
                    abs_val, val_flag = self.validate_val(param_val, sym_key, None)
                    if not val_flag:
                        validation_flag = False
                    shape_geo_dict[param_name] = abs_val
            return shape_geo_dict, validation_flag
        except Exception:
            validation_flag = False
            return shape_geo_dict, validation_flag

    # rysowanie prostokątnego przekroju         
    def draw_rectangle(self):
        # Pobranie wartości:
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                     ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        w = shape_geo_dict["width"]
        h = shape_geo_dict["height"]
        x_list = [0, w, w, 0, 0]
        z_list = [0, 0, h, h, 0]
        drawn_section = self.AuxCanvas.axes.plot(x_list, z_list, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    def draw_square(self):
        # pobranie wartości
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        a = shape_geo_dict["side"]
        x_list = [0, a, a, 0, 0]
        z_list = [0, 0, a, a, 0]
        drawn_section = self.AuxCanvas.axes.plot(x_list, z_list, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    def draw_circle(self):
        # pobranie wartości
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        r = shape_geo_dict["diameter"]/2
        theta = np.linspace(0, 2*np.pi, 1000)   # kąt od 0 do 2π koło ze wsp biegunowych
        x_full = r * np.cos(theta) + r
        z_full = r * np.sin(theta) + r
        # wpakowywanie wartości dla z:
        drawn_section = self.AuxCanvas.axes.plot(x_full, z_full, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    def draw_circular_tube(self):
        # pobranie wartości
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        r = shape_geo_dict["outer_diameter"] / 2
        r_min = (shape_geo_dict["outer_diameter"] - shape_geo_dict["wall_thickness"]) / 2
        theta = np.linspace(0, 2*np.pi, 1000)   # kąt od 0 do 2π koło ze wsp biegunowych ["outer_diameter", "wall_thickness"],
        x_full = r * np.cos(theta) + r
        z_full = r * np.sin(theta) + r
        x_full_m = r_min * np.cos(theta) + r
        z_full_m = r_min * np.sin(theta) + r
        # podanie dwóch zestawów tworzy [Line2D, Line2D]
        drawn_section = self.AuxCanvas.axes.plot(x_full, z_full, x_full_m, z_full_m, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    def draw_elliptical_tube(self):
        # pobranie wartości
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        r_w = shape_geo_dict["width"]/2
        r_h = shape_geo_dict["height"]/2
        r_w_min = (shape_geo_dict["width"] -  2 * shape_geo_dict["wall_thickness"]) / 2
        r_h_min = (shape_geo_dict["height"] - 2 * shape_geo_dict["wall_thickness"]) / 2
        theta = np.linspace(0, 2*np.pi, 1000)   # kąt od 0 do 2π koło ze wsp biegunowych ["width", "height", "wall_thickness"]
        x_full = r_w * np.cos(theta) + r_w
        z_full = r_h * np.sin(theta) + r_h
        x_full_m = r_w_min * np.cos(theta) + r_w
        z_full_m = r_h_min * np.sin(theta) + r_h
        # podanie dwóch zestawów tworzy [Line2D, Line2D]
        drawn_section = self.AuxCanvas.axes.plot(x_full, z_full, x_full_m, z_full_m, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    def draw_rectangular_tube(self):
        # Pobranie wartości:
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        w = shape_geo_dict["width"]
        h = shape_geo_dict["height"]
        d = shape_geo_dict["wall_thickness"]
        w_min = w - d
        h_min = h - d
        x_list = [0, w, w, 0, 0]
        z_list = [0, 0, h, h, 0]
        x_list_m = [d, w_min, w_min, d, d]
        z_list_m = [d, d, h_min, h_min, d]
        drawn_section = self.AuxCanvas.axes.plot(x_list, z_list, x_list_m, z_list_m,  linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section
    
    def draw_square_tube(self):
        # Pobranie wartości:
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        w = shape_geo_dict["side"]
        d = shape_geo_dict["wall_thickness"]
        w_min = w - d
        x_list = [0, w, w, 0, 0]
        z_list = [0, 0, w, w, 0]
        x_list_m = [d, w_min, w_min, d, d]
        z_list_m = [d, d, w_min, w_min, d]
        drawn_section = self.AuxCanvas.axes.plot(x_list, z_list, x_list_m, z_list_m,  linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    def draw_i_beam(self):
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        w = shape_geo_dict["width"]
        h = shape_geo_dict["height"]
        t = shape_geo_dict["flange_thickness"]
        d = shape_geo_dict["web_thickness"]
        x_list = [0, w, w, w/2+d/2, w/2+d/2, w, w, 0, 0, w/2-d/2, w/2-d/2, 0, 0]
        z_list = [0, 0, t, t, h-t, h-t, h, h, h-t, h-t, t, t ,0]
        drawn_section = self.AuxCanvas.axes.plot(x_list, z_list, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section
    
    def draw_t_beam(self):
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        w = shape_geo_dict["width"]
        h = shape_geo_dict["height"]
        t = shape_geo_dict["flange_thickness"]
        d = shape_geo_dict["web_thickness"]
        x_list = [0, w, w, w/2+d/2, w/2+d/2, w/2-d/2, w/2-d/2, 0, 0]
        z_list = [0, 0, t, t, h, h, t, t, 0]
        drawn_section = self.AuxCanvas.axes.plot(x_list, z_list, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    def draw_u_channel(self):
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(0.5, 0.5, "INVALID SHAPE PROPERTY VALUES", transform = self.AuxCanvas.axes.transAxes, 
                                        ha = "center", va = "center", fontsize = 12, color = "red")
            return drawn_section
        w = shape_geo_dict["width"]
        h = shape_geo_dict["height"]
        t = shape_geo_dict["flange_thickness"]
        d = shape_geo_dict["web_thickness"]
        x_list = [0, w, w, d, d, w, w, 0, 0]
        z_list = [0, 0, t, t, h-t, h-t, h, h, 0]
        drawn_section = self.AuxCanvas.axes.plot(x_list, z_list, linewidth = self.thicc_line, color = self.thicc_line_color, alpha = self.thicc_opacity)
        return drawn_section

    # przekrój symboliczny
    def draw_direct_values(self):
        def _polygon_centroid(x, z):
            # Centroid wielokąta (shoelace). Zakłada, że (x, z) to zamknięty kontur.
            x = np.asarray(x, dtype=float)
            z = np.asarray(z, dtype=float)
            x2 = np.append(x, x[0])
            z2 = np.append(z, z[0])
            cross = x2[:-1] * z2[1:] - x2[1:] * z2[:-1]
            A = cross.sum() * 0.5
            if abs(A) < 1e-12:
                return float(x.mean()), float(z.mean())
            cx = ((x2[:-1] + x2[1:]) * cross).sum() / (6.0 * A)
            cz = ((z2[:-1] + z2[1:]) * cross).sum() / (6.0 * A)
            return float(cx), float(cz)
        
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            drawn_section = self.AuxCanvas.axes.text(
                0.5, 0.5, "INVALID SHAPE PROPERTY VALUES",
                transform=self.AuxCanvas.axes.transAxes,
                ha="center", va="center", fontsize=12, color="red"
            )
            return [drawn_section]

        area = shape_geo_dict.get("area", 0.0)
        max_z = shape_geo_dict.get("max_z", 0.0)
        inertia_y = shape_geo_dict.get("inertia_y", 0.0)
        zuravsky_static_y = shape_geo_dict.get("zuravsky_static_y", 0.0)

        # bazowy promień z pola (bezpiecznie)
        area_eff = max(abs(area), 1e-9)
        r0 = np.sqrt(area_eff / np.pi)

        # znormalizowane współczynniki — każdy parametr „wypycha” inną harmoniczną.
        # tanh ogranicza do (-1, 1), żeby kształt nie eksplodował dla dużych wartości.
        denom_r  = r0 + 1e-9
        denom_r3 = r0**3 + 1e-9

        c1 = 0.35 * np.tanh(max_z / denom_r)    # łamie symetrię lustrzaną (cos θ)
        s1 = 0.25 * np.tanh(max_z / denom_r)    # łamie symetrię lustrzaną (sin θ)
        c2 = 0.30 * np.tanh(inertia_y / denom_r3)   # 2. harmoniczna
        c3 = 0.20 * np.tanh(zuravsky_static_y / denom_r3)   # 3. harmoniczna (nieparzysta → asymetria)
        s3 = 0.15                                            # stała domieszka, gwarantuje brak symetrii

        theta = np.linspace(0.0, 2.0 * np.pi, 400, endpoint=False)

        r = r0 * (
            1.0
            + c1 * np.cos(theta)
            + s1 * np.sin(theta)
            + c2 * np.cos(2.0 * theta)
            + c3 * np.cos(3.0 * theta)
            + s3 * np.sin(3.0 * theta)
        )
        r = np.clip(r, 0.15 * r0, None)   # zabezpieczenie: r musi być > 0

        x = r * np.cos(theta)
        z = r * np.sin(theta)

        # przesuwamy figurę, żeby centroid wypadł w (0, 0)
        x_c, z_c = _polygon_centroid(x, z)
        x = x - x_c
        z = z - z_c

        # rysowanie
        drawn_lines = self.AuxCanvas.axes.plot(
            x, z,
            linewidth=self.thicc_line,
            color=self.thicc_line_color,
            alpha=self.thicc_opacity
        )

        # adnotacja, że to schemat
        drawn_text = self.AuxCanvas.axes.text(
            0.004, 0.2,
            "SCHEMATIC — geometry does not correspond to input values",
            transform=self.AuxCanvas.axes.transAxes,
            ha="left", va="bottom",
            fontsize=8.2, color="gray",
            alpha=1
        )

        drawn_section = list(drawn_lines) + [drawn_text]
        return drawn_section

    # Funkcja rysująca środek (Osie itd):
    def draw_axis_center(self):
        # Traktowane jako walidacja:
        shape_geo_dict, flag = self.get_shape_geometry()
        if not flag:
            return
        # pobranie środka:
        shape_type = self.canvas.cross_sections[self.selected_section_ID]["shape_type"]
        m_c = self.shape_definer[shape_type]["mass_center"](shape_geo_dict)
        if shape_type == "direct_values":
            x_c = 0.5
            z_c = 0.5
            ax = 0.2
            ar = ax/4
        else:
            ymax = max(np.max(line.get_ydata()) for line in self.AuxCanvas.axes.get_lines())
            xmax = max(np.max(line.get_xdata()) for line in self.AuxCanvas.axes.get_lines())
            x_c = m_c[0]/xmax
            z_c = m_c[1]/ymax
            ax = min(x_c, z_c)/2
            ar = ax/4
        # listy rysowań osi:
        x_ax = np.array([0, 0, ax]) + x_c
        z_ax = np.array([ax, 0, 0]) + z_c
        x_ar_z = np.array([-ar, 0, ar]) + x_c
        z_ar_z = np.array([ax - ar, ax, ax - ar]) + z_c
        x_ar_y = np.array([ax - ar, ax, ax - ar]) + x_c
        z_ar_y = np.array([ar, 0, -ar]) + z_c
        coords_comp = ar/16 * self.text_size
        Z_text_x = x_c - coords_comp
        Z_text_z = z_c + ax - 2 * ar
        Y_text_x = x_c + ax - 2 * ar
        Y_text_z = z_c - coords_comp

        drawn_axis = self.AuxCanvas.axes.plot(x_ax, z_ax,
                                            transform=self.AuxCanvas.axes.transAxes,
                                            linewidth=self.thinn_line,
                                            color=self.thinn_line_color,
                                            alpha=self.thinn_opacity)
        drawn_arrow_z = self.AuxCanvas.axes.plot(x_ar_z, z_ar_z,
                                            transform=self.AuxCanvas.axes.transAxes,
                                            linewidth=self.thinn_line,
                                            color=self.thinn_line_color,
                                            alpha=self.thinn_opacity)
        drawn_arrow_y = self.AuxCanvas.axes.plot(x_ar_y, z_ar_y,
                                                    transform=self.AuxCanvas.axes.transAxes,
                                                    linewidth=self.thinn_line,
                                                    color=self.thinn_line_color,
                                                    alpha=self.thinn_opacity)
        drawn_text_y = self.AuxCanvas.axes.text(Y_text_x, Y_text_z, "Y",
                                                    transform=self.AuxCanvas.axes.transAxes,
                                                    ha = "center", va = "center",
                                                    fontsize = self.text_size,
                                                    color=self.thinn_line_color,
                                                    alpha=self.thinn_opacity)
        drawn_text_z = self.AuxCanvas.axes.text(Z_text_x, Z_text_z, "Z",
                                                    transform=self.AuxCanvas.axes.transAxes,
                                                    ha = "center", va = "center",
                                                    fontsize = self.text_size,
                                                    color=self.thinn_line_color,
                                                    alpha=self.thinn_opacity)


        # Nazwy osi:
        drawn_axis_obj = [drawn_axis, drawn_arrow_z, drawn_arrow_y, drawn_text_z, drawn_text_y]
        return drawn_axis_obj

    # Funkcja zbiorcza rysowania axis_center:
    def manage_axis_center(self, disabled = False):
        # Usuwanie:
        if hasattr(self, "axis_center") and self.axis_center is not None:
            self.remove_vOBJ(self.axis_center)
            if disabled:
                return
        try:
            self.axis_center = self.draw_axis_center()
        except Exception as e:
            print(e)
        return
        
    # ========================================================  
    
    # Funkcja walidująca wartość:
    def validate_val(self, val, symbol_key = None, widget_to_highlight = None):
        try:
            absolute_val = float(val)
            if widget_to_highlight:
                widget_to_highlight.setStyleSheet("")
            return absolute_val, True
        except ValueError as e:
            if self.canvas.data_type == "symbolic":
                try:
                    absolute_val = sp.sympify(val, locals = self.canvas.LOCAL)
                    absolute_val = float(absolute_val.subs(self.canvas.symbol_substitutes[symbol_key]))
                    if widget_to_highlight:
                        widget_to_highlight.setStyleSheet("")
                    return absolute_val, True
                except Exception as e:
                    if widget_to_highlight:
                        widget_to_highlight.setStyleSheet("background-color: red; color: white")
                    return val, False
            if widget_to_highlight:
                widget_to_highlight.setStyleSheet("background-color: red; color: white")
            return val, False
    
    # Fnkcja ogólna budowania wiersza horyzontalnego:
    def create_property_row(self, parent_lt, label_text, widget_type = None, val = None, symbol_key = None, no_info = False, text_val = False, empty_check = True, add_stretch = True):
        def add_stretch_func(lt):
            if add_stretch:
                lt.addStretch()
        local_lt = QHBoxLayout()
        local_lt.addWidget(QLabel(f"{label_text}"))
        val_widget = widget_type
        val_widget.setStyleSheet("")
        local_lt.addWidget(val_widget)
        if no_info:
            val_widget.setText(f"value not found")
            val_widget.setStyleSheet("background-color: red; color: white")
            add_stretch_func(local_lt)
            parent_lt.addLayout(local_lt)
            return val_widget
        if text_val:
            if empty_check and isinstance(val, str) and val.strip() == "":
                val_widget.setText("(empty name: \"\")")
                val_widget.setStyleSheet("background-color: red; color: white")
            else:
                val_widget.setText(f"{val}")
            add_stretch_func(local_lt)
            parent_lt.addLayout(local_lt)
            return val_widget
        # Ustawienie wartości
        abs_val, validate_flag = self.validate_val(val, symbol_key, val_widget)
        
        if validate_flag:
            if round(abs_val, 4) == 0.0:
                print_abs = f"{abs_val:.3e}"
            else:
                print_abs = round(abs_val, 4)
            if self.canvas.data_type == "symbolic":
                val_widget.setText(f"{val}")
                local_lt.addWidget(QLabel(f"(absolute value ≈ {print_abs})"))
                add_stretch_func(local_lt)
                parent_lt.addLayout(local_lt)
                return val_widget
            else:
                val_widget.setText(f"{abs_val}")
                add_stretch_func(local_lt)
                parent_lt.addLayout(local_lt)
                return val_widget
        else:
            val_widget.setText(f"{abs_val}")
            local_lt.addWidget(QLabel(f"(couldnt convert to float)"))
            add_stretch_func(local_lt)
            parent_lt.addLayout(local_lt)
            return val_widget

    # Funkcja wzbogacona o fallback:
    def create_property_row_fallback(self, parent_lt, label_text, widget_type = None , val = None, symbol_key = None, no_info = False, text_val = False, blank_widget = False, add_stretch = True):
        if blank_widget:
            new_widget = self.create_property_row(parent_lt, label_text, widget_type, val = "", text_val = True, empty_check = False, add_stretch = add_stretch)
            return new_widget
        try:
            actual_val = val() if callable(val) else val # val podawane jest w formie lambdy aby ominąć sprawdzanie wartości na wejściu funkcji
            new_widget = self.create_property_row(parent_lt, label_text, widget_type , actual_val, symbol_key, no_info , text_val, add_stretch = add_stretch)
            return new_widget
        except Exception:
            new_widget = self.create_property_row(parent_lt, label_text, widget_type, no_info = True, add_stretch = add_stretch)
            return new_widget
            
    # Funkcja zbiorcza czyszczenia gui:
    def clear_GUI(self):
        # funkcja usuwająca widgety i layouty:
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item 
        # czyszczenie main layout:
        clear_layout(self.main_layout)
        return

    # "Narzędzie" do usuwania layoutów:
    def clear_layout(self, layout_to_clear):
        def clear_layout(layout):
            if layout is None:
                return  
            while layout.count():
                item = layout.takeAt(0) # takeAt(0) prawidłowo usuwa element z layoutu
                widget = item.widget()
                sub_layout = item.layout() 
                if widget:
                    widget.deleteLater()
                elif sub_layout:
                    clear_layout(sub_layout)
                else:
                    # Jeśli to nie widget i nie layout, to jest to np. QSpacerItem
                    del item 
        # czyszczenie main layout:
        clear_layout(layout_to_clear)
        layout_to_clear.deleteLater()
        
    # Funkcja zbiorcza budująca GUI:
    def build_GUI(self):
        # Czyszczenie
        self.clear_GUI()
        # Budowanie
        self.build_section_properties_GUI()
        self.build_section_status_GUI()
        self.build_modify_section_GUI()

    # Funkcja budująca GUI przeglądania parametrów:
    def build_section_properties_GUI(self):
        # Label
        main_label = QLabel("Search cross section parameters")
        main_label_font = main_label.font()
        main_label_font.setPointSize(12)
        main_label.setFont(main_label_font)
        self.main_layout.addWidget(main_label)
        # rozdzielenie na dwie sekcje GUI:
        main_h_props_lt = QHBoxLayout()
        self.main_layout.addLayout(main_h_props_lt)
        constant_lt = QVBoxLayout() # layout zawsze jest taki sam - wybieranie przekroju ect:
        main_h_props_lt.addLayout(constant_lt)
        adaptive_lt = QVBoxLayout() # layout zależny of przekroju, pokazuje kształt i wpisane wartości
        main_h_props_lt.addLayout(adaptive_lt)

        # layout lewy (constant) =====================
        # funkcja otwierająca dostępne przekroje:
        def get_section_list(sections_dict):
            sections_list = []
            for section_id in sections_dict.keys():
                sections_list.append(section_id)
            if self.selected_section_ID not in sections_list:
                self.selected_section_ID = next(iter(sections_list), None)
            return sections_list
        
        sections_list = get_section_list(self.canvas.cross_sections)
        # sekcja combobox:
        combobox_lt = QHBoxLayout()
        constant_lt.addLayout(combobox_lt)
        self.section_box = QComboBox()
        self.section_box.addItems(sections_list)
        self.section_box.setCurrentText(self.selected_section_ID)
        combobox_lt.addWidget(QLabel("Select cross section: "))
        combobox_lt.addWidget(self.section_box)
        section_directory_type = QLabel("")
        combobox_lt.addWidget(section_directory_type)
        try:
            if self.canvas.cross_sections[self.section_box.currentText()]["system_section"]:
                section_directory_type.setText("system cross section")
            else:
                section_directory_type.setText("user defined cross section")
        except Exception:
            section_directory_type.setText("user defined cross section")
        combobox_lt.addStretch()

        # Ustawienie wyboru:
        def change_selected_section():
            self.selected_section_ID = self.section_box.currentText()

        # Funkcja budująca layout lewy:
        def build_left_GUI():
            # sekcja ID:
            section_id_line = self.create_property_row(constant_lt, 
                                                       "Cross-section ID: ", 
                                                       widget_type = QLabel(""),  
                                                       val = self.selected_section_ID, 
                                                       text_val = True)
            # nazwa sekcji:
            section_name_line = self.create_property_row_fallback(constant_lt, 
                                                                  "Cross-section name: ", 
                                                                  widget_type = QLabel(""),  
                                                                  val = lambda: self.canvas.cross_sections[self.selected_section_ID]["name"], 
                                                                  text_val = True)
            # pole przekroju:
            section_area_line = self.create_property_row_fallback(constant_lt, 
                                                                  "Cross-sectional Area: ", 
                                                                  widget_type = QLabel(""),  
                                                                  val = lambda: self.canvas.cross_sections[self.selected_section_ID]["properties"]["area"], 
                                                                  symbol_key = "area")
            # maksymalne z:
            section_max_z_line = self.create_property_row_fallback(constant_lt, 
                                                                   "Extreme Fiber Distance: ", 
                                                                   widget_type = QLabel(""),  
                                                                   val = lambda: self.canvas.cross_sections[self.selected_section_ID]["properties"]["max_z"], 
                                                                   symbol_key = "length")
            # moment bezwład:
            section_inertia_y_line = self.create_property_row_fallback(constant_lt, 
                                                                       "Moment of Inertia (I_y): ", 
                                                                       widget_type = QLabel(""),  
                                                                       val = lambda: self.canvas.cross_sections[self.selected_section_ID]["properties"]["inertia_y"], 
                                                                       symbol_key = "inertia_y")
            # moment statyczny:
            section_static_y_line = self.create_property_row_fallback(constant_lt, 
                                                                      "Static Moment for Shear: ", 
                                                                      widget_type = QLabel(""),  
                                                                      val = lambda: self.canvas.cross_sections[self.selected_section_ID]["properties"]["zuravsky_static_y"], 
                                                                      symbol_key = "zuravsky_static_y")
            # szerokość ścinania:
            shear_width_line = self.create_property_row_fallback(constant_lt,
                                                                 "Shear Width (t_c): ",
                                                                 widget_type = QLabel(""),
                                                                 val = lambda: self.canvas.cross_sections[self.selected_section_ID]["properties"]["shear_width"],
                                                                 symbol_key = "length")
            
            shear_correction_factor_line = self.create_property_row_fallback(constant_lt,
                                                                             "Shear Correction (β): ",
                                                                             widget_type = QLabel(""),
                                                                             val = lambda: self.canvas.cross_sections[self.selected_section_ID]["properties"]["shear_correction_factor"],
                                                                             symbol_key = "shear_correction_factor")
            
            constant_lt.addStretch()
            
        # layout prawy:
        adaptive_lt.addStretch()
        adaptive_label = QLabel("Shape parameters: ")
        adaptive_lt.addWidget(adaptive_label)
        adaptive_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Funkcja budująca layout:
        def build_right_GUI():
            try:
                shape_type = self.canvas.cross_sections[self.selected_section_ID]["shape_type"]
                if shape_type not in self.shape_definer:
                    shape_widget = QLabel("shape not recognized")
                    shape_widget.setStyleSheet("background-color: red; color: white")
                    adaptive_lt.addWidget(shape_widget)
                    adaptive_lt.addStretch()
                    return
            except Exception:
                shape_widget = QLabel("shape not recognized")
                shape_widget.setStyleSheet("background-color: red; color: white")
                adaptive_lt.addWidget(shape_widget)
                return
            # jeżeli kształt jest w bazie to bierzemy parametry:
            self.create_property_row(adaptive_lt, label_text = "shape type: ", widget_type = QLabel(""), val = shape_type, text_val = True)
            for prop_name in self.shape_definer[shape_type]["inputs"]:
                try:
                    subs_key = "length"
                    # Warunkowość aby podstawianie zadziałało dla przypadku direct values
                    if shape_type == "direct_values" and prop_name in ["area", "max_z", "inertia_y", "zuravsky_static_y", "shear_width", "shear_correction_factor"]:
                        if prop_name in {"max_z", "shear_width"}:
                            subs_key = "length"
                        else:
                            subs_key = prop_name    
                    self.create_property_row(adaptive_lt, label_text = f"{prop_name}: ", widget_type = QLabel(""), val = self.canvas.cross_sections[self.selected_section_ID]["shape_parameters"][prop_name], symbol_key = subs_key)
                except Exception:
                    self.create_property_row(adaptive_lt, label_text = f"{prop_name}: ", widget_type = QLabel(""), no_info = True)
              
            return
            
        # Wywołanie funkcji
        build_left_GUI()
        build_right_GUI()
        
        # Wywołanie przy zmianie wyboru sekcji:
        self.section_box.currentTextChanged.connect(change_selected_section)
        self.section_box.currentTextChanged.connect(self.build_GUI)

        # Wywołanie funkcji rysującej przy zmienie wyboru:
        self.section_box.currentTextChanged.connect(self.draw_section)

        return

    # Seckcja zmiany typu GUI z edit na add:
    def build_section_status_GUI(self):
        status_lt = QHBoxLayout()
        self.main_layout.addLayout(status_lt)
        edit_btn = QPushButton("Edit selected cross section")
        add_btn = QPushButton("Add new cross section")
        status_lt.addWidget(edit_btn)
        status_lt.addWidget(add_btn)
        
        # funkcja zmiany przycisków
        def set_selection_visual():
            if self.modify_gui_status == "edit":
                edit_btn.setStyleSheet("background-color: green; color: white")
                edit_btn.setEnabled(False)
                add_btn.setStyleSheet("")
                add_btn.setEnabled(True)
            else:
                add_btn.setStyleSheet("background-color: green; color: white")
                add_btn.setEnabled(False)
                edit_btn.setStyleSheet("")
                edit_btn.setEnabled(True)

        # wywołanie funkcji za pierwszym tworzeniem GUI:
        set_selection_visual()

        # Funkcja zmiany statusu:
        def switch_status(status):
           self.modify_gui_status = status
           self.build_GUI()
        
        # Połączenie z przyciskami:
        edit_btn.clicked.connect(lambda: switch_status(status = "edit"))
        add_btn.clicked.connect(lambda: switch_status(status = "add"))
    
    # Fukcja budująca GUI edycji:
    def build_modify_section_GUI(self):
        # funkcja skracająca długość kodu, warunkowe przypisywanie wartości zmiennej:
        def status_dependent(edit_val = None, add_val = None):
            if self.modify_gui_status == "edit":
                return edit_val
            else:
                return add_val
        
        # label
        main_label_text = status_dependent(f"Edit \"{self.selected_section_ID}\" cross section:", "Add new cross section")
        main_label = QLabel(f"{main_label_text}")
        main_label_font = main_label.font()
        main_label_font.setPointSize(12)
        main_label.setFont(main_label_font)
        self.main_layout.addWidget(main_label)
        
        # zatrzymanie przed edycją sekcji systemowej
        try:
            if self.canvas.cross_sections[self.selected_section_ID]["system_section"] and self.modify_gui_status == "edit":
                main_label.setText(f"Cannot edit system cross sections")
                return
            else:
                pass
        except Exception:
            pass

        # layouty edycji:
        main_h_layout = QHBoxLayout()
        self.main_layout.addLayout(main_h_layout)
        left_lt = QVBoxLayout()
        right_lt = QVBoxLayout()
        main_h_layout.addLayout(left_lt)
        main_h_layout.addLayout(right_lt)

        # Sekcja zmiany nazwy i id
        shape_box_lt = QHBoxLayout()
        left_lt.addLayout(shape_box_lt)
        self.shape_type_box = QComboBox()
        self.shape_type_box.addItems(self.shape_type_list)
        shape_box_lt.addWidget(QLabel("Shape type: "))
        shape_box_lt.addWidget(self.shape_type_box)
        # Ustawienie odpowiedniego wyboru
        try:
            loaded_shape = status_dependent(self.canvas.cross_sections[self.selected_section_ID]["shape_type"], next(iter(self.shape_type_list)))
            if loaded_shape not in self.shape_type_list:
                loaded_shape = next(iter(self.shape_type_list))
        except Exception:
            loaded_shape = next(iter(self.shape_type_list))
        self.shape_type_box.setCurrentText(loaded_shape) 

        shape_box_lt.addStretch()
        # nazwa i id:
        blank_setting = status_dependent(False, True)
        section_id_label = status_dependent("Modify section ID", "Section ID")
        self.section_id_line = self.create_property_row_fallback(left_lt, f"{section_id_label}: ", widget_type = QLineEdit(""), 
                                                                 val = lambda: self.selected_section_ID,  
                                                                 text_val = True, blank_widget = blank_setting)
        self.section_name_line = self.create_property_row_fallback(left_lt, "Section name: ", widget_type = QLineEdit(""), 
                                                                   val = lambda: self.canvas.cross_sections[self.selected_section_ID]["name"],  
                                                                   text_val = True, blank_widget = blank_setting)

        # sekcja dobierania symbolu
        # Funkcja budująca combobox:
        def make_combobox_lt(parent_lt, label = "", sym_dict = {}, current_sub = None):
            # tworzenie combobox:
            local_lt = QHBoxLayout()
            local_lt.addWidget(QLabel(f"{label}"))
            parent_lt.addLayout(local_lt)
            # Tworzenie listy:
            symbols_list = ["No symbol"]
            # Pobieranie słownika z fallbackiem
            try:
                actual_dict = sym_dict() if callable(sym_dict) else sym_dict
            except Exception:
                actual_dict = {}

            for symbol in actual_dict.keys():
                symbols_list.append(symbol)
            # widget:
            new_box = QComboBox()
            new_box.addItems(symbols_list)
            local_lt.addWidget(new_box)
            local_lt.addStretch()

            # Umieszczenie odpowiedniego symbolu:
            if self.modify_gui_status == "add":
                new_box.setCurrentText("No symbol")
                return new_box
            # Próba umieszczenia odpowiedniego symbolu jeżeli jest w słowniku:
            try:
                actual_sub = current_sub() if callable(current_sub) else current_sub
                if actual_sub not in actual_dict:
                    actual_sub = "No symbol"
            except Exception:
                actual_sub = "No symbol"

            # ustawienie symbolu w box:
            new_box.setCurrentText(actual_sub)
            return new_box

        # Funkcja budująca GUI symboli:
        def build_symbol_GUI():
            if hasattr(self, "symbol_v_lt") and self.symbol_v_lt is not None:
                self.clear_layout(self.symbol_v_lt)

            self.symbol_v_lt = QVBoxLayout()
            left_lt.addLayout(self.symbol_v_lt)
            if self.canvas.data_type == "symbolic" and self.shape_type_box.currentText() != "direct_values":
                self.area_symbol_box = make_combobox_lt(self.symbol_v_lt, 
                                                        label = "Area symbol: ", 
                                                        sym_dict = lambda: self.canvas.symbol_substitutes["area"], 
                                                        current_sub = lambda: self.canvas.cross_sections[self.selected_section_ID]["property_subs"]["area"])
                self.max_z_symbol_box = make_combobox_lt(self.symbol_v_lt, 
                                                        label = "Extreme Fiber Distance symbol: ", 
                                                        sym_dict = lambda: self.canvas.symbol_substitutes["length"], 
                                                        current_sub = lambda: self.canvas.cross_sections[self.selected_section_ID]["property_subs"]["max_z"])
                self.inertia_y_symbol_box = make_combobox_lt(self.symbol_v_lt, 
                                                            label = "Moment of Inertia symbol: ", 
                                                            sym_dict = lambda: self.canvas.symbol_substitutes["inertia_y"], 
                                                            current_sub = lambda: self.canvas.cross_sections[self.selected_section_ID]["property_subs"]["inertia_y"])
                self.zuravsky_static_y_symbol_box = make_combobox_lt(self.symbol_v_lt, 
                                                                    label = "Static Moment for Shear symbol: ", 
                                                                    sym_dict = lambda: self.canvas.symbol_substitutes["zuravsky_static_y"], 
                                                                    current_sub = lambda: self.canvas.cross_sections[self.selected_section_ID]["property_subs"]["zuravsky_static_y"])
                self.shear_width_symbol_box = make_combobox_lt(self.symbol_v_lt, 
                                                                     label = "Shear Width (t_c): ", 
                                                                     sym_dict = lambda: self.canvas.symbol_substitutes["length"], 
                                                                     current_sub = lambda: self.canvas.cross_sections[self.selected_section_ID]["property_subs"]["shear_width"])
                self.shear_correction_factor_symbol_box = make_combobox_lt(self.symbol_v_lt, 
                                                                     label = "Shear Correction (β): ", 
                                                                     sym_dict = lambda: self.canvas.symbol_substitutes["shear_correction_factor"], 
                                                                     current_sub = lambda: self.canvas.cross_sections[self.selected_section_ID]["property_subs"]["shear_correction_factor"])
                # stworzenie combobox dokładności:
                round_lt = QHBoxLayout()
                self.symbol_v_lt.addLayout(round_lt)
                round_lt.addWidget(QLabel("Round symbol ratio to:"))
                self.symbol_round_ratio_box = QComboBox()
                self.symbol_round_ratio_box.addItems(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])
                self.symbol_round_ratio_box.setCurrentText("6")
                round_lt.addWidget(self.symbol_round_ratio_box)
                round_lt.addStretch()
                
        # Wywołanie za pierwszym razem:
        build_symbol_GUI()
        # Łączenie zmiany kształtu z budowaniem GUI symboli:
        self.shape_type_box.currentTextChanged.connect(build_symbol_GUI)   

        # Budowanie layoutu parametrów przekroju:
        right_label = QLabel(f"{self.shape_type_box.currentText()} shape parameters:")
        right_lt.addWidget(right_label)

        # ZJEBANA FUNKCJA TWORZENIA GUI parametrów kształtu i przycisków, jebać że niewydajne chuj mnie to już
        def build_shape_btns_GUI():
            if hasattr(self, "shape_v_lt") and self.shape_v_lt is not None:
                self.clear_layout(self.shape_v_lt)
            self.shape_v_lt = QVBoxLayout()
            right_lt.addLayout(self.shape_v_lt)
            blank_setting = status_dependent(False, True) # Ustawienie flagi pustego tekstu
            # Ustawienie słownika edycji:
            self.shape_params_line_dict = {}
            # pobranie listy iterowania:
            iteration_list = self.shape_definer[self.shape_type_box.currentText()]["inputs"]
            # pętla tworząca GUI:
            for param in iteration_list:
                if self.shape_type_box.currentText() == "direct_values":
                    if param in {"max_z", "shear_width"}:
                        subs_key = "length"
                    else:
                        subs_key = param
                else:
                    subs_key = "length"
                self.shape_params_line_dict[param] = self.create_property_row_fallback(parent_lt = self.shape_v_lt,
                                                                                       label_text = f"{param}: ",
                                                                                       widget_type = QLineEdit(""),
                                                                                       val = lambda: self.canvas.cross_sections[self.selected_section_ID]["shape_parameters"][param],
                                                                                       symbol_key = subs_key,
                                                                                       blank_widget = blank_setting)
            self.shape_v_lt.addStretch()
            # Dodanie przycisków:
            apply_btn_text = status_dependent("Apply changes", "Add new section")
            self.apply_changes_btn = QPushButton(f"{apply_btn_text}")
            self.delete_btn = QPushButton("Delete section")
            self.delete_btn.setStyleSheet("background-color: red; color: white")
            self.shape_v_lt.addWidget(self.apply_changes_btn)
            if self.modify_gui_status == "edit":
                self.shape_v_lt.addWidget(self.delete_btn)
                self.delete_btn.clicked.connect(lambda: self.apply_changes(dlete_only = True))
                self.apply_changes_btn.clicked.connect(lambda: self.apply_changes(modify = True))
            else:
                self.apply_changes_btn.clicked.connect(lambda: self.apply_changes(add_new = True))
            
        # Wywołanie funkcji za pierwszym uruchiomieniem:
        build_shape_btns_GUI()
        # Wysołanie przy zmianie kształtu:
        self.shape_type_box.currentTextChanged.connect(build_shape_btns_GUI)

        return

    # Funkcja zapisywanie zmian:
    def apply_changes(self, modify = False, add_new = False, dlete_only = False):
        # Ogólna funkcja QMessageBox informująca o problemach:
        def MessageBox(info = "", widget_to_highlight = None):
            QMessageBox.warning(self,
                                "Invalid cross section data",
                                f"{info}")
            if widget_to_highlight:
                widget_to_highlight.setStyleSheet("background-color: red; color: white")
            return
        
        # Pobranie podstawowych danych (id stare)
        old_id = self.selected_section_ID
        # jeżeli jest to tylko usunięcie
        if dlete_only:
            del self.canvas.cross_sections[old_id]
            self.build_GUI()
            print(self.selected_section_ID)
            return
        # Walidujemy i alokujemy wprowadzone dane:
        # nowe id:
        new_id = self.section_id_line.text().strip()
        if new_id == "":
            MessageBox("Cross section ID was not provided", self.section_id_line)
            return
        elif new_id != old_id and new_id in self.canvas.cross_sections:
            MessageBox(f"Cross section ID {new_id} is already present in cross sections library", self.section_id_line)
            return
        else:
            self.section_id_line.setStyleSheet("")

        # nazwa, nie potrzebuje walidacji:
        new_name = self.section_name_line.text().strip()
        if new_name == "":
            new_name = "section name not assigned"

        # kształt - nie potrzebuje walidacji gdyż jest to combobox który ma fallbacki wcześniej:
        new_shape = self.shape_type_box.currentText()

        # Sekcja dotycząca symboli, tylko dla siatek symbolicznych i kształtów nie będących "direct_values":
        if new_shape != "direct_values" and self.canvas.data_type == "symbolic":
            cross_param_symbols = {
                "area": self.area_symbol_box.currentText(),
                "max_z": self.max_z_symbol_box.currentText(),
                "inertia_y": self.inertia_y_symbol_box.currentText(),
                "zuravsky_static_y": self.zuravsky_static_y_symbol_box.currentText(),
                "shear_width": self.shear_width_symbol_box.currentText(),
                "shear_correction_factor": self.shear_correction_factor_symbol_box.currentText()
            }
        # Jeśli nie jest to symboliczna siatkia / jest to direct values przypisano wartość "No symbol" aby nadal kożystać później z tego samego algorytmu liczenia wartości końcowej
        else:
              cross_param_symbols = {
                            "area": "No symbol",
                            "max_z": "No symbol",
                            "inertia_y": "No symbol",
                            "zuravsky_static_y": "No symbol",
                            "shear_width": "No symbol",
                            "shear_correction_factor": "No symbol"
                        }

        # Pobieranie surowych parametrów kształtu z walidacją:
        shape_param_vals = {}
        shape_param_str = {}
        cross_params = {"area": None,
                        "max_z": None,
                        "inertia_y": None,
                        "zuravsky_static_y": None,
                        "shear_width": None,
                        "shear_correction_factor": None}
        cross_param_val = {}
        convertion_log = []
        val_flag = True
        for param, line in self.shape_params_line_dict.items():
            param_val = line.text().strip()
            # walidacja:
            if not (new_shape == "direct_values" and param not in {"max_z", "shear_width"}):
                symbol_sub_key = "length"
            else:
                symbol_sub_key = param 
            absolute_val, val_flag = self.validate_val(val = param_val, symbol_key = symbol_sub_key, widget_to_highlight = line)
            shape_param_vals[param] = absolute_val
            shape_param_str[param] = param_val

            if not val_flag:
                convertion_log.append(f"Couldnt convert shape parameter \"{param}\", value: \"{param_val}\" to float")
            else:
                if absolute_val < 0:
                    shape_param_str[param] = None
                    convertion_log.append("Shape parameter values cannot be negative:\n"
                                          f"\"{param}\", entered value: \"{param_val}\" converted: {absolute_val}")

        # Jeśli nieudało się przekonwertować parametrów:
        if convertion_log:
            error_dialog = ListReportLog(self, self.canvas, title = "Convertion error", label_text = "Failed to convert below values", 
                                         display_list = convertion_log, minimum_width = 450)
            error_dialog.exec()
            cross_param_val = cross_params.copy()
        # Wyznaczenie parametrów:
        else:
            if new_shape != "direct_values" and self.canvas.data_type == "symbolic":
                # pobieranie stopnia zaokrąglenia:
                round_ratio = int(self.symbol_round_ratio_box.currentText())
                for param_key in cross_params.keys():
                    param_val = self.shape_definer[new_shape][param_key](shape_param_vals)
                    # Dzielenie przez wartość symbolu:
                    if cross_param_symbols[param_key] != "No symbol":
                        symbol_type = "length" if param_key in {"max_z", "shear_width"} else param_key
                        symbol_val = self.canvas.symbol_substitutes[symbol_type][cross_param_symbols[param_key]]
                        # wyznaczenie dokładniejszej wartości z Sympy
                        sym_rational = sp.Rational(str(symbol_val))
                        param_rational = sp.Rational(str(param_val))
                        param_val = param_rational / sym_rational
                        param_val = sp.N(param_val, round_ratio)
                        # ostateczna wartość:
                        param_val = f"{param_val}*{cross_param_symbols[param_key]}"
                    # przypisanie do słownika:
                    cross_param_val[param_key] = param_val
            elif self.canvas.data_type == "symbolic":
                cross_param_val = copy.deepcopy(shape_param_str)
            else:
                for param_key in cross_params.keys():
                    cross_param_val[param_key] = self.shape_definer[new_shape][param_key](shape_param_vals)

        # Po pobraniu wszystkich danych należy dokonać zapisu:
        # funkcja zapisująca:
        def save_new_section():
            # Większość słownika można wypełnić od razu:
            self.canvas.cross_sections[new_id] = {
                "name": new_name,
                "shape_type": new_shape,
                "shape_parameters": {},
                "properties":{
                    "area": cross_param_val["area"],
                    "inertia_y": cross_param_val["inertia_y"],
                    "zuravsky_static_y": cross_param_val["zuravsky_static_y"],
                    "max_z": cross_param_val["max_z"],
                    "shear_width": cross_param_val["shear_width"],
                    "shear_correction_factor": cross_param_val["shear_correction_factor"]
                }
            }
            # Pętla wypełnienia parametrów kształtu przekroju:
            if self.canvas.data_type == "symbolic":
                for shape_param, param_val in shape_param_str.items():
                    self.canvas.cross_sections[new_id]["shape_parameters"][shape_param] = param_val
            else:
                for shape_param, param_val in shape_param_vals.items():
                    self.canvas.cross_sections[new_id]["shape_parameters"][shape_param] = param_val
            # Jeśli jest to siatka symboliczna to na potrzeby meshera wypełnia się wybranymi substytami:
            if self.canvas.data_type == "symbolic":
                self.canvas.cross_sections[new_id]["property_subs"] = {}
                for property, prop_sub in cross_param_symbols.items():
                    self.canvas.cross_sections[new_id]["property_subs"][property] = prop_sub
        
        if modify:
            # Przy edytowaniu należy usunąć starą sekcję:
            del self.canvas.cross_sections[old_id]
            # zapisanie do słownika:
            save_new_section()
            # przypisanie nowego wyboru sekcji:
            self.selected_section_ID = new_id
            # odświerzenie GUI:
            self.build_GUI()
            self.draw_section()
            return
        if add_new:
            save_new_section()
            # przypisanie nowego wyboru sekcji:
            self.selected_section_ID = new_id
            # odświerzenie GUI:
            self.build_GUI()
            self.draw_section()
            return

    # Otwarcie dialogu symboli:
    def open_symbol_manager(self):
        dialog = SymbolSubstitutesDialog(self, self.canvas)
        if dialog.exec() == QDialog.Accepted:
            self.build_GUI()
            self.draw_section()
    
    # Zamykanie dialogu
    def close_dialog(self):
        self.accept()
        
# ========================================
# Klasa dialogu pomocniczego canvasa:
# ======================================== EDYTOR SIATKI
class AuxilaryCanvas(FigureCanvas):
    def __init__(self, parent = None, width = 3, height = 3, dpi = 100):
        self.fig = Figure(figsize = (width, height), dpi = dpi)
        super().__init__(self.fig)          
        self.setParent(parent)              
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.axes.set_aspect("equal")
        self.axes.clear()

# ========================================
# Klasa dialogu Logów rysowania siatki
# ======================================== EDYTOR SIATKI
class ListReportLog(QDialog):
    def __init__(self, parent = None, canvas = None, title = "No title", label_text = "Report:",  display_list = "No list", minimum_width = 400, minimum_height = 400):
        super().__init__(parent)
        self.canvas = canvas
        # Ustawienia interakcji:
        self.setModal(False)
        self.setWindowTitle(title)
        self.setMinimumWidth(minimum_width)
        self.setMinimumHeight(minimum_height)
        # Layouty:
        self.main_layout = QVBoxLayout(self) # Główny layout, po to aby przyciski dolne były zawsze w tym samym miejscu
        # Dodawanie Listy:
        label = QLabel(f"{label_text}")
        self.main_layout.addWidget(label)
        Log_list = QListWidget()
        Log_list.addItems(display_list)
        self.main_layout.addWidget(Log_list)

        # Dolna sekcja:
        close_btn = QPushButton("close")
        self.main_layout.addWidget(close_btn)
        close_btn.clicked.connect(self.close_dialog)

    def close_dialog(self):
        self.accept()

# ========================================
# Klasa rysowania siatki
# ======================================== EDYTOR SIATKI + POST PROCESSOR + EDYTOR OBCIĄŻEŃ
class MeshCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # 1. Tworzymy główną "kartkę papieru" (Figure)
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        # Dodajemy układ współrzędnych (Axes) do kartki
        # Wartość 111 oznacza: siatka 1x1, i wybieramy 1. wykres
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.MainWindow = parent

# ================================================================
# Inicializacja słowników siatki
# ================================================================

        # Flaga typu siatki:
        self.data_type = None

        # Słownik symboli:
        self.symbol_substitutes = {}
        
        # Słownik symboli specialnych:
        # Istotne gówno - jak ktoś nazwie symbol I lub E to obiekt sympy nie potraktuje tego jako urojona i eulera
        self.LOCAL = sympy_LOCAL

        # Słownik prostego rysowania siatki - dla managera symboli:
        # Funkcja rysująca elementy jako połączone linie, tylko dla edytora obciążeń:
        self.load_mesh_visual_settings = {
            "load_scale": 2000,
            "loads_color": "gray",
            "loads_transparency": 1.0,
            "thicc_line": 2,
            "thinn_line" : 0.75,
            "loads_linestyle": "-",
            "region_transparency": 0.5,
            "text_size" : 6,
            "text_color": "black",
            "text_transparency": 1.0,
            "textBOX_transparency": 0.6,
            "selection_thickness" : 8,
            "selection_color" : "green",
            "selection_transparency" : 0.5,
            "simplified_element_linestyle" : "-",
            "simplified_element_linewidth" : 0.75,
            "simplified_mesh_color" : "black",
            "simplified_mesh_transparency" : 0.5,
            "simplified_node_size" : 6.0,
            "draw_labels": "Show",
            "simplified_label_size": 5.0,
            "node_marker" : {
                            'Free': 'o',                    
                            'fix_rot': 'P',                 
                            'pinned_support': '^',          
                            'roller_support_fixX': '|',     
                            'roller_support_fixZ': '_',     
                            'FIXED_support': 's',           
                            'rollerFIX_support_fixX': 'd',  
                            'rollerFIX_support_fixZ': 'D',  
                            'unknown_support': 'X',         
                        }
        }
        
        # Słownik przekrojów:
        self.system_sections = {
                            'S10x10': {
                            "name": "Beam_10x10cm",
                            "shape_type": "rectangle",
                            "shape_parameters": { "width": 0.1, "height": 0.1 },
                            "system_section" : True,
                            "properties": {
                                "area": 0.01,
                                "inertia_y": 8.33e-6,
                                "zuravsky_static_y": 1.67e-4,
                                "max_z": 0.05,
                                "shear_width": 0.1,
                                "shear_correction_factor": 0.8333333333333333333
                                        }
                                    }
                            }

        self.cross_sections = {}
        # Słowniki materiałów:
        self.system_materials = {
                # --- STEELS ---
                "steel_S235": {
                    "name": "Structural steel S235",
                    "youngs_modulus": 210e9,       # 210 GPa
                    "poissons_ratio": 0.30,
                    "density": 7850,                # kg/m³
                },
                "steel_S355": {
                    "name": "Structural steel S355",
                    "youngs_modulus": 210e9,       # 210 GPa
                    "poissons_ratio": 0.30,
                    "density": 7850,                # kg/m³
                },
                "steel_304": {
                    "name": "Stainless steel 304 (AISI 304)",
                    "youngs_modulus": 200e9,       # 200 GPa
                    "poissons_ratio": 0.29,
                    "density": 7910,                # kg/m³
                },

                # --- LIGHT METALS ---
                "aluminium_6061": {
                    "name": "Aluminium 6061-T6",
                    "youngs_modulus": 69e9,        # 69 GPa
                    "poissons_ratio": 0.33,
                    "density": 2700,                # kg/m³
                },
                "duralumin": {
                    "name": "Duralumin (dural)",
                    "youngs_modulus": 62.43e9,     # 62.43 GPa
                    "poissons_ratio": 0.35,
                    "density": 2787,                # kg/m³
                },

                # --- WOOD ---
                "spruce_wood": {
                    "name": "Spruce wood (along grain)",
                    "youngs_modulus": 11.5e9,      # 11.5 GPa
                    "poissons_ratio": 0.37,
                    "density": 450,                 # kg/m³
                },

                # --- CONCRETE ---
                "concrete": {
                    "name": "Structural concrete",
                    "youngs_modulus": 30e9,        # 30 GPa
                    "poissons_ratio": 0.20,
                    "density": 2400,                # kg/m³
                },

                # --- POLYMERS / PLASTICS ---
                "abs_plastic": {
                    "name": "ABS (Acrylonitrile Butadiene Styrene)",
                    "youngs_modulus": 2.3e9,       # 2.3 GPa
                    "poissons_ratio": 0.35,
                    "density": 1040,                # kg/m³
                },
                "polyamide_pa6": {
                    "name": "Polyamide PA6 (Nylon 6)",
                    "youngs_modulus": 2.8e9,       # 2.8 GPa
                    "poissons_ratio": 0.36,
                    "density": 1150,                # kg/m³
                },
                "pom": {
                    "name": "POM (Polyoxymethylene)",
                    "youngs_modulus": 2.9e9,       # 2.9 GPa
                    "poissons_ratio": 0.37,
                    "density": 1420,                # kg/m³
                }
            }
      
        # Słownik domyślnych parametrów labelu węzła
        self.default_node_label_params = {
                'x_offset': 0.05,
                'z_offset': 0.05,
                'font_size': 8,
                'color' : "black",
                'transparency' : 1
        }
        
        # słownik domyślnych parametrów labelu elementu
        self.default_element_label_params = {
                'x_offset': 0.1,
                'z_offset': 0.1,
                'font_size': 6,
                'color' : "grey",
                'transparency' : 1
                }

        # Słownik domyślnych ustawień canvasa
        self.canvas_default_settings = {
            'set_aspect' : "equal",
            'margins' : 0.2,
            'grid(True/False)' : True,
            'grid_linestyle' : '--',
            'grid_alpha' : 0.5,
            'thinn_line' : 0.75,
            'thicc_line' : 1.5
        }
        
        # Słownik typów elementów:
        self.element_type = {
                            '2N4DOF_EB': {
                                'function': self.draw_beam,
                                'v_params': {
                                    'aspect_ratio': 20,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'green',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N4DOF_T_EX': {
                                'function': self.draw_beam,
                                'v_params': {
                                    'aspect_ratio': 20,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'green',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N4DOF_T_FI': {
                                'function': self.draw_beam,
                                'v_params': {
                                    'aspect_ratio': 20,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'green',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N4DOF_T_RI': {
                                'function': self.draw_beam,
                                'v_params': {
                                    'aspect_ratio': 20,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'green',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N6DOF_EB_Q': {
                                'function': self.draw_beam,
                                'v_params': {
                                    'aspect_ratio': 20,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'green',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N2DOF_Bar': {
                                'function': self.draw_rod,
                                'v_params': {
                                    'aspect_ratio': 30,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'blue',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            'Spring': {
                                'function': self.draw_spring,
                                'v_params': {
                                    'aspect_ratio': 30,
                                    'coil_num': 10,
                                    'spring_lead': 1,
                                    'start_offset': 0.5,
                                    'element_line_type': '-.',
                                    'element_color': 'black',
                                    'transparency': 1
                                }
                            },
                            '2N4DOF_Truss': {
                                'function': self.draw_rod,
                                'v_params': {
                                    'aspect_ratio': 30,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'blue',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            'Spring_2D': {
                                'function': self.draw_spring,
                                'v_params': {
                                    'aspect_ratio': 30,
                                    'coil_num': 10,
                                    'spring_lead': 1,
                                    'start_offset': 0.5,
                                    'element_line_type': '-.',
                                    'element_color': 'black',
                                    'transparency': 1
                                }
                            },
                            '2N6DOF_EB': {
                                'function': self.draw_frameEl,
                                'v_params': {
                                    'aspect_ratio': 15,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'blue',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N6DOF_T_EX': {
                                'function': self.draw_frameEl,
                                'v_params': {
                                    'aspect_ratio': 15,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'blue',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N6DOF_T_FI': {
                                'function': self.draw_frameEl,
                                'v_params': {
                                    'aspect_ratio': 15,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'blue',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N6DOF_T_RI': {
                                'function': self.draw_frameEl,
                                'v_params': {
                                    'aspect_ratio': 15,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'blue',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            '2N8DOF_EB_Q': {
                                'function': self.draw_frameEl,
                                'v_params': {
                                    'aspect_ratio': 15,
                                    'real_aspect_ratio': "True",
                                    'start_offset': 0.5,
                                    'element_line_type': '-',
                                    'element_color': 'blue',
                                    'transparency': 1,
                                    'symbol_line_type': '-',
                                    'symbol_color': 'green',
                                    'symbol_transparency': 0.75,
                                }
                            },
                            'unknown_element': {
                                'function': self.draw_unknown_element,
                                'v_params': {
                                    'element_line_type': '--',
                                    'element_color': 'red',
                                    'transparency': 0.5,
                                    'symbol_color': 'red',
                                    'symbol_size': 8,
                                    'symbol_offset_x': 0.025,
                                    'symbol_offset_z': 0.025,
                                    'symbol_transparency': 1,
                                }
                            }
                        }
        
        # Słownik podpór w zależności od uwiązania:
        self.support_type = {
            'Free' : {
                "constraint": {"UX": True, "UZ": True, "RY": True}, 
                "function" : self.draw_node_mark,
                "v_params": {
                    "marker_shape" : 'o',
                    "marker_size" : 4,
                    "marker_color": 'green',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'fix_rot' : {
                "constraint": {"UX": True, "UZ": True, "RY": False}, 
                "function" : self.draw_node_fix_rot,
                "v_params": {
                    "marker_shape" : 's',
                    "marker_size" : 6,
                    "marker_color": 'gray',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'pinned_support' : {
                "constraint": {"UX": False, "UZ": False, "RY": True},
                "function" : self.draw_pinned_support,
                "v_params" : {
                    "rotation_angle" : 0,
                    "support_width" : 0.1,
                    "support_height" : 0.075,
                    "hatch_angle" : 60,
                    "hatch_density" : 10,
                    "support_color": 'blue',
                    "marker_shape" : 'o',
                    "marker_size" : 6,
                    "marker_color": 'blue',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'roller_support_fixX' : {
                "constraint": {"UX": False, "UZ": True, "RY": True},
                "function" : self.draw_roller_support,
                "v_params" : {
                    "rotation_angle" : 90,
                    "support_width" : 0.1,
                    "support_height" : 0.075,
                    "hatch_angle" : 60,
                    "hatch_density" : 10,
                    "gap" : 0.01,
                    "support_color": 'blue',
                    "marker_shape" : 'o',
                    "marker_size" : 6,
                    "marker_color": 'blue',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'roller_support_fixZ' : {
                "constraint": {"UX": True, "UZ": False, "RY": True},
                "function" : self.draw_roller_support,
                "v_params" : {
                    "rotation_angle" : 0,
                    "support_width" : 0.1,
                    "support_height" : 0.075,
                    "hatch_angle" : 60,
                    "hatch_density" : 10,
                    "gap" : 0.01,
                    "support_color": 'blue',
                    "marker_shape" : 'o',
                    "marker_size" : 6,
                    "marker_color": 'blue',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'FIXED_support' : {
                "constraint": {"UX": False, "UZ": False, "RY": False},
                "function" : self.draw_FIXED_support,
                "v_params" : {
                    "rotation_angle" : 0,
                    "support_width" : 0.1,
                    "support_height" : 0.075,
                    "hatch_angle" : 60,
                    "hatch_density" : 10,
                    "support_color": 'blue',
                    "marker_shape" : 's',
                    "marker_size" : 6,
                    "marker_color": 'blue',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'rollerFIX_support_fixX' : {
                "constraint": {"UX": False, "UZ": True, "RY": False}, 
                "function" : self.draw_rollerFIX_support,
                "v_params" : {
                    "rotation_angle" : 90,
                    "support_width" : 0.1,
                    "support_height" : 0.075,
                    "hatch_angle" : 60,
                    "hatch_density" : 10,
                    "gap" : 0.01,
                    "support_color": 'blue',
                    "marker_shape" : 's',
                    "marker_size" : 6,
                    "marker_color": 'blue',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'rollerFIX_support_fixZ' : {
                "constraint": {"UX": True, "UZ": False, "RY": False},
                "function" : self.draw_rollerFIX_support,
                "v_params" : {
                    "rotation_angle" : 0,
                    "support_width" : 0.1,
                    "support_height" : 0.075,
                    "hatch_angle" : 60,
                    "hatch_density" : 10,
                    "gap" : 0.01,
                    "support_color": 'blue',
                    "marker_shape" : 's',
                    "marker_size" : 6,
                    "marker_color": 'blue',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
                },
            'unknown_support':{
                'constraint': None,
                'function': self.draw_unknown_support,
                'v_params': {
                    "support_width" : 0.1,
                    "support_height" : 0.075,
                    "support_color": 'red',
                    'marker_shape': '^',
                    "marker_size" : 6,
                    'marker_color': 'red',
                    "marker_face_color" : 'white',
                    "transparency" : 1,
                    }
            }
        }

        # Inicjalizujemy most (FigureCanvas) przekazując mu naszą "kartkę"
        super().__init__(self.fig)
        self.setParent(parent)

    # Funkcja czyszcząca wykres
    def clear_mesh(self):
        self.axes.clear()
        self.draw() # Odświeżenie widoku
        # Czyszczenie słownika obiektów Matplotlib, canvas.clear() pozostawia klucze (id węzłów) w słowniku dlatego przy zmianie pliku siatki 
        # program prubuje wymazać coś czego nie ma i się wiesi
        self.drawn_nodeOBJ = {}
        self.drawn_elementOBJ = {}

    # Funkcja ustawień płutna:
    def canvas_settings(self):
        # Słownik domyślnych ustawień:
        def update_canvas():
            set_aspect = self.canvas_settings_dict['set_aspect']
            margins = float(self.canvas_settings_dict['margins'])
            gridTF = self.canvas_settings_dict['grid(True/False)']
            grid_linestyle = self.canvas_settings_dict['grid_linestyle']
            grid_alpha = float(self.canvas_settings_dict['grid_alpha'])
            # Zabezpieczenie przed złą wartością grubości linii, ponieważ te same grubości linii są używane w każdym elemencie zapisywane są do oddzielnych zmiennych
            float(self.canvas_settings_dict['thinn_line'])
            float(self.canvas_settings_dict['thicc_line'])
            
            self.axes.set_aspect(set_aspect) # ustawienie takich samych proporcji dla obu osi
            self.axes.margins(margins) # ustawienie marginesu np. 20% aby id węzłów nie nachodziły na ramkę wykresu
            if gridTF:
                self.axes.grid(linestyle = grid_linestyle, alpha = grid_alpha)
            else:
                self.axes.grid(visible = gridTF) # niestety reszta ustawień nadpisuje opcję visible = false
            
        # Sprawdzane jest czy słownik w ogóle istnieje.
        if hasattr(self, 'canvas_settings_dict') and self.canvas_settings_dict:
            try:
                update_canvas()
            except Exception as e:
                QMessageBox.warning(self,
                            "Canvas settings Error",
                            f"Unexpected canvas visual settings value,\nError log:\n{e}")
                self.canvas_settings_dict = self.canvas_default_settings.copy()
                update_canvas()
        else:
            self.canvas_settings_dict = self.canvas_default_settings.copy()
            update_canvas()
            
    # Funkcja tworząca brakujące słowniki dla nowej siatki:
    def initiate_new_mesh(self, data_type):
        # Ustawienie flagi typu danych
        self.data_type = data_type
        # Słowniki:
        self.nodes = {}
        self.elements = {}
        self.nodeOBJ_visuals = {}
        self.elementOBJ_visuals = {}
        self.user_defined_materials = {}
        self.symbol_substitutes = {}
        self.mesh_summary = copy.deepcopy(self.MainWindow.mesh_summary)
        self.cross_sections = copy.deepcopy(self.system_sections)
        # czyszczenie w razie wczytania nowej siatki:
        self.clear_mesh() # tutaj alokowane są słowniki drawn OBJ
        # Odświerzanie ustawień płutna:
        self.canvas_settings()
        self.selection_size = 16.0
        self.draw()

    # Funkcja główna alokowania słownika siatki JSON do wyrażenia self.mesh_dat
    def unpack_mesh(self, mesh_dat, data_type, raporting = True):
        # Ustawienie flagi typu danych
        self.data_type = data_type
        # Określenie słownika JSON w obszarze klasy canvas
        self.mesh_dat = mesh_dat
        self.mesh_summary = copy.deepcopy(self.mesh_dat["model_summary"])
        # Czyszczenie słoników:
        self.cross_sections = copy.deepcopy(self.system_sections)
        self.user_defined_materials = {}
        # czyszczenie w razie wczytania nowej siatki:
        self.clear_mesh()
        # Odświerzanie ustawień płutna:
        self.canvas_settings()
        self.selection_size = 16.0
        # tworzenie słowników siatki:
        self.generate_mesh_directories(data_type, Raport_dialog = raporting)
        # rysowanie siatki
        self.draw_mesh(Raport_dialog = raporting)
        self.draw_OBJ_selection(cancel = True)

    # Funkcja walidująca wartość:
    def validate_val(self, val, symbol_key = None, return_val_only = False):
        try:
            absolute_val = float(val)
            return absolute_val, True
        except ValueError as e:
            if self.data_type == "symbolic":
                try:
                    absolute_val = sp.sympify(val, locals = self.LOCAL)
                    absolute_val = float(absolute_val.subs(self.symbol_substitutes[symbol_key]))
                    if return_val_only:
                        return absolute_val
                    else:
                        return absolute_val, True
                except Exception as e:
                    print(e)
                    return val, False
            return val, False

    # Funkcja budująca listy węzłów i elementów na stronie edytora:
    def make_OBJ_lists(self):
        e_list = []
        for e_id, e_dict in self.elements.items():
            e_list.append(f"ID: {e_id} | {e_dict["node_1_id"]}->{e_dict["node_2_id"]} | {self.map_element_type(e_id, MessageBox = False, log = False)}")
        # czyszczenie i importowanie listy:
        self.MainWindow.EL_list.clear()
        self.MainWindow.EL_list.addItems(e_list)
        n_list = []
        for n_id, n_dict in self.nodes.items():
            n_list.append(f"ID: {n_id} | {self.map_node_constraints(n_id, MessageBox = False, log = False)}")
        self.MainWindow.Node_list.clear()
        self.MainWindow.Node_list.addItems(n_list)


    # Funkcja czyszcząca wszelkie słowniki i dane po powrocie do menu głównego:
    def delete_mesheditor_data(self):
        def delete_except(item_f, name = ""):
            try:
                item = item_f() if callable(item_f) else item_f
                del item
                print(f"dleted: {name}")
            except Exception as e:
                print(f"Couldnt delete: {name}\n {e}")
        
        delete_except(lambda: self.mesh_dat, "imported JSON")
        delete_except(lambda: self.nodes, "nodes dict")
        delete_except(lambda: self.elements, "elements dict")
        delete_except(lambda: self.nodeOBJ_visuals, "node visuals")
        delete_except(lambda: self.elementOBJ_visuals, "element visuals")
        delete_except(lambda: self.symbol_substitutes, "symbol substitutes")
        delete_except(lambda: self.user_defined_materials, "user defined materials")
        self.clear_mesh()
        self.cross_sections = copy.deepcopy(self.system_sections)

#========== Elementy

    # Funkcja generowania słownika elementów
    def unpack_elements(self, MessageBox = True, log = False):
        # Przygotowanie słownika:
        self.elements = {}
        # Pobranie danych elementu z pliku siatki
        elements_dict = self.mesh_dat['elements']
        for i, e in enumerate(elements_dict, start = 1):
            e_id = e["id"]
            # SPRAWDZENIE SORTOWANIA / DUPLIKATÓW
            if i != e_id:
                print("ERROR - Element id are not properly sorted or contain duplicates")
                QMessageBox.critical(self,
                        "Failed to generate mesh",
                        f"Element ID error! Expected ID: {i}, but found: {e_id} in JSON file.\n"
                        "Ensure ascending order and no duplicates are present.")
                return # Przerywamy ładowanie siatki
                
            # Budowanie słownika self.elements, nie ma co się matrwić referencjami ponieważ eklements dict istnieje tylko lokalnie
            self.elements[e_id] = {}
            self.elements[e_id]["id"] = e_id
            self.elements[e_id]["type"] = elements_dict[e_id - 1].get("type", "unknown_element") # e_id -1 ponieważ elements_dict to lista
            self.elements[e_id]["node_1_id"] = elements_dict[e_id - 1].get("node_1_id", "???")
            self.elements[e_id]["node_2_id"] = elements_dict[e_id - 1].get("node_2_id", "???")
            self.elements[e_id]["material"] = elements_dict[e_id - 1].get("material", "???")
            if self.elements[e_id]["type"] in ("Spring", "Spring_2D"):
                self.elements[e_id]["stiffness"] = elements_dict[e_id - 1].get("stiffness", "???")
            else:
                self.elements[e_id]["section_id"] = elements_dict[e_id - 1].get("section_id", "???")
            def warning_msg(assigned_key, e_id, property_name):
                if assigned_key == "???":
                    if MessageBox:
                        QMessageBox.warning(self,
                                            f"Missing {property_name} in Element id: {e_id}",
                                            "Missing properties can be added in Edit Element dialog")
                    if log:
                        self.mesh_directory_values_ERROR_log.append(f"Missing {property_name} in Element id: {e_id}")
                        print(f"added_log {property_name}")
            
            def check_property_presence(property_id, e_id, property_name, property_dict_1, property_dict_2 = {}):
                if property_id == "???":
                    return
                if property_id not in (property_dict_1 | property_dict_2):
                    if MessageBox:
                        QMessageBox.warning(self,
                                            f"Invalid {property_name} in Element id: {e_id}",
                                            f"Couldnt find '{property_id}' in {property_name} library")
                    if log:
                        self.mesh_directory_values_ERROR_log.append(f"Couldnt find '{property_id}' in {property_name} library for Element ID: {e_id}")

            warning_msg(self.elements[e_id]["material"], e_id, "material")
            check_property_presence(self.elements[e_id]["material"], e_id, "material", self.system_materials, self.user_defined_materials)
            if self.elements[e_id]["type"] in ("Spring", "Spring_2D"):
                warning_msg(self.elements[e_id]["stiffness"], e_id, "stiffess")
            else:
                warning_msg(self.elements[e_id]["section_id"], e_id, "cross_section")
                check_property_presence(self.elements[e_id]["section_id"], e_id, "cross_section", self.cross_sections)
            
            

        return

    # Funkcja mapująca typ elementu
    def map_element_type(self, e_id, MessageBox = True, log = False):
        element_type = self.elements[e_id].get('type', 'unknown_element')
        for e_type in self.element_type.keys():
            if element_type == e_type:
                mapped_type = e_type
                return mapped_type
        mapped_type = "unknown_element"
        if MessageBox:
            QMessageBox.warning(self, 
                    "Element validation Error",
                    f"Could not find element type for element id: {e_id}, \n Elementy type has to be assigned before conducting calculations")
        if log:
            self.mesh_directory_values_ERROR_log.append(f"Could not find element type for element id: {e_id}, \n Element type has to be assigned before conducting calculations")
        return mapped_type
    
    # Funkcja tworząca słownik parametrów wizualnych elementów
    def unpack_elementOBJ_visuals(self, MessageBox = True, log = False):
        self.elementOBJ_visuals = {}
        # Bezpieczne pobranie zapisanych wizualiów (jeśli plik je posiada)
        saved_visuals = self.mesh_dat.get("elementOBJ_visuals", {})

        for e_id in self.elements.keys():
            e_type = self.map_element_type(e_id, MessageBox, log)
            str_e_id = str(e_id)

            if str_e_id in saved_visuals:
                raw_params = saved_visuals[str_e_id].get("visual_parameters", self.element_type[e_type]['v_params'])
                v_params = raw_params.copy()
                label_params = saved_visuals[str_e_id].get("label", copy.deepcopy(self.default_element_label_params))
            else:
                raw_params = self.element_type[e_type]['v_params']
                v_params = raw_params.copy()
                label_params = copy.deepcopy(self.default_element_label_params)
            self.elementOBJ_visuals[e_id] = {
                                'element_type' : e_type,
                                'visual_parameters' : v_params,
                                'label': label_params 
                            }

#========== Węzły

    # Funkcja generowania słownika węzłów oraz slownika substytutów
    def unpack_nodes(self):
        # inicjowanie słowników
        self.nodes = {}
        nodes = {}
        # czytanie listy z pliku siatki
        nodes_dict = self.mesh_dat['nodes']
        # Tworzenie słownika nodes:
        for n in nodes_dict:
            try:
                n_id = n["id"]
                # Sprawdzamy czy nie ma duplikatów
                if n_id in nodes:
                    QMessageBox.critical(
                        self,
                        "Duplicate node ID",
                        f"Node ID {n_id} appears more than once."
                    )
                    return
                # Tworzenie słowika dla węzła n_id
                nodes[n_id] = {
                    "id": n_id,
                    "constraint": n["constraint"],
                    "coordinates": n["coordinates"],
                }
            except KeyError as e:
                QMessageBox.critical(
                    self,
                    "Missing node data in mesh file",
                    "Ensure nodes mesh contains dictionaries with keys: "
                    "[id], [constraint], [coordinates]\n"
                    f"Missing key: {e}"
                )
                return
        # Sortowanie raz, po zbudowaniu słownika, sorted zwraca listę dlatego musi być dict
        self.nodes = dict(sorted(nodes.items()))
        # Sprawdzenie kolejności ID
        for expected_id, n_id in enumerate(self.nodes.keys(), start=1):
            if expected_id != n_id:
                QMessageBox.critical(
                    self,
                    "Failed to generate mesh",
                    f"Node ID error! Expected ID: {expected_id}, but found: {n_id}.\n"
                    "Ensure ascending order and no duplicates are present."
                )
                return  
    
    # Funkcja mapowania typu podpory
    def map_node_constraints(self, n_id, MessageBox = True, log = False):
        constraint_type = self.nodes[n_id]["constraint"]
        def search_constraint():
            for support_type, contents in self.support_type.items():
                constraint = contents['constraint']
                if constraint_type == constraint:
                    mapped_support = support_type
                    return mapped_support
            return None
        # Próbujemy znaleźć uwiązanie:
        mapped_support = search_constraint()
        # Sprawdzamy czy znaleziono:
        if mapped_support:
            return mapped_support
        else:
            # Jeśli constraint są przechowywane jako tekst:
            for axis, const in constraint_type.items():
                val_str = str(const).strip().lower()
                if val_str == "true":
                    self.nodes[n_id]["constraint"][axis] = True
                elif val_str == "false":
                    self.nodes[n_id]["constraint"][axis] = False
            # Próbujemy jeszcze raz po modyfikacji słownika:
            constraint_type = self.nodes[n_id]["constraint"]
            mapped_support = search_constraint()
            if mapped_support:
                return mapped_support
            else:
                # Jeśli nie znaleziono podpory, funkcja nadal się wykonuje i przypisuje unknown support       
                mapped_support = "unknown_support"
                if MessageBox is True:
                    QMessageBox.warning(self, 
                            "Node validation Error",
                            f"Could not find support for node id: {n_id}, \nNode constraint need to be updated")
                if log is True and hasattr(self, "mesh_directory_values_ERROR_log"):
                    self.mesh_directory_values_ERROR_log.append(f"Could not find support for node id: {n_id}, Node constraint need to be updated")
                return mapped_support
            
    # Funkcja generowania/pobierania słownika wizualnych parametrów węzła:
    def unpack_nodeOBJ_visuals(self, MessageBox = True, log = False):
        self.nodeOBJ_visuals = {}
        # Bezpieczne pobranie zapisanych wizualiów (jeśli plik je posiada)
        saved_visuals = self.mesh_dat.get("nodeOBJ_visuals", {})

        for n_id in self.nodes:
            # Zmapowanie typu uwiązania
            s_type = self.map_node_constraints(n_id, MessageBox, log)
            # JSON zawsze czyta klucze słowników jako stringi, więc rzutujemy n_id
            str_n_id = str(n_id)
        
            if str_n_id in saved_visuals:
                # Węzeł ma zapisane własne parametry w pliku
                raw_params = saved_visuals[str_n_id].get("visual_parameters", self.support_type[s_type]['v_params'])
                v_params = raw_params.copy()
                label_params = saved_visuals[str_n_id].get("label", copy.deepcopy(self.default_node_label_params))
            else:
                # Brak danych w pliku - ładujemy startowe parametry z bazy statycznej
                raw_params = self.support_type[s_type]['v_params']
                v_params = raw_params.copy()
                label_params = copy.deepcopy(self.default_node_label_params)
            
            # Zapisanie kompletnego stanu do pamięci płótna
            self.nodeOBJ_visuals[n_id] = {
                    'support_type': s_type,
                    'visual_parameters': v_params,
                    'label': label_params
                    }

#========== Pobieranie innych danych:
    
    # Funkcja wczytująca słownik substytutów:
    def unpack_symbol_substitutes(self, MessageBox = True, log = False):
        try:
            symbol_dict = self.mesh_dat["symbol_substitutes"]
            self.symbol_substitutes = symbol_dict.copy()
        except KeyError as e:
            if MessageBox:
                QMessageBox.warning(self,
                                    "Missing symbol substitute data",
                                    f"Mesh file is missing {e} key that is reserved for symbol substitutions.\n"
                                    'example: "symbol_substitutes": {"area" : {"A" : 0.01}, "inertia_y" : {"I" : 8.33e-6}, "length" : {"l": 1.0}}\n'
                                    "All symbols will be interpreted as if their value was equal to 1.0, "
                                    "changing that value is possible via Substitute dialog")
            if log:
                self.mesh_directory_values_ERROR_log.append("Missing symbol substitute data\n"
                                                            f"Mesh file is missing {e} key that is reserved for symbol substitutions.\n"
                                                            'example: "symbol_substitutes": {"area" : {"A" : 0.01}, "inertia_y" : {"I" : 8.33e-6}, "length" : {"l": 1.0}}\n'
                                                            "All symbols will be interpreted as if their value was equal to 1.0, "
                                                            "changing that value is possible via Substitute dialog")
            return
        try:
            for sym_role, sym_dict in symbol_dict.items():
                for sym_name, sym_val in sym_dict.items():
                    float(sym_val)
                    invalid_sym_name = sym_name
                    invalid_sym_role = sym_role
        except (ValueError, TypeError, AttributeError) as e:
            message_text = "---------------------------------------" 
            if isinstance(e, ValueError):
                message_text = f"Invalid symbol value for {invalid_sym_name} ({invalid_sym_role} type symbol)"
            if MessageBox:
                QMessageBox.critical(self,
                    "Substitute dict error",
                    f"Invalid symbol_substitutes layout: {e}\n"
                    "Expected layout: \"symbol_substitutes\":{\n\"length\": {\"L\": float, ...},\n \"area\":{\"A_1\": float, ...}, \n...}\n"
                    f"{message_text}\n"
                    "Symbolic data has been erased.")
            if log:
                self.mesh_directory_values_ERROR_log.append("Substitute dict error\n"
                                    f"Invalid symbol_substitutes layout: {e}\n"
                                    "Expected layout: \"symbol_substitutes\":{\n\"length\": {\"L\": float, ...},\n \"area\":{\"A_1\": float, ...}, \n...}\n"
                                    f"{message_text}\n"
                                    "Symbolic data has been erased.")
            self.symbol_substitutes = {}
        print(f"Imported {self.data_type} mesh")
        return

    # Funkcja wczytująca słownik przekroji poprzecznych:
    def unpack_cross_sections(self, log = False):
        cross_section_dict = self.mesh_dat.get("cross_sections", None)
        if cross_section_dict:
            try:
                for section_id, section_dict in cross_section_dict.items():
                    self.cross_sections[section_id] = section_dict.copy()
            except Exception as e:
                if log:
                    self.mesh_directory_values_ERROR_log.append(f"WARNING: A problem occured while importing cross section data:\n {e}")
                return
        else:
            if log:
                self.mesh_directory_values_ERROR_log.append("Note - couldnt locate user-defined cross sections")
        return
    
    # Funkcja wczytująca słownik materiałów urzytkownika:
    def unpack_user_materials(self, log = False):
        self.user_defined_materials = {}
        user_materials_dict = self.mesh_dat.get("user_defined_materials", None)
        if user_materials_dict:
            try:
                for material_id, material_dict in user_materials_dict.items():
                    if material_id in self.system_materials:
                        if log:
                            self.mesh_directory_values_ERROR_log.append(f"WARNING: user defined material id: {material_id} is already present in system materials library\n"
                                                                        "material was not imported - change name in mesh file")
                    else:
                        self.user_defined_materials[material_id] = material_dict.copy()
            except Exception as e:
                if log:
                    self.mesh_directory_values_ERROR_log.append(f"WARNING: A problem occured while importing material data:\n {e}")
                pass
        else:
            if log:
                self.mesh_directory_values_ERROR_log.append("Note - couldnt locate user-defined material library")
        return

#========== Komnonowanie siatki:

    # Funkcja tworzenia słowników siatki
    def generate_mesh_directories(self, data_type, Raport_dialog = True):
        # Prosta funkcja powiększająca Listę logów:
        def Extend_list(local_log, global_log):
            if not local_log:
                global_log.append("No problems occured")
            else:
                global_log.extend(self.mesh_directory_values_ERROR_log)
        # Inicjacja schowka logów:
        Report_log = []
        # Rozpakowywanie przekrojów poprzecznych:
        self.mesh_directory_values_ERROR_log = []
        Report_log.append("======== Imported cross sections check ========")
        self.unpack_cross_sections()
        Extend_list(self.mesh_directory_values_ERROR_log, Report_log)

        # Rozpakowywanie materiałów:
        self.mesh_directory_values_ERROR_log = []
        Report_log.append("======== Imported materials sections check ========")
        self.unpack_user_materials(log = True)
        Extend_list(self.mesh_directory_values_ERROR_log, Report_log)


        # Rozpakowanie elementów:
        self.mesh_directory_values_ERROR_log = []
        Report_log.append("======== Element properties check ========")
        self.unpack_elements(MessageBox = False, log = True)
        self.unpack_elementOBJ_visuals(MessageBox = False, log = True)
        Extend_list(self.mesh_directory_values_ERROR_log, Report_log)

        # Rozpakowywanie węzłów:
        self.mesh_directory_values_ERROR_log = []
        Report_log.append("======== Node constraint check ========")
        self.unpack_nodes()
        self.unpack_nodeOBJ_visuals(MessageBox = False, log = True)
        Extend_list(self.mesh_directory_values_ERROR_log, Report_log)
        
        # Pobranie słownika symboli:
        # Jeśli jest to siatka symboliczna należy utworzyć słownik symboli:
        if data_type == "symbolic":
            self.mesh_directory_values_ERROR_log = []
            Report_log.append("======== Symbol substitutes check ========")
            self.unpack_symbol_substitutes(MessageBox = False, log = True)
            Extend_list(self.mesh_directory_values_ERROR_log, Report_log)

        # Inicjowanie dialogu raportu
        if Raport_dialog:
            dialog = ListReportLog(self, self, title = "Loaded object properties log", display_list = Report_log, minimum_width = 650)
            dialog.exec()
        return

    # Funkcja rysowania siatki (mając już wszelkie potrzebne słowniki)
    def draw_mesh(self, Raport_dialog = True):
        # Rysowanie węzłów oraz labeli węzłów
        # Tworzenie loga dla rysowania siatki:
        self.mesh_drawing_ERROR_log = []
        Report_log = []
        for n_id in self.nodes:
            self.draw_node(n_id, refresh_canvas = False, MessageBox = False, log = True)
        Report_log.append("========= Checking Nodes =========")
        if self.mesh_drawing_ERROR_log:
            Report_log.extend(self.mesh_drawing_ERROR_log)
        else:
            Report_log.append("No errors occured")

        # Rysowanie elementów
        self.mesh_drawing_ERROR_log = []
        for e_id in self.elements:
            self.draw_element(e_id, refresh_canvas = False, MessageBox = False, log = True)
        Report_log.append("========= Checking Elements =========")
        if self.mesh_drawing_ERROR_log:
            Report_log.extend(self.mesh_drawing_ERROR_log)
        else:
            Report_log.append("No errors occured")

        # Sprawdzanie ustawienia elementów dla PErpandicular_Beam_Construction:
        if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
            self.mesh_drawing_ERROR_log = []
            for e_id in self.elements:
                self.check_element_positioning(e_id, MessageBox = False, log = True)
            Report_log.append("========= Checking Parallel_Beam_Approach positioning =========")
            if self.mesh_drawing_ERROR_log:
                Report_log.extend(self.mesh_drawing_ERROR_log)
            else:
                Report_log.append("No errors occured")

        # Czyszczenie error loga
        self.mesh_drawing_ERROR_log = []
        # Odświerzanie płutna
        self.draw()
        self.simple_mesh_flag = False
        # Insertowanie list:
        self.make_OBJ_lists()

        # Inicjowanie dialogu raportu
        if Raport_dialog:
            dialog = ListReportLog(self, self, title = "Mesh drawing log", display_list = Report_log, minimum_width = 650)
            dialog.exec()
        
# =================================================
# Funkcje rysujące poszczególne obiekty : ELEMENTY
# =================================================
    
    # Funkcja pobierająca koordynaty węzłów
    def get_element_vector(self, e_id, MessageBox = True, log = False, angle_only = False):
        no_node_flag = False
        node_1_id = self.elements[e_id]['node_1_id']
        node_2_id = self.elements[e_id]['node_2_id']  

        # Pobieranie za pomocą funkcji węzła
        x_1, z_1, no_coords_flag_1 = self.get_node_coordinates(node_1_id, MessageBox = False, log = False)
        x_2, z_2, no_coords_flag_2 = self.get_node_coordinates(node_2_id, MessageBox = False, log = False)
        if no_coords_flag_1:
            no_node_flag = True
            x_1 = 1
            z_1 = 1
        if no_coords_flag_2:
            no_node_flag = True
            x_2 = 2
            z_2 = 2
        if node_1_id == node_2_id:
            no_node_flag = True
            x_1 = 1
            z_1 = 1
            x_2 = 2
            z_2 = 2
            if MessageBox:
                QMessageBox.warning(self, 
                            "Mesh error",
                            f"Element id: {e_id} is connected to one node, modify connection in element edit dialog")
            if log:
                self.mesh_drawing_ERROR_log.append(f"WARNING: Element id: {e_id} is connected to one node, modify connection in element edit dialog")

        dx = x_2 - x_1
        dz = z_2 - z_1
        L = np.hypot(dx, dz) # Funkcja wyznaczająca długlość z tw. pitagorasa odporna na różne "mylące" dane
        theta = np.arctan2(dz, dx) # Atan który jest odporny na różne wartości
        if no_node_flag and log:
            self.mesh_drawing_ERROR_log.append(f"WARNING: Element id: {e_id}: Invalid node allocation\n missing node coordinates \\ invalid node id")
        if angle_only:
            return theta
        return x_1, z_1, x_2, z_2, L, theta, no_node_flag

    # Funkcja rysująca podkreślenie elementu aby zwrócił na sibie uwagę
    def draw_element_highlight(self, e_id, edge_color = 'green', marker_shape = 'o', marker_size = 6, highlight_text = "", font_size = 10, font_color = 'green'):
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox = False, log = False)
        x_flat = L/2
        z_flat = 0
        x_final = x_flat * np.cos(theta) - z_flat * np.sin(theta) + x_1
        z_final = x_flat * np.sin(theta) + z_flat * np.cos(theta) + z_1
        drawn_highlight = self.axes.plot(
                        x_final, z_final, 
                        marker = marker_shape, 
                        markeredgecolor = edge_color, 
                        markersize = marker_size, 
                        markerfacecolor = 'none',
                        linestyle = 'None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
        drawn_highlight_text = self.axes.text(x_final + L/20, z_final +  L/20, f"{highlight_text}", fontsize = font_size, color = font_color)
        return drawn_highlight, drawn_highlight_text
 
    # Funkcja rysowania sprężyny:
    def draw_spring(self, e_id, MessageBox = True, log = False):
        # Pobranie podstawowych danych
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox, log)   
        def draw():
            # Pobranie parametrów:
            aspect_ratio = float(self.elementOBJ_visuals[e_id]['visual_parameters']['aspect_ratio'])
            coil_num = int(self.elementOBJ_visuals[e_id]['visual_parameters']['coil_num'])
            spring_lead_param = float(self.elementOBJ_visuals[e_id]['visual_parameters']['spring_lead'])
            spring_lead = spring_lead_param * L / aspect_ratio
            start_offset_param = float(self.elementOBJ_visuals[e_id]['visual_parameters']['start_offset'])
            start_offset = start_offset_param * L / aspect_ratio
            element_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['element_line_type']
            element_color = self.elementOBJ_visuals[e_id]['visual_parameters']['element_color']
            transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['transparency'])
            width = L / aspect_ratio
            # Koordynaty dla pierwszej i ostatniej lini (część prostego odcinka sprężyny)
            x_lead_1 = [start_offset, spring_lead + start_offset]
            z_lead_1 = [0, 0]
            x_lead_2 = [L - spring_lead - start_offset, L - start_offset]
            z_lead_2 = [0, 0]
            # Tworzenie list wszystkich punktów rysowania sprężyny
            x_flat = []
            z_flat = []
            x_flat.extend(x_lead_1)
            z_flat.extend(z_lead_1)
            # Generowaie punktów dla zwojnicy, pamiętając że start i stop muszą być na wysokości 0:
            coil_x_cords = np.linspace(x_lead_1[1], x_lead_2[0], 2 * coil_num)
            for i, x in enumerate(coil_x_cords):
                x_flat.append(x) # Dodanie koordynaty x
                if i % 2 == 0: # Zwraca true dla liczby podzielnej przez 2 lub 0
                    z_flat.append(-width / 2) # wierzchołek dolny
                else:
                    z_flat.append(width / 2) # wierzchołek górny
            # dodanie końcówki sprężyny:
            x_flat.extend(x_lead_2)
            z_flat.extend(z_lead_2)
            # Konwersja standardowych list na tablice numpy, chodzi o to by móc całą tablicę przemnożyć razy skalar lub do karzdego elementu dodać skalar
            x_flat = np.array(x_flat)
            z_flat = np.array(z_flat)
            # Równanie obrotu o kąt theta, zwraca sprężynę obróconą ale o początku w punkcie (0,0)
            x_rot = x_flat * np.cos(theta) - z_flat * np.sin(theta)
            z_rot = x_flat * np.sin(theta) + z_flat * np.cos(theta)
            # Translacja (przesunięcie na właściwe miejsce na ekranie)
            x_final = x_rot + x_1
            z_final = z_rot + z_1

            # Rysowanie sprężyny:
            drawn_elementOBJ_local = {}
            drawn_elementOBJ_local['element'] = self.axes.plot(x_final, z_final, linestyle = element_line_type, linewidth = self.canvas_settings_dict['thicc_line'], color = element_color, alpha = transparency)

            # rysowanie zaznaczenia na wypadek braku węzła
            if no_node_flag:
                drawn_elementOBJ_local['highlight'], drawn_elementOBJ_local['highlight_text'] = self.draw_element_highlight(e_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = f"E_{e_id} NODE NOT ALLOCATED", font_size = 10, font_color = 'red')
            else:
                pass

            return drawn_elementOBJ_local

        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            if MessageBox:
                QMessageBox.warning(self,
                                "Element object canvas failure",
                                f"Unexpected element visual parameter. \nTo prevent crashes visual element properties has been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.element_type['2N2DOF_Bar']['v_params']
            self.elementOBJ_visuals[e_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()   

    # Funkcja rysowania pręta:
    def draw_rod(self, e_id, MessageBox = True, log = False):
        # Pobranie podstawowych danych
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox, log) 
        def draw():
            # Pobranie parametrów:
            aspect_ratio = float(self.elementOBJ_visuals[e_id]['visual_parameters']['aspect_ratio'])
            try:
                if str(self.elementOBJ_visuals[e_id]['visual_parameters']['real_aspect_ratio'].strip().lower()) in ("yes", "true", "1"):
                    max_z = self.cross_sections[self.elements[e_id]["section_id"]]["properties"]["max_z"]
                    abs_val, val_flag = self.validate_val(val = max_z, symbol_key = "length")
                    if val_flag:
                        width = 2 * abs_val
                    else:
                        width = L / aspect_ratio
                else:
                    width = L / aspect_ratio
            except Exception:
                width = L / aspect_ratio
            start_offset_param = float(self.elementOBJ_visuals[e_id]['visual_parameters']['start_offset'])
            start_offset = start_offset_param * L / aspect_ratio
            element_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['element_line_type']
            element_color = self.elementOBJ_visuals[e_id]['visual_parameters']['element_color']
            transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['transparency'])
            symbol_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_line_type']
            symbol_color = self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_color']
            symbol_transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_transparency'])
            
            arrow_length = (L - 2 * start_offset)/4 # Określa długość "strzałki" wewnątrz pręta
            arr_h = width/4 # określa "wysokość" grota strzałki
            arr_l = arrow_length/6 # określa długość grota strzałki
            width_05 = width / 2
            L_05 = L / 2
            # Punkty rysowania prostokątnej części pręta (aby domknąć prostokąt potrzeba 5 punktu (kolejno punkty: 1 -> 2 -> 3 -> 4 -> 1))
            x_flat = [start_offset, start_offset, L - start_offset, L - start_offset, start_offset]
            z_flat = [-width_05 , width_05 , width_05 , -width_05 , -width_05 ]
            
            # Punkty rysowania skrzałkowej części pręta (wewnątrz, wskazuje na tylko reakcje w osi)
            x_a_flat = [L_05 - arrow_length/2 + arr_l, L_05 - arrow_length/2, L_05 + arrow_length/2, L_05 + arrow_length/2 - arr_l]
            z_a_flat = [arr_h, 0, 0, -arr_h]

            # Konwersja standardowych list na tablice numpy, chodzi o to by móc całą tablicę przemnożyć razy skalar lub do karzdego elementu dodać skalar
            x_flat = np.array(x_flat)
            z_flat = np.array(z_flat)
            x_a_flat = np.array(x_a_flat)
            z_a_flat = np.array(z_a_flat)
    
            # Równanie obrotu p kąt theta, zwraca sprężynę obróconą ale o początku w punkcie (0,0)
            x_rot = x_flat * np.cos(theta) - z_flat * np.sin(theta)
            z_rot = x_flat * np.sin(theta) + z_flat * np.cos(theta)
            x_a_rot = x_a_flat * np.cos(theta) - z_a_flat * np.sin(theta)
            z_a_rot = x_a_flat * np.sin(theta) + z_a_flat * np.cos(theta)
    
            # Translacja (przesunięcie na właściwe miejsce na ekranie)
            x_final = x_rot + x_1
            z_final = z_rot + z_1
            x_a_final = x_a_rot + x_1
            z_a_final = z_a_rot + z_1

            # Rysowanie pręta:
            drawn_elementOBJ_local = {}
            drawn_elementOBJ_local['element'] = self.axes.plot(x_final, z_final, linestyle = element_line_type, linewidth = self.canvas_settings_dict['thicc_line'], color = element_color, alpha = transparency)
            drawn_elementOBJ_local['symbol'] = self.axes.plot(x_a_final, z_a_final, linestyle = symbol_line_type, linewidth = self.canvas_settings_dict['thinn_line'], color = symbol_color, alpha = symbol_transparency)

            # rysowanie zaznaczenia na wypadek braku węzła
            if no_node_flag:
                drawn_elementOBJ_local['highlight'], drawn_elementOBJ_local['highlight_text'] = self.draw_element_highlight(e_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = f"E_{e_id} NODE NOT ALLOCATED", font_size = 10, font_color = 'red')
            else:
                pass

            return drawn_elementOBJ_local

        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            if MessageBox:
                QMessageBox.warning(self,
                                "Element object canvas failure",
                                f"Unexpected element visual parameter. \nTo prevent crashes visual element properties has been restored to default.\nError log:\n{e}")
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.element_type['2N2DOF_Bar']['v_params']
            self.elementOBJ_visuals[e_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()

    # Funkcja rysowania belki:
    def draw_beam(self, e_id, MessageBox = True, log = False):
        # Pobranie podstawowych danych
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox, log)    
        def draw():
            # Pobranie parametrów:
            # Pobranie parametrów:
            aspect_ratio = float(self.elementOBJ_visuals[e_id]['visual_parameters']['aspect_ratio'])
            try:
                if str(self.elementOBJ_visuals[e_id]['visual_parameters']['real_aspect_ratio'].strip().lower()) in ("yes", "true", "1"):
                    max_z = self.cross_sections[self.elements[e_id]["section_id"]]["properties"]["max_z"]
                    abs_val, val_flag = self.validate_val(val = max_z, symbol_key = "length")
                    if val_flag:
                        width = 2 * abs_val
                    else:
                        width = L / aspect_ratio
                else:
                    width = L / aspect_ratio
            except Exception:
                width = L / aspect_ratio
            start_offset_param = float(self.elementOBJ_visuals[e_id]['visual_parameters']['start_offset'])
            start_offset = start_offset_param * L / aspect_ratio
            element_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['element_line_type']
            element_color = self.elementOBJ_visuals[e_id]['visual_parameters']['element_color']
            transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['transparency'])
            symbol_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_line_type']
            symbol_color = self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_color']
            symbol_transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_transparency'])

            arrow_length = (L - 2 * start_offset)/4 # Określa długość "strzałki" wewnątrz pręta
            arr_h = width / 3 # określa "wysokość" grota strzałki
            width_05 = width / 2
            L_05 = L / 2
            # Punkty rysowania prostokątnej części pręta (aby domknąć prostokąt potrzeba 5 punktu (kolejno punkty: 1 -> 2 -> 3 -> 4 -> 1))
            x_flat = [start_offset, start_offset, L - start_offset, L - start_offset, start_offset]
            z_flat = [-width_05, width_05, width_05, -width_05, -width_05]
            
            # Punkty rysowania skrzałkowej części belki (wewnątrz, wskazuje na tylko reakcje w poprzek osi)
            x_a_flat = [L_05 - arrow_length/2, L_05 - arrow_length/2, L_05 + arrow_length/2, L_05 + arrow_length/2]
            z_a_flat = [arr_h, 0, 0, -arr_h]
            
            # Konwersja standardowych list na tablice numpy, chodzi o to by móc całą tablicę przemnożyć razy skalar lub do karzdego elementu dodać skalar
            x_flat = np.array(x_flat)
            z_flat = np.array(z_flat)
            x_a_flat = np.array(x_a_flat)
            z_a_flat = np.array(z_a_flat)
    
            # Równanie obrotu o kąt theta, zwraca sprężynę obróconą ale o początku w punkcie (0,0)
            x_rot = x_flat * np.cos(theta) - z_flat * np.sin(theta)
            z_rot = x_flat * np.sin(theta) + z_flat * np.cos(theta)
            x_a_rot = x_a_flat * np.cos(theta) - z_a_flat * np.sin(theta)
            z_a_rot = x_a_flat * np.sin(theta) + z_a_flat * np.cos(theta)
    
            # Translacja (przesunięcie na właściwe miejsce na ekranie)
            x_final = x_rot + x_1
            z_final = z_rot + z_1
            x_a_final = x_a_rot + x_1
            z_a_final = z_a_rot + z_1
            # Rysowanie belki:
            drawn_elementOBJ_local = {}
            drawn_elementOBJ_local['element'] = self.axes.plot(x_final, z_final, linestyle = element_line_type, linewidth = self.canvas_settings_dict['thicc_line'], color = element_color, alpha = transparency)
            drawn_elementOBJ_local['symbol'] = self.axes.plot(x_a_final, z_a_final, linestyle = symbol_line_type, linewidth = self.canvas_settings_dict['thinn_line'], color = symbol_color, alpha = symbol_transparency)

            # rysowanie zaznaczenia na wypadek braku węzła
            if no_node_flag:
                drawn_elementOBJ_local['highlight'], drawn_elementOBJ_local['highlight_text'] = self.draw_element_highlight(e_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = f"E_{e_id} NODE NOT ALLOCATED", font_size = 10, font_color = 'red')
            else:
                pass

            return drawn_elementOBJ_local
        
        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            if MessageBox:
                QMessageBox.warning(self,
                                "Element object canvas failure",
                                f"Unexpected element visual parameter. \nTo prevent crashes visual element properties has been restored to default.\nError log:\n{e}")
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.element_type['2N4DOF_EB']['v_params']
            self.elementOBJ_visuals[e_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
           
    # Funkcja rysowania ramy:
    def draw_frameEl(self, e_id, MessageBox = True, log = False):
        # Pobranie podstawowych danych
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox, log) 
        def draw():
            # Pobranie parametrów:
            # Pobranie parametrów:
            aspect_ratio = float(self.elementOBJ_visuals[e_id]['visual_parameters']['aspect_ratio'])
            try:
                if str(self.elementOBJ_visuals[e_id]['visual_parameters']['real_aspect_ratio'].strip().lower()) in ("yes", "true", "1"):
                    max_z = self.cross_sections[self.elements[e_id]["section_id"]]["properties"]["max_z"]
                    abs_val, val_flag = self.validate_val(val = max_z, symbol_key = "length")
                    if val_flag:
                        width = 2 * abs_val
                    else:
                        width = L / aspect_ratio
                else:
                    width = L / aspect_ratio
            except Exception:
                width = L / aspect_ratio
            start_offset_param = float(self.elementOBJ_visuals[e_id]['visual_parameters']['start_offset'])
            start_offset = start_offset_param * L / aspect_ratio
            element_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['element_line_type']
            element_color = self.elementOBJ_visuals[e_id]['visual_parameters']['element_color']
            transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['transparency'])
            symbol_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_line_type']
            symbol_color = self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_color']
            symbol_transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_transparency'])
            
            arrow_length = (L - 2 * start_offset)/8 # Określa długość "strzałki" wewnątrz pręta
            arr_l = arrow_length/6 # określa długość grota strzałki
            arr_h = width / 4 # określa "wysokość" grota strzałki
            width_05 = width / 2
            L_05 = L / 2
            # Punkty rysowania prostokątnej części pręta (aby domknąć prostokąt potrzeba 5 punktu (kolejno punkty: 1 -> 2 -> 3 -> 4 -> 1))
            x_flat = [start_offset, start_offset, L - start_offset, L - start_offset, start_offset]
            z_flat = [-width_05, width_05, width_05, -width_05, -width_05]
            
            # Punkty rysowania skrzałkowej części ramy
            x_a_flat = [L_05 - arrow_length/2, 
                        L_05 - arrow_length/2 + arr_l, 
                        L_05 - arrow_length/2 + arr_l, 
                        L_05 - arrow_length/2 + arr_l, 
                        L_05 - arrow_length/2 + arr_l,
                        L_05 + arrow_length/2 - arr_l,
                        L_05 + arrow_length/2 - arr_l,
                        L_05 + arrow_length/2 - arr_l,
                        L_05 + arrow_length/2 - arr_l,
                        L_05 + arrow_length/2 ]
            z_a_flat = [0, 0, arr_h, -arr_h, 0, 0, arr_h, -arr_h, 0, 0]
            
            # Konwersja standardowych list na tablice numpy, chodzi o to by móc całą tablicę przemnożyć razy skalar lub do karzdego elementu dodać skalar
            x_flat = np.array(x_flat)
            z_flat = np.array(z_flat)
            x_a_flat = np.array(x_a_flat)
            z_a_flat = np.array(z_a_flat)

            # Równanie obrotu p kąt theta, zwraca sprężynę obróconą ale o początku w punkcie (0,0)
            x_rot = x_flat * np.cos(theta) - z_flat * np.sin(theta)
            z_rot = x_flat * np.sin(theta) + z_flat * np.cos(theta)
            x_a_rot = x_a_flat * np.cos(theta) - z_a_flat * np.sin(theta)
            z_a_rot = x_a_flat * np.sin(theta) + z_a_flat * np.cos(theta)

            # Translacja (przesunięcie na właściwe miejsce na ekranie)
            x_final = x_rot + x_1
            z_final = z_rot + z_1
            x_a_final = x_a_rot + x_1
            z_a_final = z_a_rot + z_1
            # Rysowanie ramy:
            drawn_elementOBJ_local = {}
            drawn_elementOBJ_local['element'] = self.axes.plot(x_final, z_final, linestyle = element_line_type, linewidth = self.canvas_settings_dict['thicc_line'], color = element_color, alpha = transparency)
            drawn_elementOBJ_local['symbol'] = self.axes.plot(x_a_final, z_a_final, linestyle = symbol_line_type, linewidth = self.canvas_settings_dict['thinn_line'], color = symbol_color, alpha = symbol_transparency)

            # rysowanie zaznaczenia na wypadek braku węzła
            if no_node_flag:
                drawn_elementOBJ_local['highlight'], drawn_elementOBJ_local['highlight_text'] = self.draw_element_highlight(e_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = f"E_{e_id} NODE NOT ALLOCATED", font_size = 10, font_color = 'red')
            else:
                pass

            return drawn_elementOBJ_local

        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            if MessageBox:
                QMessageBox.warning(self,
                                "Element object canvas failure",
                                f"Unexpected element visual parameter. \nTo prevent crashes visual element properties has been restored to default.\nError log:\n{e}")
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.element_type['2N6DOF_EB']['v_params']
            self.elementOBJ_visuals[e_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
        
    # Funkcja rysująca nieznany element:
    def draw_unknown_element(self, e_id, MessageBox = True, log = False):
        # Pobranie podstawowych danych
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox, log)  
        def draw():
            # Pobranie parametrów:
            element_line_type = self.elementOBJ_visuals[e_id]['visual_parameters']['element_line_type']
            element_color = self.elementOBJ_visuals[e_id]['visual_parameters']['element_color']
            transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['transparency'])
            symbol_color = self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_color']
            symbol_size = float(self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_size'])
            symbol_offset_x = float(self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_offset_x'])
            symbol_offset_x = symbol_offset_x * L
            symbol_offset_z = float(self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_offset_z'])
            symbol_offset_z = symbol_offset_z * L
            symbol_transparency = float(self.elementOBJ_visuals[e_id]['visual_parameters']['symbol_transparency'])
            L_075 = L * 0.75
            # Punkty rysowania prostokątnej części pręta (aby domknąć prostokąt potrzeba 5 punktu (kolejno punkty: 1 -> 2 -> 3 -> 4 -> 1))
            x_flat = [0, L]
            z_flat = [0, 0]
            
            # Punkty symbolu:
            x_sym_flat = L_075 + symbol_offset_x
            z_sym_flat = symbol_offset_z
            
            # Konwersja standardowych list na tablice numpy, chodzi o to by móc całą tablicę przemnożyć razy skalar lub do karzdego elementu dodać skalar
            x_flat = np.array(x_flat)
            z_flat = np.array(z_flat)
            x_sym_flat = np.array(x_sym_flat)
            z_sym_flat = np.array(z_sym_flat)

            # Równanie obrotu p kąt theta, zwraca sprężynę obróconą ale o początku w punkcie (0,0)
            x_rot = x_flat * np.cos(theta) - z_flat * np.sin(theta)
            z_rot = x_flat * np.sin(theta) + z_flat * np.cos(theta)
            x_sym_rot = x_sym_flat * np.cos(theta) - z_sym_flat * np.sin(theta)
            z_sym_rot = x_sym_flat * np.sin(theta) + z_sym_flat * np.cos(theta)

            # Translacja (przesunięcie na właściwe miejsce na ekranie)
            x_final = x_rot + x_1
            z_final = z_rot + z_1
            x_sym_final = x_sym_rot + x_1
            z_sym_final = z_sym_rot + z_1
            # Rysowanie ramy:
            drawn_elementOBJ_local = {}
            drawn_elementOBJ_local['element'] = self.axes.plot(x_final, z_final, linestyle = element_line_type, linewidth = self.canvas_settings_dict['thicc_line'], color = element_color, alpha = transparency)
            drawn_elementOBJ_local['symbol'] = self.axes.text(x_sym_final, z_sym_final, "???", fontsize = symbol_size, color = symbol_color, alpha = symbol_transparency)

            # rysowanie zaznaczenia na wypadek braku węzła
            if no_node_flag:
                drawn_elementOBJ_local['highlight'], drawn_elementOBJ_local['highlight_text'] = self.draw_element_highlight(e_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = f"E_{e_id} NODE NOT ALLOCATED", font_size = 10, font_color = 'red')
            else:
                pass

            return drawn_elementOBJ_local
        
        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            if MessageBox:
                QMessageBox.warning(self,
                                "Element object canvas failure",
                                f"Unexpected element visual parameter. \nTo prevent crashes visual element properties has been restored to default.\nError log:\n{e}")
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.element_type['unknown_element']['v_params']
            self.elementOBJ_visuals[e_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()

    # Funkcja rysująca label elementu
    def draw_element_label(self, e_id):
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox = False, log = False)
        def draw_label():
            # Pobranie parametrów:
            x_offset = float(self.elementOBJ_visuals[e_id]['label']['x_offset'])
            x_offset = x_offset * L
            z_offset = float(self.elementOBJ_visuals[e_id]['label']['z_offset'])
            z_offset = z_offset * L
            font_size = float(self.elementOBJ_visuals[e_id]['label']['font_size'])
            color = self.elementOBJ_visuals[e_id]['label']['color']
            transparency = float(self.elementOBJ_visuals[e_id]['label']['transparency'])
            L_05 = L * 0.5
            # Punkty symbolu:
            x_sym_flat = L_05 + x_offset
            z_sym_flat = z_offset
            x_sym_flat = np.array(x_sym_flat)
            z_sym_flat = np.array(z_sym_flat)
            x_sym_rot = x_sym_flat * np.cos(theta) - z_sym_flat * np.sin(theta)
            z_sym_rot = x_sym_flat * np.sin(theta) + z_sym_flat * np.cos(theta)
            x_sym_final = x_sym_rot + x_1
            z_sym_final = z_sym_rot + z_1
            # Rysowanie labelu:
            self.drawn_elementOBJ[e_id]['label_obj'] = self.axes.text(x_sym_final, z_sym_final, f"e_{e_id}", fontsize = font_size, color = color, alpha = transparency)

        # Sprawdzamy, czy słownik ma już zapisane parametry labelu
        if "label" in self.elementOBJ_visuals[e_id]:
            try:
                draw_label()
                return
            except Exception as error:
                QMessageBox.warning(self,
                                "Element label Error",
                                f"Couldnt load label for element id: {e_id}, unexpected parameters value\nError log:\n{error}")
                # Nadpisujemy uszkodzone parametry poprawnymi domyślnymi
                draw_label()
                return
        else:
            # Jeśli nie ma, przypisujemy domyślne i rysujemy
            self.elementOBJ_visuals[e_id]['label'] = self.default_element_label_params.copy()
            draw_label()
            return
  
    # Funkcja rysująca elementy, zbierająca wszystko "do kupy":
    def draw_element(self, e_id, refresh_canvas = False, MessageBox = True, log = False):
        # Usuwanie elementu jeżeli jest:
        if e_id in self.drawn_elementOBJ:
            # Pętla wyciąga zawartość wszystkich obiektów elementu:
            for item in self.drawn_elementOBJ[e_id].values():
                # Funkcja usuwająca różne typy obiektów matplotlib
                self.remove_visualOBJ(item)

        # odczytujemy typ elementu:
        e_type = self.elementOBJ_visuals[e_id].get('element_type', 'unknown_element')
        # pobieramy funkcję rysującą (dano drugir get gdyby jakimś cudem 'type' było złe)
        draw_func = self.element_type[e_type].get('function', self.draw_unknown_element)
        # Wywołanie wyspecjalizowanej funkcji (bloki EAFP wewnątrz zadbają o poprawność)
        self.drawn_elementOBJ[e_id] = draw_func(e_id, MessageBox, log)
        self.draw_element_label(e_id)
        # Warunkowe odświeżenie po pojedynczej edycji
        if refresh_canvas:
            self.draw()
        return

# =======================================================
# Funkcje rysujące poszczególne obiekty : OBIEKTY WĘZŁOWE
# ======================================================

    # Funkcja pobierająca koordynaty węzłów
    def get_node_coordinates(self, n_id, MessageBox = True, log = False):
        def get_numerical_coords():
            no_coords_flag = False
            try:
                x = float(self.nodes[n_id]['coordinates']['X'])
                z = float(self.nodes[n_id]['coordinates']['Z'])
            except (TypeError, KeyError, ValueError):
                no_coords_flag = True
                x = 1.5
                z = 1.5
                if MessageBox:
                    QMessageBox.warning(self, 
                                    f"Node id {n_id} error",
                                    f"Invalid node id {n_id} coordinates, use node edit dialog to assign valid coordinates")
                if log:
                    self.mesh_drawing_ERROR_log.append(f"WARNING: Invalid node id {n_id} coordinates, use node edit dialog to assign valid coordinates")
            return x, z, no_coords_flag
        def get_symbolic_coords():
            def corrupt_data_fallback_coords(silent = False):
                no_coords_flag = True
                x = 1.5
                z = 1.5
                if MessageBox:
                    if not silent:
                        QMessageBox.warning(self, 
                                        f"Node id {n_id} error",
                                        f"Corrupted coordinate value for node id: {n_id}")
                if log:
                    if not silent:
                        self.mesh_drawing_ERROR_log.append(f"WARNING: Invalid node id {n_id} coordinates, use node edit dialog to assign valid coordinates")                      
                return x, z, no_coords_flag
            no_coords_flag = False    
            try:
                # Pobranie stringów
                x_str = str(self.nodes[n_id]['coordinates']['X'])
                z_str = str(self.nodes[n_id]['coordinates']['Z'])

                # Jeśli błąd polega na braku wartości (x = ""):
                if not x_str.strip() or not z_str.strip():
                    return corrupt_data_fallback_coords()
                
            except (KeyError, TypeError): # Brak danych w słowniku przypisanie stałych wartości
               return corrupt_data_fallback_coords()
            
            # Inicjacja słownika symboli z warunkiem na brak klucza "length":
            if "length" not in self.symbol_substitutes:
                self.symbol_substitutes["length"] = {}
                
            symbol_subs = self.symbol_substitutes["length"] # Jedynie funkcjonuje jako referencja

            try:
                x_expr = sp.sympify(x_str, locals=self.LOCAL)
                z_expr = sp.sympify(z_str, locals=self.LOCAL)
            except ValueError:
                # Nieudana zamiana na sympy
                return corrupt_data_fallback_coords()
            try:
                # Próba podstawienia wartości:
                x = float(x_expr.subs(symbol_subs))
                z = float(z_expr.subs(symbol_subs))
                return x, z, no_coords_flag
            
            # Wykonuje się tylko jak trzeba a nie zawsze:
            except (ValueError, TypeError):
                no_coords_flag = True
                new_subs_dict = {} # Podzielenie na "new subs" aby móc obsłużyć ewentualny błąd funkcji .update()
                # Tworzenie setów symboli:
                x_expr_set = x_expr.free_symbols
                z_expr_set = z_expr.free_symbols
                # Sumowanie setów ("|" sumuje sety)
                expr_set = x_expr_set | z_expr_set
                # Po zbiorze (set) iteruje się jak po liście, sprawdzamy jakich symboli nie ma w symbol_subs["length"]:
                missing_symbols = []
                for symbol in expr_set:
                    if symbol.name not in symbol_subs: # .name pobiera stringa z symbolu w odpowiedni sposób (str() mogłoby zrobić coś źle)
                        new_subs_dict[symbol.name] = 1 # Przypisywanie 1 brakującej wartości
                        missing_symbols.append(symbol.name)
                if not missing_symbols:
                    if MessageBox:
                        QMessageBox.warning(self, 
                                            f"Node id {n_id} error",
                                            f"Invalid node id {n_id} coordinates: unconvertable expressions.\n"
                                            f"Coordinates: X {x_str}, Z: {z_str} \n"
                                            "Coordinates can be changed in Node Edit dialog")
                    if log:
                        self.mesh_drawing_ERROR_log.append(f"WARNING: Node id {n_id} error - unconvertable expressions: coordinates: X {x_str}, Z: {z_str}")
                else:
                    if MessageBox:
                        QMessageBox.warning(self, 
                                            f"Node id {n_id} error",
                                            f"Invalid node id {n_id} coordinates: missing symbol substitutions.\n"
                                            f"Detected {sorted(missing_symbols)} missing substitutions. All have been assigned a value equal to 1.0.\n"
                                            "Properties can be changed in Symbols dialog")
                    if log:
                        self.mesh_drawing_ERROR_log.append(f"WARNING: Node id {n_id} error - missing symbol substitutions:\n Detected {sorted(missing_symbols)} missing substitutions. All have been assigned a value equal to 1.0")
                # Update słownika
                symbol_subs.update(new_subs_dict)
                try:
                    x = float(x_expr.subs(symbol_subs))
                    z = float(z_expr.subs(symbol_subs))
                    return x, z, no_coords_flag
                except (ValueError, TypeError):
                    # Jeżeli w środku jest coś co psuje floata to trudno, zwracamy wartości fallbackowe, skoro to się uruchomiło to wiadomo, że coś trzeba poprawić.
                    return corrupt_data_fallback_coords(silent = True)  
                
        # wywoływanie odpowiedniej funkcji:
        if self.data_type == "symbolic":
            return get_symbolic_coords()
        else:
            return get_numerical_coords()

    # Funkcja podkreślająca węzeł:
    def draw_node_highlight(self, n_id, edge_color = 'green', marker_shape = 'o', marker_size = 6, highlight_text = "", font_size = 10, font_color = 'green'):
        x, z, no_coords_flag = self.get_node_coordinates(n_id, MessageBox = False)
        drawn_highlight = self.axes.plot(
                                x, z, 
                                marker = marker_shape, 
                                markeredgecolor = edge_color, 
                                markersize = marker_size, 
                                markerfacecolor = 'none',
                                linestyle = 'None' # upewniamy się, że rysuje sam punkt, bez linii
                            )
        drawn_highlight_text = self.axes.text(x + 0.1, z + 0.1, f"{highlight_text}", fontsize = font_size, color = font_color)
        return drawn_highlight, drawn_highlight_text

    # Podpora przegubowa nieprzesówna
    def draw_pinned_support(self, n_id, MessageBox = True, log = False):
        # Parametry wyciągane bezpośrednio ze słownika params
        # h wysokość trójkąta
        # w szerokość podstawy
        # Konwersja kąta ze stopni na radiany (dla wygody użytkownika GUI)
        x, z, no_node_flag = self.get_node_coordinates(n_id, MessageBox, log)
        def draw():
            # Pobieranie parametrów
            w = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_width'])
            h = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_height'])
            theta = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['rotation_angle']))
            h_ang = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_angle']))
            hatch_density = int(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_density'])
            support_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['support_color']
            marker_shape = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_shape']
            marker_size = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_size'])
            marker_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_color']
            marker_face_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_face_color']
            transparency = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['transparency'])
        
            # Rysowanie trójkąta
            # Zaczynamy w (0,0), idziemy do lewego dolnego rogu, potem prawego dolnego i wracamy do (0,0)
            x_t_flat = np.array([0, -w/2, w/2, 0])
            z_t_flat = np.array([0, -h, -h, 0])
            # Rysowanie kreskowania wraz z translacjami:
            x_h_final = []
            z_h_final = []
            x_htt = np.linspace(-0.75 * w, 0.75 * w, hatch_density) # punkty gdzie będzie startowało kresowanie
            for x_loc in x_htt:
                x_1 = x_loc
                z_1 = -h
                x_2 = x_loc - 0.5 * h / np.tan(h_ang)
                z_2 = -1.5 * h
                # translacja punktów
                x_1f = x_1 * np.cos(theta) - z_1 * np.sin(theta) + x
                z_1f = x_1 * np.sin(theta) + z_1 * np.cos(theta) + z
                x_2f = x_2 * np.cos(theta) - z_2 * np.sin(theta) + x
                z_2f = x_2 * np.sin(theta) + z_2 * np.cos(theta) + z
                x_h_final.append([x_1f, x_2f])
                z_h_final.append([z_1f, z_2f])

            # Prosta linia oddzielająca kreskowanie od trójkąta:
            x_l_flat = np.array([-0.75 * w, 0.75 * w])
            z_l_flat = np.array([-h, -h])
            
            # obrót o theta
            x_t_rot = x_t_flat * np.cos(theta) - z_t_flat * np.sin(theta)
            z_t_rot = x_t_flat * np.sin(theta) + z_t_flat * np.cos(theta)
            x_l_rot = x_l_flat * np.cos(theta) - z_l_flat * np.sin(theta)
            z_l_rot = x_l_flat * np.sin(theta) + z_l_flat * np.cos(theta)
    
            # Translacja (przesunięcie na współrzędne węzła):
            x_t_final = x_t_rot + x
            z_t_final = z_t_rot + z
            x_l_final = x_l_rot + x
            z_l_final = z_l_rot + z

            # Słownik drawn obj, zbiera wszystkie rysowania w jedno miejsce
            drawn_nodeOBJ_local = {}

            # Rysowanie trójkąta i kreski oddzielającej:
            drawn_nodeOBJ_local["support"] = self.axes.plot(x_t_final, z_t_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)
            drawn_nodeOBJ_local["separation"] = self.axes.plot(x_l_final, z_l_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)

            # Rysowanie kreskowania:
            for i, (x_h, z_h) in enumerate(zip(x_h_final, z_h_final)): # zip tworzy krotkę x_h, z_h aby dało się odwoływać do dwóch list w tej samej pętli:
                name_i = f"hatch_line_{i + 1}" 
                drawn_nodeOBJ_local[name_i] = self.axes.plot(x_h, z_h, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thinn_line'], alpha = transparency)

            # Rysowanie kółka przegubu na głównym węźle (x, z)
            drawn_nodeOBJ_local["node_mark"] = self.axes.plot(
                        x, z, 
                        marker = marker_shape, 
                        color = marker_color, 
                        markersize = marker_size, 
                        markerfacecolor = marker_face_color,
                        alpha = transparency,
                        linestyle='None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
            if no_node_flag:
                drawn_nodeOBJ_local['highlight'], drawn_nodeOBJ_local['highlight_text'] = self.draw_node_highlight(n_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = "CORRUPTED COORDINATES", font_size = 10, font_color = 'red')
            else:
                pass
            return drawn_nodeOBJ_local  # Zwracamy wynik z wewnątrz funkcji draw()

        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            QMessageBox.warning(self,
                                "Node object canvas failure",
                                f"Unexpected node visual parameter. \nTo prevent crashes visual node properties had been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.support_type['pinned_support']['v_params']
            self.nodeOBJ_visuals[n_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
    
    # Funkcja rysowania podpory przesównej:
    def draw_roller_support(self, n_id, MessageBox = True, log = False):
        # Ponieważ są dwie możliwości ustawienia podpory przesównej należy rozpoznać jaka jest to podpora 
        # aby w przystart_offsetku złych prametrów przypisać poprawne wartości domyślne
        s_type = self.nodeOBJ_visuals[n_id]['support_type']
        x, z, no_node_flag = self.get_node_coordinates(n_id, MessageBox, log)
        def draw():
            # Pobieranie parametrów
            w = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_width'])
            h = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_height'])
            theta = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['rotation_angle']))
            h_ang = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_angle']))
            hatch_density = int(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_density'])
            gap = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['gap'])
            support_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['support_color']
            marker_shape = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_shape']
            marker_size = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_size'])
            marker_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_color']
            marker_face_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_face_color']
            transparency = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['transparency'])

            # Punkty trójkąta:
            x_t_flat = np.array([0, -w/2, w/2, 0])
            z_t_flat = np.array([0, -h, -h, 0])
            # Rysowanie kreskowania wraz z translacjami:
            x_h_final = []
            z_h_final = []
            x_htt = np.linspace(-0.75 * w, 0.75 * w, int(hatch_density)) # punkty gdzie będzie startowało kresowanie
            for x_loc in x_htt:
                x_1 = x_loc
                z_1 = -h - gap
                x_2 = x_loc - 0.5 * h / np.tan(h_ang)
                z_2 = -1.5 * h - gap
                x_1f = x_1 * np.cos(theta) - z_1 * np.sin(theta) + x
                z_1f = x_1 * np.sin(theta) + z_1 * np.cos(theta) + z
                x_2f = x_2 * np.cos(theta) - z_2 * np.sin(theta) + x
                z_2f = x_2 * np.sin(theta) + z_2 * np.cos(theta) + z
                x_h_final.append([x_1f, x_2f])
                z_h_final.append([z_1f, z_2f])

            # Prosta linia oddzielająca kreskowanie od trójkąta:
            x_l_flat = np.array([-0.75 * w, 0.75 * w])
            z_l_flat = np.array([-h - gap, -h - gap])
            
            # obrót o theta
            x_t_rot = x_t_flat * np.cos(theta) - z_t_flat * np.sin(theta)
            z_t_rot = x_t_flat * np.sin(theta) + z_t_flat * np.cos(theta)
            x_l_rot = x_l_flat * np.cos(theta) - z_l_flat * np.sin(theta)
            z_l_rot = x_l_flat * np.sin(theta) + z_l_flat * np.cos(theta)
    
            # Translacja (przesunięcie na współrzędne węzła):
            x_t_final = x_t_rot + x
            z_t_final = z_t_rot + z
            x_l_final = x_l_rot + x
            z_l_final = z_l_rot + z

            # Słownik drawn obj, zbiera wszystkie rysowania w jedno miejsce
            drawn_nodeOBJ_local = {}

            # Rysowanie trójkąta i kreski oddzielającej:
            drawn_nodeOBJ_local["support"] = self.axes.plot(x_t_final, z_t_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)
            drawn_nodeOBJ_local["separation"] = self.axes.plot(x_l_final, z_l_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)

            # Rysowanie kreskowania:
            for i, (x_h, z_h) in enumerate(zip(x_h_final, z_h_final)): # zip tworzy krotkę x_h, z_h aby dało się odwoływać do dwóch list w tej samej pętli:
                name_i = f"hatch_line_{i + 1}" 
                drawn_nodeOBJ_local[name_i] = self.axes.plot(x_h, z_h, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thinn_line'], alpha = transparency)

            # Rysowanie kółka przegubu na głównym węźle (x, z)
            drawn_nodeOBJ_local["node_mark"] = self.axes.plot(
                        x, z, 
                        marker = marker_shape, 
                        color = marker_color, 
                        markersize = marker_size, 
                        markerfacecolor = marker_face_color,
                        alpha = transparency,
                        linestyle='None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
            if no_node_flag:
                drawn_nodeOBJ_local['highlight'], drawn_nodeOBJ_local['highlight_text'] = self.draw_node_highlight(n_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = "CORRUPTED COORDINATES", font_size = 10, font_color = 'red')
            else:
                pass
            return drawn_nodeOBJ_local  # Zwracamy wynik z wewnątrz funkcji draw()
        
        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            QMessageBox.warning(self,
                                "Node object canvas failure",
                                f"Unexpected node visual parameter. \nTo prevent crashes visual node properties had been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.support_type[s_type]['v_params']
            self.nodeOBJ_visuals[n_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
            
    # Funkcja rysowania "zamurowania":
    def draw_FIXED_support(self, n_id, MessageBox = True, log = False):
        x, z, no_node_flag = self.get_node_coordinates(n_id, MessageBox, log)
        def draw():
            # Pobieranie parametrów
            w = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_width'])
            h = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_height'])
            theta = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['rotation_angle']))
            h_ang = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_angle']))
            hatch_density = int(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_density'])
            support_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['support_color']
            marker_shape = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_shape']
            marker_size = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_size'])
            marker_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_color']
            marker_face_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_face_color']
            transparency = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['transparency'])

            # Rysowanie kreskowania wraz z translacjami:
            x_h_final = []
            z_h_final = []
            x_htt = np.linspace(-0.75 * w, 0.75 * w, int(hatch_density)) # punkty gdzie będzie startowało kresowanie
            for x_loc in x_htt:
                x_1 = x_loc
                z_1 = 0
                x_2 = x_loc - 0.5 * h / np.tan(h_ang)
                z_2 = -0.5 * h
                x_1f = x_1 * np.cos(theta) - z_1 * np.sin(theta) + x
                z_1f = x_1 * np.sin(theta) + z_1 * np.cos(theta) + z
                x_2f = x_2 * np.cos(theta) - z_2 * np.sin(theta) + x
                z_2f = x_2 * np.sin(theta) + z_2 * np.cos(theta) + z
                x_h_final.append([x_1f, x_2f])
                z_h_final.append([z_1f, z_2f])
            
            # Prosta linia
            x_l_flat = np.array([-0.75 * w, 0.75 * w])
            z_l_flat = np.array([0, 0])
            
            # obrót o theta
            x_l_rot = x_l_flat * np.cos(theta) - z_l_flat * np.sin(theta)
            z_l_rot = x_l_flat * np.sin(theta) + z_l_flat * np.cos(theta)
    
            # Translacja (przesunięcie na współrzędne węzła):
            x_l_final = x_l_rot + x
            z_l_final = z_l_rot + z

            # Słownik drawn obj, zbiera wszystkie rysowania w jedno miejsce
            drawn_nodeOBJ_local = {}
            
            # Rysowanie kreski oddzielającej:
            drawn_nodeOBJ_local["separation"] = self.axes.plot(x_l_final, z_l_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)
            # Rysowanie kreskowania:
            for i, (x_h, z_h) in enumerate(zip(x_h_final, z_h_final)): # zip tworzy krotkę x_h, z_h aby dało się odwoływać do dwóch list w tej samej pętli:
                name_i = f"hatch_line_{i + 1}"
                drawn_nodeOBJ_local[name_i] = self.axes.plot(x_h, z_h, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thinn_line'], alpha = transparency)

            # Rysowanie punktu na głównym węźle (x, z)
            drawn_nodeOBJ_local["node_mark"] = self.axes.plot(
                        x, z, 
                        marker = marker_shape, 
                        color = marker_color, 
                        markersize = marker_size, 
                        markerfacecolor = marker_face_color,
                        alpha = transparency,
                        linestyle='None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
            if no_node_flag:
                drawn_nodeOBJ_local['highlight'], drawn_nodeOBJ_local['highlight_text'] = self.draw_node_highlight(n_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = "CORRUPTED COORDINATES", font_size = 10, font_color = 'red')
            else:
                pass
            return drawn_nodeOBJ_local  # Zwracamy wynik z wewnątrz funkcji draw()

        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            QMessageBox.warning(self,
                                "Node object canvas failure",
                                f"Unexpected node visual parameter. \nTo prevent crashes visual node properties had been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.support_type['FIXED_support']['v_params']
            self.nodeOBJ_visuals[n_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
   
    # Funkcja rysowania rolki odbierającej moment ale przesównej:
    def draw_rollerFIX_support(self, n_id, MessageBox = True, log = False):
        # Ponieważ są dwie możliwości ustawienia podpory przesównej należy rozpoznać jaka jest to podpora 
        # aby w przystart_offsetku złych prametrów przypisać poprawne wartości domyślne
        x, z, no_node_flag = self.get_node_coordinates(n_id, MessageBox, log)
        s_type = self.nodeOBJ_visuals[n_id]['support_type']
        def draw():
            # Pobieranie parametrów
            w = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_width'])
            h = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_height'])
            theta = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['rotation_angle']))
            h_ang = np.radians(float(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_angle']))
            hatch_density = int(self.nodeOBJ_visuals[n_id]['visual_parameters']['hatch_density'])
            gap = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['gap'])
            support_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['support_color']
            marker_shape = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_shape']
            marker_size = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_size'])
            marker_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_color']
            marker_face_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_face_color']
            transparency = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['transparency'])

            # Punkty prostokąta
            # Zaczynamy w (0,0), idziemy do lewego dolnego rogu, potem prawego dolnego i wracamy do (0,0)
            x_t_flat = np.array([0, -w/1.5, -w/1.5, w/1.5, w/1.5, 0])
            z_t_flat = np.array([0, 0, -h, -h, 0, 0])

            # Rysowanie kreskowania wraz z translacjami:
            x_h_final = []
            z_h_final = []
            x_htt = np.linspace(-0.85 * w, 0.85 * w, int(hatch_density)) # punkty gdzie będzie startowało kresowanie
            for x_loc in x_htt:
                x_1 = x_loc
                z_1 = -h - gap
                x_2 = x_loc - 0.5 * h / np.tan(h_ang)
                z_2 = -1.5 * h - gap
                x_1f = x_1 * np.cos(theta) - z_1 * np.sin(theta) + x
                z_1f = x_1 * np.sin(theta) + z_1 * np.cos(theta) + z
                x_2f = x_2 * np.cos(theta) - z_2 * np.sin(theta) + x
                z_2f = x_2 * np.sin(theta) + z_2 * np.cos(theta) + z
                x_h_final.append([x_1f, x_2f])
                z_h_final.append([z_1f, z_2f])
            
            # Prosta linia oddzielająca kreskowanie od trójkąta:
            x_l_flat = np.array([-0.85 * w, 0.85 * w])
            z_l_flat = np.array([-h - gap, -h - gap])
            
            # obrót o theta
            x_t_rot = x_t_flat * np.cos(theta) - z_t_flat * np.sin(theta)
            z_t_rot = x_t_flat * np.sin(theta) + z_t_flat * np.cos(theta)
            x_l_rot = x_l_flat * np.cos(theta) - z_l_flat * np.sin(theta)
            z_l_rot = x_l_flat * np.sin(theta) + z_l_flat * np.cos(theta)
    
            # Translacja (przesunięcie na współrzędne węzła):
            x_t_final = x_t_rot + x
            z_t_final = z_t_rot + z
            x_l_final = x_l_rot + x
            z_l_final = z_l_rot + z
    
            # Słownik drawn obj, zbiera wszystkie rysowania w jedno miejsce
            drawn_nodeOBJ_local = {}

            # Rysowanie trójkąta i kreski oddzielającej:
            drawn_nodeOBJ_local["support"] = self.axes.plot(x_t_final, z_t_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)
            drawn_nodeOBJ_local["separation"] = self.axes.plot(x_l_final, z_l_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)

            # Rysowanie kreskowania:
            for i, (x_h, z_h) in enumerate(zip(x_h_final, z_h_final)): # zip tworzy krotkę x_h, z_h aby dało się odwoływać do dwóch list w tej samej pętli:
                name_i = f"hatch_line_{i + 1}" 
                drawn_nodeOBJ_local[name_i] = self.axes.plot(x_h, z_h, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thinn_line'], alpha = transparency)

            # Rysowanie punktu na głównym węźle (x, z)
            drawn_nodeOBJ_local["node_mark"] = self.axes.plot(
                        x, z, 
                        marker = marker_shape, 
                        color = marker_color, 
                        markersize = marker_size, 
                        markerfacecolor = marker_face_color,
                        alpha = transparency,
                        linestyle='None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
            if no_node_flag:
                drawn_nodeOBJ_local['highlight'], drawn_nodeOBJ_local['highlight_text'] = self.draw_node_highlight(n_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = "CORRUPTED COORDINATES", font_size = 10, font_color = 'red')
            else:
                pass
            return drawn_nodeOBJ_local  # Zwracamy wynik z wewnątrz funkcji draw()
        
        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            QMessageBox.warning(self,
                                "Node object canvas failure",
                                f"Unexpected node visual parameter. \nTo prevent crashes visual node properties had been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.support_type[s_type]['v_params']
            self.nodeOBJ_visuals[n_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
     
    # Funkcja rysowania podpory nieznanej:
    def draw_unknown_support(self, n_id, MessageBox = True, log = False):
        # h wysokość trójkąta
        # w szerokość podstawy
        # Konwersja kąta ze stopni na radiany (dla wygody użytkownika GUI)
        x, z, no_node_flag = self.get_node_coordinates(n_id, MessageBox, log)
        def draw():
            # Pobieranie parametrów
            w = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_width'])
            h = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['support_height'])
            support_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['support_color']
            marker_shape = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_shape']
            marker_size = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_size'])
            marker_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_color']
            marker_face_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_face_color']
            transparency = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['transparency'])
            # Punkty trójkąta 
            # Zaczynamy w (0,0), idziemy do lewego dolnego rogu, potem prawego dolnego i wracamy do (0,0)
            x_t_flat = np.array([0, -w/2, w/2, 0])
            z_t_flat = np.array([0, -h, -h, 0])
            # Nieznana podpora nie musi być obracana
            # Translacja (przesunięcie na współrzędne węzła):
            x_t_final = x_t_flat + x
            z_t_final = z_t_flat + z
            # Słownik drawn obj, zbiera wszystkie rysowania w jedno miejsce
            drawn_nodeOBJ_local = {}
            # Rysowanie trójkąta:
            drawn_nodeOBJ_local["support"] = self.axes.plot(x_t_final, z_t_final, color = support_color, linestyle = '-', linewidth = self.canvas_settings_dict['thicc_line'], alpha = transparency)
            # Rysowanie punktu na głównym węźle (x, z)
            drawn_nodeOBJ_local["node_mark"] = self.axes.plot(
                        x, z, 
                        marker = marker_shape, 
                        color = marker_color, 
                        markersize = marker_size, 
                        markerfacecolor = marker_face_color,
                        alpha = transparency,
                        linestyle='None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
            if no_node_flag:
                drawn_nodeOBJ_local['highlight'], drawn_nodeOBJ_local['highlight_text'] = self.draw_node_highlight(n_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = "CORRUPTED COORDINATES", font_size = 10, font_color = 'red')
            else:
                pass
            return drawn_nodeOBJ_local  # Zwracamy wynik z wewnątrz funkcji draw()
        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            QMessageBox.warning(self,
                                "Node object canvas failure",
                                f"Unexpected node visual parameter. \nTo prevent crashes visual node properties had been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.support_type['unknown_support']['v_params']
            self.nodeOBJ_visuals[n_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
             
    # Funkcja rysowania węzła z zablokowaną rotacją
    def draw_node_fix_rot(self, n_id, MessageBox = True, log = False):
        x, z, no_node_flag = self.get_node_coordinates(n_id, MessageBox, log)
        def draw():
            # Pobieranie parametrów
            marker_shape = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_shape']
            marker_size = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_size'])
            marker_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_color']
            marker_face_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_face_color']
            transparency = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['transparency'])

            # Słownik obiektów
            drawn_nodeOBJ_local = {}
        
            # Rysowanie punktu na głównym węźle (x, z)
            drawn_nodeOBJ_local["node_mark"] = self.axes.plot(
                        x, z, 
                        marker = marker_shape, 
                        color = marker_color, 
                        markersize = marker_size, 
                        markerfacecolor = marker_face_color,
                        alpha = transparency,
                        linestyle='None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
            if no_node_flag:
                drawn_nodeOBJ_local['highlight'], drawn_nodeOBJ_local['highlight_text'] = self.draw_node_highlight(n_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = "CORRUPTED COORDINATES", font_size = 10, font_color = 'red')
            else:
                pass
            return drawn_nodeOBJ_local  # Zwracamy wynik z wewnątrz funkcji draw()
        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            QMessageBox.warning(self,
                                "Node object canvas failure",
                                f"Unexpected node visual parameter. \nTo prevent crashes visual node properties had been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.support_type['Free']['v_params']
            self.nodeOBJ_visuals[n_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
    
    # Funkcja rysowania węzła wolnego:
    def draw_node_mark(self, n_id, MessageBox = True, log = False):
        x, z, no_node_flag = self.get_node_coordinates(n_id, MessageBox, log)
        def draw():
            # Pobieranie parametrów
            marker_shape = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_shape']
            marker_size = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_size'])
            marker_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_color']
            marker_face_color = self.nodeOBJ_visuals[n_id]['visual_parameters']['marker_face_color']
            transparency = float(self.nodeOBJ_visuals[n_id]['visual_parameters']['transparency'])

            # Słownik obiektów
            drawn_nodeOBJ_local = {}
        
            # Rysowanie punktu na głównym węźle (x, z)
            drawn_nodeOBJ_local["node_mark"] = self.axes.plot(
                        x, z, 
                        marker = marker_shape, 
                        color = marker_color, 
                        markersize = marker_size, 
                        markerfacecolor = marker_face_color,
                        alpha = transparency,
                        linestyle='None' # upewniamy się, że rysuje sam punkt, bez linii
                    )
            if no_node_flag:
                drawn_nodeOBJ_local['highlight'], drawn_nodeOBJ_local['highlight_text'] = self.draw_node_highlight(n_id, edge_color = 'red', marker_shape = 'o', marker_size = 40, highlight_text = "CORRUPTED COORDINATES", font_size = 10, font_color = 'red')
            else:
                pass
            return drawn_nodeOBJ_local  # Zwracamy wynik z wewnątrz funkcji draw()
        # Zabezpieczenie przed wadliwymi wartościami słownika danych wizualnych    
        try:
            # Próba rysowania i zwrócenie wygenerowanych obiektów
            return draw()
        except (KeyError, ValueError, TypeError) as e:
            # Informacja o błędzie
            QMessageBox.warning(self,
                                "Node object canvas failure",
                                f"Unexpected node visual parameter. \nTo prevent crashes visual node properties had been restored to default.\nError log:\n{e}")
            
            # Nadpisanie parametrów wizualnych na domyślne
            new_params = self.support_type['Free']['v_params']
            self.nodeOBJ_visuals[n_id]['visual_parameters'] = new_params.copy()
            
            # Próba rysowania z poprawnymi parametrami i zwrócenie obiektów
            return draw()
        
    # Funkcja dodająca label do węzła:
    def draw_node_label(self, n_id):
        # Funkcja wewnętrzna (domknięcie) – ma poprawny dostęp do n_x i n_z
        def draw_label():
            x_offset = float(self.nodeOBJ_visuals[n_id]['label']['x_offset'])
            z_offset = float(self.nodeOBJ_visuals[n_id]['label']['z_offset'])
            font_size = float(self.nodeOBJ_visuals[n_id]['label']['font_size'])
            color = self.nodeOBJ_visuals[n_id]['label']['color']
            transparency = float(self.nodeOBJ_visuals[n_id]['label']['transparency'])
            self.drawn_nodeOBJ[n_id]['label_obj'] = self.axes.text(n_x + x_offset, n_z + z_offset, f"n_{n_id}", fontsize=font_size, alpha = transparency, color = color)

        # Pobieranie współrzędnych węzła
        n_x, n_z, no_node_flag = self.get_node_coordinates(n_id, MessageBox = False)

        # Sprawdzamy, czy słownik ma już zapisane parametry labelu
        if "label" in self.nodeOBJ_visuals[n_id]:
            try:
                draw_label()
                return
            except Exception as error:
                QMessageBox.warning(self,
                                "Node label Error",
                                f"Couldnt load label for node id: {n_id}, unexpected parameters value\nError log:\n{error}")
                # Nadpisujemy uszkodzone parametry poprawnymi domyślnymi
                self.nodeOBJ_visuals[n_id]['label'] = self.default_node_label_params.copy()
                draw_label()
                return
        else:
            # Jeśli nie ma, przypisujemy domyślne i rysujemy
            self.nodeOBJ_visuals[n_id]['label'] = self.default_node_label_params.copy()
            draw_label()
            return

    # Uniwersalna funkcja rysująca i aktualizująca węzeł
    def draw_node(self, n_id, refresh_canvas = False, MessageBox = True, log = False):
        # Czyszczenie starego rysunku (odpala się przy edycji węzła)
        if n_id in self.drawn_nodeOBJ:
            # Pętla wyciąga zawartość ze słownika
            for item in self.drawn_nodeOBJ[n_id].values():
                # Funkcja usuwająca dowolny obiekt matplotlib
                self.remove_visualOBJ(item)
                    
        # Szukanie typu podpory
        s_type = self.nodeOBJ_visuals[n_id]['support_type']
        
        # Bezpieczne pobranie funkcji z fallbackiem na unknown_support w razie awarii klucza
        s_prop = self.support_type.get(s_type, self.support_type['unknown_support'])
        draw_func = s_prop["function"]
        
        # Wywołanie wyspecjalizowanej funkcji (bloki EAFP wewnątrz zadbają o poprawność)
        self.drawn_nodeOBJ[n_id] = draw_func(n_id, MessageBox, log)
        self.draw_node_label(n_id)
        # Warunkowe odświeżenie po pojedynczej edycji
        if refresh_canvas:
            self.draw()
        return

    # Funkcja rysująca zaznaczenie obiektu:
    def draw_OBJ_selection(self, obj_type = None, obj_id = None, cancel = False):
        if hasattr(self, "selected_obj") and self.selected_obj is not None:
            self.remove_visualOBJ(self.selected_obj)
            self.selected_obj = None
            if cancel or obj_type not in ("node", "element"):
                self.draw()
                return
        if obj_type == "element" and obj_id is not None:
            self.selected_obj, high_text = self.draw_element_highlight(obj_id, edge_color = "green", marker_shape = "s", marker_size = self.selection_size)
            self.draw()
            return
        elif obj_type == "node" and obj_id is not None:
            self.selected_obj, high_text = self.draw_node_highlight(obj_id, edge_color = "green", marker_shape = "s", marker_size = self.selection_size)
            self.draw()
            return
    
    def remove_visualOBJ(self, visualOBJ):
        if visualOBJ is None:
            return

        def _safe_remove(obj):
            # Sprawdzamy czy obiekt ma metodę remove
            if not hasattr(obj, "remove") or not callable(obj.remove):
                return

            # Sprawdzamy powiązanie z osią / figurą (bezpiecznie przez getattr)
            has_axes = getattr(obj, "axes", None) is not None
            get_fig = getattr(obj, "get_figure", None)
            has_fig = False
            if callable(get_fig):
                try:
                    has_fig = get_fig(root=False) is not None
                except TypeError:
                    # Starsze wersje Matplotlib nie mają parametru root
                    has_fig = get_fig() is not None
            elif getattr(obj, "figure", None) is not None:
                has_fig = True

            if has_axes or has_fig:
                try:
                    obj.remove()
                except (ValueError, NotImplementedError, KeyError, AttributeError):
                    pass

        # 1. Obsługa słowników
        if isinstance(visualOBJ, dict):
            for dict_val in list(visualOBJ.values()):
                self.remove_visualOBJ(dict_val)

        # 2. Obsługa list, krotek i zbiorów (pełna rekurencja)
        elif isinstance(visualOBJ, (list, tuple, set)):
            for item in list(visualOBJ):
                self.remove_visualOBJ(item)

        # 3. Pojedynczy obiekt Matplotlib
        else:
            _safe_remove(visualOBJ)
        

# =======================================================
# Inne funkcje walidacyjne jakich nie ma wewnątrz funkcji rysujących
# =======================================================

    # Sprawdzenie czy położenie belki/sprężyny jest poprawne dla siatki perpandicular beam:
    def check_element_positioning(self, e_id, MessageBox = True, log = False, return_flag = False):
        # Pobranie pozycji węzłów:
        flag = True
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox = False, log = False)
        vertical_elements = {"2N2DOF_Bar", "Spring"}
        horizontal_elements = {"2N4DOF_EB", "2N4DOF_T_EX", "2N4DOF_T_FI", "2N4DOF_T_RI", "2N6DOF_EB_Q"}
        if no_node_flag:
            if return_flag:
                flag = False
                return f"ERROR - element {e_id}: Unable to validate element location; connected nodes contain corrupted coordinates.", flag
            else:
                return
        # Sprawdzamy czy kąt jest odpowiedni:
        e_type = self.elements[e_id]["type"]
        # Ustawienie tolerancji:
        tolerance = 1e-5
        if e_type in vertical_elements:
            # funkcja math.isclose, sprawdza czy wyrażenie jest bliskie danej wartości (bo floaty nie są dokładne) zwraca true/false
            # dla pionowego kąta (czyli dla sprężyny/pręta) cosinus musi być zerowy:
            if not math.isclose(math.cos(theta), 0.0, abs_tol = tolerance):
                self.drawn_elementOBJ[e_id]["angle_error_highlight"], self.drawn_elementOBJ[e_id]["angle_error_text"] = self.draw_element_highlight(e_id, edge_color = 'red', marker_shape = 'o', marker_size = 6, highlight_text = "Unsuported angle", font_size = 10, font_color = 'red')
                if log:
                    self.mesh_drawing_ERROR_log.append(f"Element ID: {e_id} , type: {e_type} ---- {vertical_elements} elements in Parallel_Beam_Approach must be positioned vertically")
                if MessageBox:
                    QMessageBox.warning(self,
                                        f"Element ID: {e_id} unproper angle, type: {e_type}",
                                        f"{vertical_elements} elements in Parallel_Beam_Approach must be positioned vertically")
                if return_flag:
                    flag = False
                    text = f"ERROR - element ID: {e_id} , type: {e_type} ---- {vertical_elements} elements in Parallel_Beam_Approach must be positioned vertically"
                    return text, flag
                return 
        elif e_type in horizontal_elements:
            # funkcja math.isclose, sprawdza czy wyrażenie jest bliskie danej wartości (bo floaty nie są dokładne) zwraca true/false
            # dla pionowego kąta (czyli dla belek) sinus musi być zerowy:
            if not math.isclose(math.sin(theta), 0.0, abs_tol = tolerance):
                self.drawn_elementOBJ[e_id]["angle_error_highlight"], self.drawn_elementOBJ[e_id]["angle_error_text"] = self.draw_element_highlight(e_id, edge_color = 'red', marker_shape = 'o', marker_size = 6, highlight_text = "Unsuported angle", font_size = 10, font_color = 'red')
                if log:
                    self.mesh_drawing_ERROR_log.append(f"Element ID: {e_id} , type: {e_type} ---- {horizontal_elements} elements in Parallel_Beam_Approach must be positioned horzontally")
                if MessageBox:
                    QMessageBox.warning(self,
                                        f"Element ID: {e_id} unproper angle, type: {e_type}",
                                        f"{horizontal_elements} elements in Parallel_Beam_Approach must be positioned horizontally")
                if return_flag:
                    flag = False
                    text = f"ERROR - element ID: {e_id} , type: {e_type} ---- {horizontal_elements} elements in Parallel_Beam_Approach must be positioned horzontally"
                    return text, flag
                return
        else:
            if log:
                self.mesh_drawing_ERROR_log.append(f"Element ID: {e_id}: {e_type} in not supported by Parallel_Beam_Approach mesh type")
            if MessageBox:
                QMessageBox.warning(self,
                                    f"Element ID: {e_id} Element type: {e_type}",
                                    f"Elements supported by Parallel_Beam_Approach mesh type:\n"
                                    f"{horizontal_elements}, {vertical_elements}")
        if return_flag:
            return "", flag

    # Zbiorcza funkcja walidacji:
    def MASTER_validate(self, full_validation = False, float_converter = False, return_flag = False):
        master_flag = True
        master_log = ["=================================================",
                      "=================== VALIDATING MESH =================",
                      "================================================="]
        # walidacja słownika symboli:
        if self.data_type == "symbolic":
            flag, log = self.validate_symbol_subs(full_validation)
            if flag is False:
                master_flag = False
            master_log.append("")
            master_log.extend(log)

        # walidacja słownika materiałów
        flag, log = self.validate_user_materials(full_validation, float_converter)
        if flag is False:
            master_flag = False
        master_log.append("")
        master_log.extend(log)

        # walidacja słownika przekrojów poprzecznych
        flag, log = self.validate_cross_sections(full_validation, float_converter)
        if flag is False:
            master_flag = False
        master_log.append("")
        master_log.extend(log)

        # walidacja elementów:
        flag, log = self.validate_elements(full_validation, float_converter)
        if flag is False:
            master_flag = False
        master_log.append("")
        master_log.extend(log)

        # walidacja węzłów:
        flag, log = self.validate_nodes(full_validation, float_converter)
        if flag is False:
            master_flag = False
        master_log.append("")
        master_log.extend(log)

        
        if master_flag is True:
            master_log.extend(["", "======= MESH VALIDATION - Passed ======="])
        else:
            master_log.extend(["", "======= MESH VALIDATION - FAILED! ======="])
        # dla wczytywania siatki w load manager
        if return_flag:
            if master_flag:
                return master_flag
            else:
                loads_dialog = ListReportLog(self, self, title = "FAILED MESH VALIDATION!", 
                                             label_text = "Loads cannot be assigned to corrupted mesh file.\nValidation log:", 
                                             display_list = master_log, minimum_width = 500, minimum_height = 600)
                loads_dialog.exec()
                return master_flag
        # wywołanie w edytorze siatki
        # Wwołanie dialogu:
        dialog = ListReportLog(self, self, title = "Mesh validation", label_text = "validation log:", display_list = master_log, minimum_width = 500, minimum_height = 600)
        dialog.exec()
        return
        
    # WALIDACJA SŁOWNIKA SYMBOL SUBS:
    def validate_symbol_subs(self, full_validation = False):
        flag = True
        log = ["========= SYMBOL SUBSTITUTES VALIDATION ========="]
        if self.symbol_substitutes == {}:
            log.append("symbol substitute dict is empty, no problems occured")
            return flag, log
        try:
            for sym_type, sym_dict in self.symbol_substitutes.items():
                if full_validation:
                    log.append(f"- checking - {sym_type} substitutes:")
                try:
                    for sym, sym_val in sym_dict.items():
                        try:
                            float(sym_val)
                            if full_validation:
                                log.append(f"{sym}: {sym_val}")
                        except Exception:
                            flag = False
                            log.append(f"ERROR - {sym}: {sym_val} - unconvertable to float")
                except Exception:
                    flag = False
                    log.append(f"Unable to process {sym_type} symbols container: \n found dict: {sym_dict}")
        except Exception as e:
            flag = False
            log.append(f"Unable to process symbol substitute dict: \n {e}")
        if flag is True:
            log.append("=== No problems occured ===")
        else:
            log.append("=== FAILED VALIDATION! ===")

        return flag, log

    # Walidacja materiałów:
    def validate_user_materials(self, full_validation = False, float_converter = False):
        subs_dict = {"youngs_modulus": "pressure", 
                    "poissons_ratio": "poissons_ratio",
                    "density": "density"}
        flag = True
        log = ["========= USER DEFINED MATERIAL'S VALIDATION ========="]
        self.user_defined_materials_float = {}
        if self.user_defined_materials == {}:
            log.append("user defined material's dict is empty, no problems occured")
            return flag, log
        try:
            for mat_name, mat_dict in self.user_defined_materials.items():
                if float_converter:
                    self.user_defined_materials_float[mat_name] = {}
                if full_validation:
                    log.append(f"- checking - {mat_name} material:")
                try:
                    for mat_prop, prop_val in mat_dict.items():
                        if mat_prop != "name":
                            abs_val, val_flag = self.validate_val(val = prop_val, symbol_key = subs_dict[mat_prop])
                            if not val_flag:
                                flag = False
                                log.append(f"ERROR - material: {mat_name}, property: {mat_prop}: {prop_val} failed float convertion")
                            else:
                                if full_validation:
                                    log.append(f"{mat_prop}: {prop_val} = {abs_val}")
                                if float_converter:
                                    if mat_prop != "name":
                                        self.user_defined_materials_float[mat_name][mat_prop] = abs_val
                                    else:
                                        self.user_defined_materials_float[mat_name][mat_prop] = prop_val
                    if "name" not in mat_dict:
                        log.append(f"NOTE - material '{mat_name}' is missing 'name' property")
                    if "youngs_modulus" not in mat_dict:
                        flag = False
                        log.append(f"ERROR - material '{mat_name}' is missing 'youngs_modulus' property")
                    if "poissons_ratio" not in mat_dict:
                        flag = False
                        log.append(f"ERROR - material '{mat_name}' is missing 'poissons_ratio' property")
                    if "density" not in mat_dict:
                        flag = False
                        log.append(f"ERROR - material '{mat_name}' is missing 'density' property")
                except Exception:
                    flag = False
                    log.append(f"Unable to process {mat_name}: \n found dict: {mat_dict}")
        except Exception as e:
            flag = False
            log.append(f"Unable to process user material dict: \n {e}")

        if flag is True:
            log.append("=== No problems occured ===")
        else:
            log.append("=== FAILED VALIDATION! ===")
        
        return flag, log

    # Walidacja przekrojów poprzecznych:
    def validate_cross_sections(self, full_validation = False, float_converter = False):
        subs_dict = {"area": "area",
                    "inertia_y": "inertia_y",
                    "zuravsky_static_y": "zuravsky_static_y",
                    "max_z": "length",
                    "shear_width": "length",
                    "shear_correction_factor": "shear_correction_factor"}
        shapes = {'rectangle',
                'square',
                'circle',
                'circular_tube',
                'elliptical_tube',
                'rectangular_tube',
                'square_tube',
                'i_beam',
                't_beam',
                'u_channel',
                'direct_values'}
        flag = True
        log = ["========= CROSS SECTIONS VALIDATION ========="]
        self.cross_sections_float = {}
        if self.cross_sections == {}:
            flag = False
            log.append("ERROR - cross sections dict is empty")
            return flag, log
        try:
            skip = False
            for section_name, section_dict in self.cross_sections.items():
                if float_converter:
                    self.cross_sections_float[section_name] = copy.deepcopy(self.cross_sections[section_name])
                if full_validation:
                    log.append(f"- checking - {section_name} cross section:")
                if skip:
                    continue
                try:
                    if section_dict["system_section"] is True:
                        del self.cross_sections_float[section_name]
                        continue
                except Exception:
                    pass
                try:
                    for sec_prop, prop_dict in section_dict.items():
                        if sec_prop == "name":
                            continue
                        elif sec_prop == "shape_type":
                            if prop_dict not in shapes:
                                flag = False
                                log.append(f"ERROR - cross section {section_name}, shape: {prop_dict} is not supported \n available shapes: {shapes}")
                            else:
                                if full_validation:
                                    log.append(f"shape: {prop_dict} - supported")
                            continue
                        elif sec_prop == "shape_parameters":
                            try:
                                for dimen, dimen_val in prop_dict.items():
                                    sym_key = subs_dict[dimen] if section_dict["shape_type"] == "direct_values" else "length"                                  
                                    abs_val, val_flag = self.validate_val(val = dimen_val, symbol_key = sym_key)
                                    if not val_flag:
                                        flag = False
                                        log.append(f"ERROR {section_name} - {sec_prop} - {dimen}: {dimen_val}\n float convertion error")
                                    else:
                                        if full_validation:
                                            log.append(f"shape parameter: {dimen}: {dimen_val} = {abs_val}")
                                        if float_converter:
                                            self.cross_sections_float[section_name][sec_prop][dimen] = abs_val
                            except Exception:
                                flag = False
                                log.append(f"ERROR - Unable to process {section_name} - {sec_prop}")
                            continue
                        elif sec_prop == "properties":
                                try:
                                    for prop, prop_val in prop_dict.items():
                                        abs_val, val_flag = self.validate_val(val = prop_val, symbol_key = subs_dict[prop])
                                        if not val_flag:
                                            flag = False
                                            log.append(f"ERROR {section_name} - {sec_prop} - {prop}: {prop_val}\n float convertion error")
                                        else:
                                            if full_validation:
                                                log.append(f"property: {prop}: {prop_val} = {abs_val}")
                                            if float_converter:
                                                self.cross_sections_float[section_name][sec_prop][prop] = abs_val
                                except Exception:
                                    flag = False
                                    log.append(f"ERROR - Unable to process section: {section_name} - {sec_prop}")
                                continue 
                except Exception:
                    flag = False
                    log.append(f"Unable to process {sec_prop}: \n found dict: {prop_dict}")
                if float_converter:
                    try:
                        if self.data_type == "symbolic":
                            del self.cross_sections_float[section_name]["property_subs"]
                            if self.cross_sections_float[section_name]["shape_type"] == "direct_values":
                                params_copy = copy.deepcopy(self.cross_sections_float[section_name]["properties"])
                                self.cross_sections_float[section_name]["shape_parameters"] = params_copy
                    except Exception as e:
                        print(f"failed to alter cross section dict {section_name}:\n{e}")
        except Exception as e:
            flag = False
            log.append(f"Unable to process cross sections dict: \n {e}")

        if flag is True:
            log.append("=== No problems occured ===")
        else:
            log.append("=== FAILED VALIDATION! ===")
        
        return flag, log

    # Walidacja elementów:
    def validate_elements(self, full_validation = False, float_converter = False):
        flag = True
        log = ["========= ELEMENTS VALIDATION ========="]
        self.elements_float = {}
        self.connected_nodes = {}
        available_elements = {
            'Generalized_Coordinate_Framing' :[
                "2N6DOF_EB",
                "2N6DOF_T_EX",
                "2N6DOF_T_FI",
                "2N6DOF_T_RI",
                "2N8DOF_EB_Q",
                "2N4DOF_Truss",
                "Spring_2D",
                "unknown_element"
            ],
            'Parallel_Beam_Approach':[
                "2N4DOF_EB",
                "2N4DOF_T_EX",
                "2N4DOF_T_FI",
                "2N4DOF_T_RI",
                "2N6DOF_EB_Q",
                "2N2DOF_Bar",
                "Spring", 
                "unknown_element"     
            ]
        }
        if self.elements == {}:
            flag = False
            log.append("WARNING - MESH DOES NOT CONTAIN ELEMENTS")
            return flag, log
        # tworzenie słownika połączonych węzłów:
        try:
            for e_id, e_dict in self.elements.items():
                self.connected_nodes[e_id] = {e_dict["node_1_id"], e_dict["node_2_id"]}
        except Exception as e:
            flag = False
            log.append(f"ERROR - unable to process node connections, error log: \n {e}")
        try:
            for e_id, e_dict in self.elements.items():
                if float_converter:
                    self.elements_float[e_id] = copy.deepcopy(self.elements[e_id])
                if full_validation:
                    log.append(f"- checking - element ID {e_id}:")
                element_type = self.map_element_type(e_id, MessageBox = False, log = False)
                if element_type == "unknown_element":
                    flag = False
                    log.append(f"ERROR - element ID {e_id}, invalid element type: {e_dict["type"]}")
                else:
                    if full_validation:
                        log.append(f"mapped element type: {element_type}")
                if element_type not in available_elements[self.MainWindow.mesh_element_layout_type]:
                    flag = False
                    log.append(f"ERROR element type {e_dict["type"]} is not supported by {self.MainWindow.mesh_element_layout_type} mesh layout")
                # walidacja id węzłów:
                try:
                    # sprawdzenie czy nie ma połączeń z tymi samymi węzłami
                    local_connections = {e_dict["node_1_id"], e_dict["node_2_id"]}
                    if full_validation:
                        log.append(f"checking node connections: {local_connections}")
                    for c_id, e_connections in self.connected_nodes.items():
                        if e_connections == local_connections and c_id != e_id:
                            flag = False
                            log.append(f"ERROR - Overlaping elements:\n e_ID: {e_id} connecting {self.connected_nodes[e_id]} nodes \n e_ID: {c_id} connecting {self.connected_nodes[c_id]} nodes ")
                    if e_dict["node_1_id"] not in self.nodes.keys():
                        flag = False
                        log.append(f"ERROR - element ID {e_id} node_1_ID ({e_dict["node_1_id"]}) does not exist")
                    if e_dict["node_2_id"] not in self.nodes.keys():
                        flag = False
                        log.append(f"ERROR - element ID {e_id} node_2_ID ({e_dict["node_2_id"]}) does not exist")
                    try:
                        n_1_id = int(e_dict["node_1_id"])
                        n_2_id = int(e_dict["node_2_id"])
                        self.elements[e_id]["node_1_id"] = n_1_id
                        self.elements[e_id]["node_2_id"] = n_2_id
                        if float_converter:
                            self.elements_float[e_id]["node_1_id"] = n_1_id
                            self.elements_float[e_id]["node_2_id"] = n_2_id
                    except Exception:
                        flag = False
                        log.append(f"ERROR element ID {e_id} node IDs are not stored as integer values")
                except Exception:
                    flag = False
                    log.append(f"ERROR - unable to process node connections for element ID {e_id}")
                # Sprawdzenie materiału:
                try:
                    if e_dict["material"] not in (self.system_materials | self.user_defined_materials):
                        flag = False
                        log.append(f"ERROR - element ID {e_id} material '{e_dict["material"]}' not present in materials library")
                    elif full_validation:
                        log.append(f"material: {e_dict["material"]}")
                except Exception:
                    flag = False
                    log.append(f"ERROR - couldnt find material for element ID {e_id}")
                # Sprawdzenie czy przekrój istnieje
                try:
                    if e_dict["type"] not in ("Spring", "Spring_2D"):
                        if full_validation:
                            log.append(f"checking cross section: {e_dict["section_id"]}")
                        if e_dict["section_id"] not in self.cross_sections:
                            flag = False
                            log.append(f"ERROR - element ID {e_id} cross section {e_dict["section_id"]} is not defined")
                    elif e_dict["type"] in ("Spring", "Spring_2D"):
                        abs_val, val_flag = self.validate_val(e_dict["stiffness"], "stiffness")
                        if not val_flag:
                            flag = False
                            log.append(f"ERROR - element ID {e_id} striffness {e_dict["stiffness"]} is anconvertable to float")
                        else:
                            if full_validation:
                                log.append(f"striffness {e_dict["stiffness"]} absolute val: {abs_val}")
                            if float_converter:
                                self.elements_float[e_id]["stiffness"] = abs_val
                except Exception:
                    flag = False
                    log.append(f"ERROR - couldnt verify cross section/stiffness for element ID {e_id}")
                # Sprawdzenie wektora:
                if self.MainWindow.mesh_element_layout_type == "Parallel_Beam_Approach":
                    text, ret_flag = self.check_element_positioning(e_id, MessageBox = False, log = False, return_flag = True)
                    if not ret_flag:
                        flag = False
                        log.append(f"{text}")
                    elif full_validation:
                        log.append(f"checking Parallel_Beam_Approach positioning")
        except Exception as e:
            flag = False
            log.append(f"Unable to process elements dict: \n {e}")

        if flag is True:
            log.append("=== No problems occured ===")
        else:
            log.append("=== FAILED VALIDATION! ===")
        
        return flag, log

        # Walidacja węzłów:
    
    # Walidacja węzłów
    def validate_nodes(self, full_validation = False, float_converter = False):
        flag = True
        log = ["========= NODES VALIDATION ========="]
        self.nodes_float = {}
        if self.nodes == {}:
            flag = False
            log.append("WARNING - MESH DOES NOT CONTAIN NODES")
            return flag, log
        if hasattr(self, "connected_nodes") and self.connected_nodes is not None:
            check_connection = True
        else:
            check_connection = False
            flag = False
            log.append(f"Unable to validate node connections")
        try:
            for n_id, n_dict in self.nodes.items():
                if float_converter:
                    self.nodes_float[n_id] = copy.deepcopy(self.nodes[n_id])
                if full_validation:
                    log.append(f"- checking - node ID {n_id}:")
                try:
                    mapped_constraint = self.map_node_constraints(n_id, MessageBox = False, log = False)
                    if mapped_constraint == "unknown_support":
                        flag = False
                        log.append(f"ERROR - invalid constraint for node ID {n_id}:\n {n_dict["constraint"]} -- couldnt mapp support")
                    else:
                        if full_validation:
                            log.append(f"constraint: {n_dict["constraint"]}, mapped support: {mapped_constraint}")
                except Exception:
                    flag = False
                    log.append(f"Unable to process node ID {n_id}: \n found dict: {n_dict}")
                try:
                    for cord, cord_val in n_dict["coordinates"].items():
                        abs_val, val_flag = self.validate_val(cord_val, "length")
                        if not val_flag:
                            flag = False
                            log.append(f"ERROR - node ID {n_id} coordinate {cord} = {cord_val} - failed float convertion")
                        else:
                            if full_validation:
                                log.append(f"coordinate {cord}: val: {cord_val}, absolute value: {abs_val}")
                            if float_converter:
                                self.nodes_float[n_id]["coordinates"][cord] = abs_val
                except Exception:
                    flag = False
                    log.append(f"Unable to process node ID {n_id}: \n found dict: {n_dict}")

                # Sprawdzenie czy węzły nie nachodzą na siebie:
                if full_validation:
                    log.append("Checking node overlapping")
                n_coords = {"X": self.validate_val(n_dict["coordinates"]["X"], "length", True),
                            "Z": self.validate_val(n_dict["coordinates"]["Z"], "length", True)}
                for node_id, node_dict in self.nodes.items():
                    node_coords = {"X": self.validate_val(node_dict["coordinates"]["X"], "length", True),
                                   "Z": self.validate_val(node_dict["coordinates"]["Z"], "length", True)}
                    if n_coords == node_coords and n_id != node_id:
                        flag = False
                        log.append(f"ERROR - Nodes {n_id} and {node_id} have identical coordinates.")
                # Sprawdzenie czy węzeł ma przypisany element:
                if check_connection:
                    if full_validation:
                        log.append("Checking connections to elements")
                    con_flag = False
                    for e_id, el_nodes in self.connected_nodes.items():
                        if n_id in el_nodes:
                            con_flag = True
                            if full_validation:
                                log.append(f" - connected to element ID {e_id}")
                    if not con_flag:
                        flag = False
                        log.append(f"ERROR - node ID {n_id} is not connected to element")
        except Exception as e:
            flag = False
            log.append(f"Unable to process nodes dict: \n {e}")

        if flag is True:
            log.append("=== No problems occured ===")
        else:
            log.append("=== FAILED VALIDATION! ===")
        
        return flag, log

    #============================
    # Funkcja zapisania pliku siatki:
    def save_mesh_file(self, copy = False, float_converter = False, visuals = False):

        # Tworzenie odpowiednich słowników
        if float_converter:
            log, flag = self.validate_user_materials(full_validation = False, float_converter = True)
            log, flag = self.validate_cross_sections(full_validation = False, float_converter = True)
            log, flag = self.validate_nodes(full_validation = False, float_converter = True)
            log, flag = self.validate_elements(full_validation = False, float_converter = True)
            self.mesh_summary["data_type"] = "numerical"
            mat_dict = self.user_defined_materials_float
            cross_dict = self.cross_sections_float
            nodes_dict = self.nodes_float
            elements_dict = self.elements_float
        else:
            mat_dict = self.user_defined_materials
            cross_dict = self.cross_sections
            nodes_dict = self.nodes
            elements_dict = self.elements

        # Tworzenie list węzłów i elementów:
        elements_list = []
        nodes_list = []
        for e_dict in elements_dict.values():
            elements_list.append(e_dict)
        for n_dict in nodes_dict.values():
            nodes_list.append(n_dict)

        # Ustalenie odpowiedniego kontenera do zapisania
        if float_converter is False and self.data_type == "symbolic":
            dump = {"model_summary": self.mesh_summary,
                    "symbol_substitutes": self.symbol_substitutes,
                    "user_defined_materials": mat_dict,
                    "cross_sections": cross_dict,
                    "nodes": nodes_list,
                    "elements": elements_list}
        else:
            dump = {"model_summary": self.mesh_summary,
                    "user_defined_materials": mat_dict,
                    "cross_sections": cross_dict,
                    "nodes": nodes_list,
                    "elements": elements_list}
        if visuals:
            dump.update({"nodeOBJ_visuals": self.nodeOBJ_visuals,
                        "elementOBJ_visuals": self.elementOBJ_visuals})
        # Pobranie lokalizacji dla siatki:
        if not copy:
            mesh_path = self.MainWindow.full_mesh_path
            with open(mesh_path, "w", encoding="utf-8") as mesh:
                        json.dump(dump, mesh, indent = 4)
        else:
            base_path = self.MainWindow.full_mesh_path.removesuffix("_msh.json")
            mesh_path = base_path + "(copy)_msh.json"
            saved = False
            while not saved:
                try:
                    with open(mesh_path, "x", encoding="utf-8") as mesh:
                        json.dump(dump, mesh, indent = 4)
                        saved = True
                except FileExistsError:
                    base_path = mesh_path.removesuffix("_msh.json")
                    mesh_path = base_path + "_(copy)_msh.json"


    # ======================================================================= FUNKCJE EDYTORA OBCIĄŻEŃ
    def draw_simple_node(self, n_id):
        x, z, no_coords_flag = self.get_node_coordinates(n_id, MessageBox = False, log = False)
        marker = self.axes.plot(x, z, marker = self.load_mesh_visual_settings["node_marker"][self.map_node_constraints(n_id, MessageBox = False, log = False)],
                                color = self.load_mesh_visual_settings["simplified_mesh_color"],
                                markersize = self.load_mesh_visual_settings["simplified_node_size"],
                                alpha = self.load_mesh_visual_settings["simplified_mesh_transparency"],
                                linestyle = 'None')
        if self.load_mesh_visual_settings["draw_labels"] == "Show":
            if self.load_mesh_visual_settings["simplified_mesh_transparency"] + 0.2 < 1:
                transparency = self.load_mesh_visual_settings["simplified_mesh_transparency"] + 0.2
            else:
                transparency = self.load_mesh_visual_settings["simplified_mesh_transparency"]

            label = self.axes.text(x, z, f"n_{n_id}",
                                color = self.load_mesh_visual_settings["simplified_mesh_color"],
                                fontsize = self.load_mesh_visual_settings["simplified_label_size"],
                                alpha = self.load_mesh_visual_settings["simplified_mesh_transparency"],
                                bbox = dict(
                                        boxstyle = 'round,pad=0.15',
                                        fc = 'white',
                                        ec = 'none',
                                        alpha = transparency))

    def draw_simple_element(self, e_id):
        x_1, z_1, x_2, z_2, L, theta, no_node_flag = self.get_element_vector(e_id, MessageBox = False, log = False)
        line = self.axes.plot([x_1, x_2], [z_1, z_2],
                                linewidth = self.load_mesh_visual_settings["simplified_element_linewidth"],
                                color = self.load_mesh_visual_settings["simplified_mesh_color"],
                                alpha = self.load_mesh_visual_settings["simplified_mesh_transparency"],
                                linestyle  = self.load_mesh_visual_settings["simplified_element_linestyle"]) 
        if self.load_mesh_visual_settings["draw_labels"] == "Show":
            if self.load_mesh_visual_settings["simplified_mesh_transparency"] + 0.2 < 1:
                transparency = self.load_mesh_visual_settings["simplified_mesh_transparency"] + 0.2
            else:
                transparency = self.load_mesh_visual_settings["simplified_mesh_transparency"]
            x = (x_2 + x_1) / 2
            z = (z_2 + z_1) / 2
            label = self.axes.text(x, z, f"e_{e_id}",
                                   color = self.load_mesh_visual_settings["simplified_mesh_color"],
                                   fontsize = self.load_mesh_visual_settings["simplified_label_size"],
                                   alpha = self.load_mesh_visual_settings["simplified_mesh_transparency"],
                                   bbox = dict(
                                           boxstyle = 'round,pad=0.15',
                                           fc = 'white',
                                           ec = 'none',
                                           alpha = transparency))

    def draw_simple_mesh(self):
        self.clear_mesh()
        for n_id in self.nodes.keys():
            self.draw_simple_node(n_id)
        for e_id in self.elements.keys():
            self.draw_simple_element(e_id)
        self.canvas_settings()
        self.draw()
        self.simple_mesh_flag = True
        return


    
# ===============================================================================================
# ================ Kod właściwy=================
# ===============================================================================================

if __name__ == "__main__":
    # Tworzymy aplikację - to silnik całego GUI
    app = QApplication(sys.argv)
    
    # sprawdzenie czy program znalazł plik ikony
    if not os.path.exists(icon_path):
        print("BŁĄD: System nie widzi pliku ikony pod wskazaną ścieżką!")
    else:
        print("Sukces: Plik ikony został znaleziony w folderze.")
        
    # Tworzymy obiekt naszego okna
    okno = MainWindow()
    
    # Pokazujemy okno (domyślnie jest ukryte)
    okno.show()
    
    # Uruchamiamy pętlę zdarzeń i czekamy na zamknięcie
    sys.exit(app.exec())