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
from typing import Any, Optional
from _collections_abc import Callable

# ========================================
# Klasa dialogu zwracająca listę
# ========================================
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
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
# Klasa dialogu pomocniczego canvasa:
# ========================================
class AuxilaryCanvas(FigureCanvas):
    def __init__(self, parent = None, width = 3, height = 3, dpi = 100):
        self.fig = Figure(figsize = (width, height), dpi = dpi)
        super().__init__(self.fig)          
        self.setParent(parent)              
        self.axes = self.fig.add_subplot(1, 1, 1)
        self.axes.set_aspect("equal")
        self.axes.clear()


# ========================================
# Klasa dialogu pomocniczego z przyciskami:
# ========================================
class ButtonsDialog(QDialog):
    def __init__(self, parent = None, canvas = None, title = "No title", information_text = "Report:",  
                 buttons_dict = {"btn_1": "return_val_1", "btn_2": "return_val_2"}, visuals = {"btn_2": "red;white"},
                 font_size: int = 10, minimum_width = 200, minimum_height = 200):
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
            label = QLabel(f"{information_text}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label_font = label.font()
            label_font.setPointSize(font_size)
            label.setFont(label_font)
            self.main_layout.addWidget(label)
            self.return_val = None
    
            # Dolna sekcja:
            self.main_layout.addStretch()
            bottom_lt = QHBoxLayout()
            self.main_layout.addLayout(bottom_lt)
            self.btns_dict = {}
            for btn_name, return_val in buttons_dict.items():
                self.btns_dict[btn_name] = {"widget": QPushButton(f"{btn_name}"),
                                            "return_val": return_val}
                try:
                    if btn_name in visuals:
                         colors = visuals[btn_name]
                         color_1 = colors.split(";")[0]
                         color_2 = colors.split(";")[1]
                         self.btns_dict[btn_name]["widget"].setStyleSheet(f"background-color: {color_1}; color: {color_2}")
                except Exception as e:
                    print(f"{type(e).__name__}: {e}")

                bottom_lt.addWidget(self.btns_dict[btn_name]["widget"])
                self.btns_dict[btn_name]["widget"].clicked.connect(lambda checked = False, val = return_val: self.close_dialog(val)) 
                # Trzeba pierwszy argument przypisać, bo przycisk zawsze pierwszą wartość przypisuje false

    def close_dialog(self, return_val):
         self.return_val = return_val
         self.accept()


# ========================================
# Klasa pomocnicza budowania layoutów i widgetwów
# ========================================
class ToolsGUI:
    """
    Tools for making dialogs:
    - clearLayout
    - makeLayout1
    - makeLayout2 # not available
    - validateWidget
    """
    def __init__(self):
        return
    
    def clearLayout(self, lt_to_clear: QLayout):
        """
        Clears given layout with all of its components (widgets, spacers, sub layouts)
        """
        if lt_to_clear is None:
            return
        while lt_to_clear.count():
            item = lt_to_clear.takeAt(0)
            widget = item.widget()
            sub_layout = item.layout()
            if widget:
                widget.deleteLater()
            elif sub_layout:
                self.clearLayout(sub_layout)
            else:
                del item
        return

    
    def setStyleSheet(self, widget: QWidget, style: str):
        if style.strip() == "":
            widget.setStyleSheet("")
        else:
            try:
                bg_c = style.split(";")[0]
                text_c = style.split(";")[1]
                widget.setStyleSheet(f"background-color: {bg_c} ; color: {text_c}")
            except Exception as e:
                print(f"An error occured while setting style sheets for widget:\n" f"{type(e).__name__}: {e}")
                widget.setStyleSheet("")

    
    def setWidgetContents(self, widget: QLabel | QLineEdit | QPushButton | QComboBox | QListWidget,
                          textToSet: str | callable, styleOnMissingText: str = "", clearOldList: bool = True):
        """
        sets current text, changes lists, allows usung lambda function for lazy evaluation.
        styleSheet: Colors formatted as "<background>;<text>"
        (e.g., "red;white").
        """
        def TryAgain_ComboBox(text_to_fill):
            try:
                again_text = str(int(float(text_to_fill)))
                widget.setCurrentText(again_text)
            except Exception:
                pass

        def TryAgain_ListWidget(text_to_fill):
            try:
                again_text = str(int(text_to_fill))
                i = 0
                while i < widget.count():
                    if widget.item(i).text() == again_text:
                        widget.setCurrentRow(i)
                        break
                    i += 1
            except Exception:
                pass         

        try:
            newText = textToSet() if callable(textToSet) else textToSet 
            if isinstance(newText, list):
                newText = [str(row) for row in newText]
            else:
                newText = str(newText)
        except Exception:
            newText = ""
            self.setStyleSheet(widget, styleOnMissingText)

        if isinstance(widget, QLabel | QLineEdit | QPushButton):
            widget.setText(newText)

        elif isinstance(widget, QComboBox):
            if isinstance(newText, list):
                if clearOldList:
                    widget.clear()
                widget.addItems(newText)
            else:
                widget.setCurrentText(newText)
                if widget.findText(newText) == -1:
                    TryAgain_ComboBox(newText)

        elif isinstance(widget, QListWidget):
            if isinstance(newText, list):
                if clearOldList:
                    widget.clear()
                widget.addItems(newText)
            else:
                found = False
                i = 0
                while i < widget.count():
                    if widget.item(i).text() == newText:
                        widget.setCurrentRow(i)
                        found = True
                        break
                    i += 1
                if not found:
                    TryAgain_ListWidget(newText)

    
    def makeLayout1(self, parent_lt: QHBoxLayout, widget: QWidget,
                    sub_layout: QHBoxLayout,
                    label_txt: str, 
                    widget_contents: str | list | callable,
                    set_widgetItem: str = "",
                    add_stretch: bool = True,
                    font_size: int = 10,
                    label_styleSheet: str = "",
                    widget_styleSheet: str = "",
                    styleOnMissingText: str = "",
                    return_widget: bool = True,
                    return_layout: bool = False,
                    return_label: bool = False) -> None | QWidget | tuple[QLayout, QWidget] | tuple[QLayout, QLabel, QWidget] | tuple[QLabel, QWidget]:
        """
        Creates a simple horizontal or vertical layout with a QLabel and a QWidget.
        supported widgets: QLabel | QLineEdit | QPushButton | QComboBox | QListWidget

        Layout structure:
            QLabel(label_txt) | QWidget(widget_txt)

        Args:
            label_styleSheet: Colors formatted as "<background>;<text>"
              (e.g., "red;white").
            widget_styleSheet: Colors formatted as "<background>;<text>"
              (e.g., "white;black").
        """
        parent_lt.addLayout(sub_layout)
        # 1st widget
        label = QLabel()
        self.setStyleSheet(label, label_styleSheet)
        self.setWidgetContents(label, label_txt, styleOnMissingText)
        label_font = label.font()
        label_font.setPointSize(font_size)
        label.setFont(label_font)
        # 2nd widget
        self.setStyleSheet(widget, widget_styleSheet)
        self.setWidgetContents(widget, widget_contents, styleOnMissingText)
        if set_widgetItem:
            self.setWidgetContents(widget, set_widgetItem, styleOnMissingText)
        widget_font = widget.font()
        widget_font.setPointSize(font_size)
        widget.setFont(widget_font)
        # layout:
        sub_layout.addWidget(label)
        sub_layout.addWidget(widget)
        if add_stretch:
            sub_layout.addStretch()
        returns = []
        if return_layout:
            returns.append(sub_layout)
        if return_label:
            returns.append(label)
        if return_widget:
            returns.append(widget)
        if not returns:
            return
        elif len(returns) == 1:
            return returns[0]
        else:
            return tuple(returns)

    
    def validateWidget(self, widget: QLabel | QLineEdit | QPushButton | QComboBox,
                    validationFunc: Callable[[], Any],
                    styleOnPassed: str = "", styleOnFailed: str = "red;white",
                    return_val: bool = False, return_flag: bool = True) -> Any | bool | tuple[Any, bool] | None:
        """Sets style sheet on a widget according to the provided validation function.

        Args:
            validationFunc: Callable returning either `bool` or `tuple[val, bool]`.
            styleOnPassed: Colors formatted as "<background>;<text>" when valid.
            styleOnFailed: Colors formatted as "<background>;<text>" when invalid.
        """
        res = validationFunc()
        if isinstance(res, tuple):
            val, flag = res
        else:
            val, flag = res, bool(res)

        style_sheet = styleOnPassed if flag else styleOnFailed
        self.setStyleSheet(widget, style_sheet)

        if return_val and return_flag:
            return val, flag
        elif return_flag:
            return flag
        elif return_val:
            return val
        return None
                        
        

        

