import sys
import os
import marshal
import base64
import zlib
import binascii
import random
import string
import re
import ast
import json
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QCheckBox, QSpinBox, QTextEdit, QFileDialog,
                            QGroupBox, QMessageBox, QStatusBar, QFrame,
                            QComboBox, QTabWidget)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QPoint, QTimer, QSettings
from PySide6.QtGui import QColor, QPalette, QFont, QPainter, QLinearGradient
from translations import TRANSLATIONS

class LanguageComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._icon_path = parent._icon_path if parent else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        arrow_path = os.path.join(self._icon_path, 'arrow.svg').replace('\\', '/')
        
        self.setFixedWidth(120)
        self.addItem("English", "en")
        self.addItem("Русский", "ru")
        
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: #2b2b2b;
                color: white;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 5px 10px;
                min-height: 30px;
            }}
            QComboBox:hover {{
                border: 2px solid #2d5af5;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: url("{arrow_path}");
                width: 12px;
                height: 12px;
            }}
            QComboBox::down-arrow:hover {{
                image: url("{arrow_path}");
            }}
            QComboBox QAbstractItemView {{
                background-color: #2b2b2b;
                color: white;
                selection-background-color: #2d5af5;
                selection-color: white;
                border: 2px solid #555555;
                border-radius: 5px;
            }}
        """)

class ModernButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumHeight(40)
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._animation.setDuration(150)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d5af5;
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4169e1;
            }
            QPushButton:pressed {
                background-color: #1e3cad;
            }
        """)

class ModernCheckBox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
                color: #ffffff;
                font-size: 13px;
                min-height: 25px;
                padding-right: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #555555;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background-color: #2d5af5;
                border: 2px solid #2d5af5;
                image: url(checkmark.svg);
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2d5af5;
            }
        """)

class ModernGroupBox(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QGroupBox {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 6px;
                margin-top: 1.2em;
                padding: 6px;
                font-size: 13px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 4px;
                top: -6px;
                background-color: #1e1e1e;
            }
        """)

class ModernSpinBox(QSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QSpinBox {
                background-color: #2b2b2b;
                border: 2px solid #333333;
                border-radius: 6px;
                color: white;
                padding: 4px;
                min-width: 80px;
                min-height: 30px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                background-color: #2d5af5;
                border-radius: 4px;
                margin: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #4169e1;
            }
        """)

class ModernLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                border: 2px solid #333333;
                border-radius: 8px;
                color: white;
                padding: 8px;
                min-height: 40px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #2d5af5;
            }
        """)

class ModernTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 10px;
                color: white;
                padding: 10px;
                font-size: 13px;
                selection-background-color: #2d5af5;
            }
        """)

class EncoderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.settings = QSettings('SimpleEncoder', 'SimpleEncoderApp')
        self.current_language = self.settings.value('language', 'en')
        
        self._icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        
        self.setWindowTitle(self.tr('window_title'))
        self.setMinimumSize(900, 700)  # Уменьшаем размер окна
        
        self.set_dark_theme()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(5)
        lang_label = QLabel(self.tr('language') + ":")
        self.lang_combo = LanguageComboBox(self)
        index = self.lang_combo.findData(self.current_language)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        
        file_layout = QHBoxLayout()
        file_layout.setSpacing(5)
        self.input_path = ModernLineEdit()
        self.input_path.setPlaceholderText("Select input Python file...")
        self.browse_button = ModernButton("Browse")
        self.browse_button.setFixedWidth(80)
        self.browse_button.clicked.connect(self.select_input_file)
        file_layout.addWidget(self.input_path)
        file_layout.addWidget(self.browse_button)
        
        header_layout.addLayout(lang_layout, 1)
        header_layout.addLayout(file_layout, 4)
        main_layout.addLayout(header_layout)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)
        
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)
        
        basic_group = ModernGroupBox("Basic Methods")
        basic_layout = QVBoxLayout()
        basic_layout.setSpacing(5)
        
        self.use_marshal = ModernCheckBox("Marshal")
        self.use_base64 = ModernCheckBox("Base64")
        self.use_zlib = ModernCheckBox("Zlib")
        self.use_binascii = ModernCheckBox("Binascii")
        self.use_compile = ModernCheckBox("Compile")
        
        self.use_marshal.setChecked(True)
        self.use_base64.setChecked(True)
        self.use_zlib.setChecked(True)
        
        for widget in [self.use_marshal, self.use_base64, self.use_zlib, 
                      self.use_binascii, self.use_compile]:
            basic_layout.addWidget(widget)
        
        basic_group.setLayout(basic_layout)
        left_panel.addWidget(basic_group)
        
        additional_group = ModernGroupBox("Additional Options")
        additional_layout = QVBoxLayout()
        additional_layout.setSpacing(5)
        
        self.use_encryption = ModernCheckBox("String Encryption")
        self.use_junk = ModernCheckBox("Add Junk Code")
        self.use_rename = ModernCheckBox("Rename Variables")
        self.use_compress = ModernCheckBox("Maximum Compression")
        
        for widget in [self.use_encryption, self.use_junk, 
                      self.use_rename, self.use_compress]:
            additional_layout.addWidget(widget)
        
        additional_group.setLayout(additional_layout)
        left_panel.addWidget(additional_group)
        
        advanced_group = ModernGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(5)
        
        layers_layout = QHBoxLayout()
        layers_layout.setSpacing(5)
        self.layers_label = QLabel("Layers:")
        self.layers_spin = ModernSpinBox()
        self.layers_spin.setRange(1, 10)
        self.layers_spin.setValue(1)
        layers_layout.addWidget(self.layers_label)
        layers_layout.addWidget(self.layers_spin)
        
        junk_layout = QHBoxLayout()
        junk_layout.setSpacing(5)
        self.junk_label = QLabel("Junk Size:")
        self.junk_spin = ModernSpinBox()
        self.junk_spin.setRange(0, 1000)
        self.junk_spin.setValue(100)
        junk_layout.addWidget(self.junk_label)
        junk_layout.addWidget(self.junk_spin)
        
        advanced_layout.addLayout(layers_layout)
        advanced_layout.addLayout(junk_layout)
        advanced_group.setLayout(advanced_layout)
        left_panel.addWidget(advanced_group)
        
        left_panel.addStretch()
        
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)
        
        output_group = ModernGroupBox("Output Settings")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(5)
        
        filename_layout = QHBoxLayout()
        filename_layout.setSpacing(5)
        filename_label = QLabel("Filename:")
        self.output_filename = ModernLineEdit()
        self.output_filename.setPlaceholderText("Enter output filename")
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.output_filename)
        
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(5)
        dir_label = QLabel("Directory:")
        self.output_dir = ModernLineEdit()
        self.output_dir.setPlaceholderText("Output directory")
        browse_dir_btn = ModernButton("...")
        browse_dir_btn.setFixedWidth(40)
        browse_dir_btn.clicked.connect(self.select_output_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.output_dir)
        dir_layout.addWidget(browse_dir_btn)
        
        self.overwrite_existing = ModernCheckBox("Overwrite existing files")
        self.create_backup = ModernCheckBox("Create backup")
        
        output_layout.addLayout(filename_layout)
        output_layout.addLayout(dir_layout)
        output_layout.addWidget(self.overwrite_existing)
        output_layout.addWidget(self.create_backup)
        output_group.setLayout(output_layout)
        right_panel.addWidget(output_group)
        
        self.result_group = ModernGroupBox("Result")
        result_layout = QVBoxLayout()
        result_layout.setSpacing(5)
        
        self.result_text = ModernTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        result_layout.addWidget(self.result_text)
        
        self.result_group.setLayout(result_layout)
        right_panel.addWidget(self.result_group)
        
        content_layout.addLayout(left_panel, 2)
        content_layout.addLayout(right_panel, 3)
        
        main_layout.addLayout(content_layout)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.encode_button = ModernButton("Encode")
        self.encode_button.setMinimumWidth(120)
        self.encode_button.clicked.connect(self.encode_with_animation)
        
        self.clear_button = ModernButton("Clear")
        self.clear_button.setMinimumWidth(120)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        self.clear_button.clicked.connect(self.clear_all)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.encode_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #1a1a1a;
                color: white;
                padding: 5px;
                font-size: 13px;
            }
        """)
        self.setStatusBar(self.statusBar)
        
        checkmark_path = os.path.join(self._icon_path, 'checkmark.svg').replace('\\', '/')
        arrow_path = os.path.join(self._icon_path, 'arrow.svg').replace('\\', '/')
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #121212;
            }}
            QWidget {{
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}
            QLabel {{
                padding: 2px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #555555;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #2b2b2b;
            }}
            QCheckBox::indicator:checked {{
                background-color: #2d5af5;
                border: 2px solid #2d5af5;
                image: url("{checkmark_path}");
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid #2d5af5;
            }}
            QComboBox::down-arrow {{
                image: url("{arrow_path}");
                width: 12px;
                height: 12px;
            }}
        """)
        
        self.retranslateUi()
        
    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(18, 18, 18))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(27, 27, 27))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(27, 27, 27))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        self.setPalette(palette)
        
    def create_language_selector(self, parent_layout):
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(10)
        
        lang_label = QLabel(self.tr('language') + ":")
        lang_label.setFont(QFont("Segoe UI", 10))
        
        self.lang_combo = LanguageComboBox(self)
        
        index = self.lang_combo.findData(self.current_language)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
        
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        parent_layout.addLayout(lang_layout)
    
    def tr(self, key):
        return TRANSLATIONS[self.current_language].get(key, key)
    
    def change_language(self, index):
        self.current_language = self.lang_combo.itemData(index)
        self.settings.setValue('language', self.current_language)
        self.retranslateUi()
    
    def retranslateUi(self):
        self.setWindowTitle(self.tr('window_title'))
        
        self.input_path.setPlaceholderText(self.tr('select_file_placeholder'))
        self.browse_button.setText(self.tr('browse_button'))
        
        self.use_marshal.setText(self.tr('use_marshal'))
        self.use_base64.setText(self.tr('use_base64'))
        self.use_zlib.setText(self.tr('use_zlib'))
        self.use_binascii.setText(self.tr('use_binascii'))
        self.use_compile.setText(self.tr('use_compile'))
        
        self.use_encryption.setText(self.tr('use_encryption'))
        self.use_junk.setText(self.tr('use_junk'))
        self.use_rename.setText(self.tr('use_rename'))
        self.use_compress.setText(self.tr('use_compress'))
        
        self.layers_label.setText(self.tr('encoding_layers'))
        self.junk_label.setText(self.tr('junk_code_size'))
        
        self.overwrite_existing.setText(self.tr('overwrite_existing'))
        self.create_backup.setText(self.tr('create_backup'))
        
        self.encode_button.setText(self.tr('encode_button'))
        self.clear_button.setText(self.tr('clear_button'))

    def create_file_section(self, parent_layout):
        self.file_group = ModernGroupBox("File Selection")
        file_layout = QHBoxLayout()
        file_layout.setSpacing(10)
        
        self.input_path = ModernLineEdit()
        self.input_path.setPlaceholderText("Select input Python file...")
        self.browse_button = ModernButton("Browse")
        self.browse_button.clicked.connect(self.select_input_file)
        
        file_layout.addWidget(self.input_path)
        file_layout.addWidget(self.browse_button)
        
        self.file_group.setLayout(file_layout)
        parent_layout.addWidget(self.file_group)
        
    def create_settings_tabs(self, parent_layout):
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(400)  # Уменьшаем минимальную высоту вкладок
        
        encoding_tab = QWidget()
        encoding_layout = QVBoxLayout(encoding_tab)
        encoding_layout.setSpacing(10)
        encoding_layout.setContentsMargins(10, 10, 10, 10)
        
        encoding_scroll = QWidget()
        encoding_scroll_layout = QVBoxLayout(encoding_scroll)
        encoding_scroll_layout.setSpacing(10)
        encoding_scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_encoding_options(encoding_scroll_layout)
        self.create_advanced_settings(encoding_scroll_layout)
        encoding_scroll_layout.addStretch()
        
        encoding_layout.addWidget(encoding_scroll)
        self.tabs.addTab(encoding_tab, "Encoding")
        
        output_tab = QWidget()
        output_layout = QVBoxLayout(output_tab)
        output_layout.setSpacing(10)
        output_layout.setContentsMargins(10, 10, 10, 10)
        
        output_scroll = QWidget()
        output_scroll_layout = QVBoxLayout(output_scroll)
        output_scroll_layout.setSpacing(10)
        output_scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_output_settings(output_scroll_layout)
        output_scroll_layout.addStretch()
        
        output_layout.addWidget(output_scroll)
        self.tabs.addTab(output_tab, "Output")
        
        exe_tab = QWidget()
        exe_layout = QVBoxLayout(exe_tab)
        exe_layout.setSpacing(10)
        exe_layout.setContentsMargins(10, 10, 10, 10)
        
        exe_scroll = QWidget()
        exe_scroll_layout = QVBoxLayout(exe_scroll)
        exe_scroll_layout.setSpacing(10)
        exe_scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        self.create_exe_settings(exe_scroll_layout)
        exe_scroll_layout.addStretch()
        
        exe_layout.addWidget(exe_scroll)
        self.tabs.addTab(exe_tab, "EXE Options")
        
        parent_layout.addWidget(self.tabs)

    def create_encoding_options(self, parent_layout):
        self.options_group = ModernGroupBox("Encoding Options")
        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        options_layout.setContentsMargins(10, 10, 10, 10)
        
        basic_layout = QVBoxLayout()
        basic_layout.setSpacing(8)
        self.basic_label = QLabel("Basic Methods:")
        self.basic_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self.use_marshal = ModernCheckBox("Marshal")
        self.use_marshal.setToolTip("Use marshal module for bytecode serialization")
        
        self.use_base64 = ModernCheckBox("Base64")
        self.use_base64.setToolTip("Encode using base64 encoding")
        
        self.use_zlib = ModernCheckBox("Zlib")
        self.use_zlib.setToolTip("Apply zlib compression to reduce file size")
        
        self.use_binascii = ModernCheckBox("Binascii")
        self.use_binascii.setToolTip("Convert to hexadecimal representation")
        
        self.use_compile = ModernCheckBox("Compile")
        self.use_compile.setToolTip("Compile source to Python bytecode")
        
        self.use_marshal.setChecked(True)
        self.use_base64.setChecked(True)
        self.use_zlib.setChecked(True)
        
        for widget in [self.basic_label, self.use_marshal, self.use_base64, 
                      self.use_zlib, self.use_binascii, self.use_compile]:
            basic_layout.addWidget(widget)
        basic_layout.addStretch()
        
        additional_layout = QVBoxLayout()
        additional_layout.setSpacing(8)
        self.additional_label = QLabel("Additional Options:")
        self.additional_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self.use_encryption = ModernCheckBox("String Encryption")
        self.use_encryption.setToolTip("Encrypt string literals in the code")
        
        self.use_junk = ModernCheckBox("Add Junk Code")
        self.use_junk.setToolTip("Add random code to obfuscate the original")
        
        self.use_rename = ModernCheckBox("Rename Variables")
        self.use_rename.setToolTip("Rename variables to make code harder to read")
        
        self.use_compress = ModernCheckBox("Maximum Compression")
        self.use_compress.setToolTip("Use maximum compression level for smaller file size")
        
        for widget in [self.additional_label, self.use_encryption, self.use_junk,
                      self.use_rename, self.use_compress]:
            additional_layout.addWidget(widget)
        additional_layout.addStretch()
        
        options_layout.addLayout(basic_layout, stretch=1)
        options_layout.addLayout(additional_layout, stretch=1)
        
        self.options_group.setLayout(options_layout)
        parent_layout.addWidget(self.options_group)

    def create_advanced_settings(self, parent_layout):
        self.advanced_group = ModernGroupBox("Advanced Settings")
        advanced_layout = QHBoxLayout()
        advanced_layout.setSpacing(50)
        advanced_layout.setContentsMargins(20, 20, 20, 20)
        
        layers_layout = QHBoxLayout()
        layers_layout.setSpacing(15)
        self.layers_label = QLabel("Encoding Layers:")
        self.layers_spin = ModernSpinBox()
        self.layers_spin.setRange(1, 10)
        self.layers_spin.setValue(1)
        self.layers_spin.setMinimumWidth(100)
        layers_layout.addWidget(self.layers_label)
        layers_layout.addWidget(self.layers_spin)
        layers_layout.addStretch()
        
        junk_layout = QHBoxLayout()
        junk_layout.setSpacing(15)
        self.junk_label = QLabel("Junk Code Size:")
        self.junk_spin = ModernSpinBox()
        self.junk_spin.setRange(0, 1000)
        self.junk_spin.setValue(100)
        self.junk_spin.setMinimumWidth(100)
        junk_layout.addWidget(self.junk_label)
        junk_layout.addWidget(self.junk_spin)
        junk_layout.addStretch()
        
        advanced_layout.addLayout(layers_layout)
        advanced_layout.addLayout(junk_layout)
        
        self.advanced_group.setLayout(advanced_layout)
        parent_layout.addWidget(self.advanced_group)

    def create_output_settings(self, parent_layout):
        output_group = ModernGroupBox("Output File Settings")
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        filename_layout = QHBoxLayout()
        filename_layout.setSpacing(15)
        filename_label = QLabel("Output filename:")
        filename_label.setMinimumWidth(120)
        self.output_filename = ModernLineEdit()
        self.output_filename.setPlaceholderText("Enter output filename (without extension)")
        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.output_filename)
        
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(15)
        dir_label = QLabel("Output directory:")
        dir_label.setMinimumWidth(120)
        self.output_dir = ModernLineEdit()
        self.output_dir.setPlaceholderText("Leave empty for same directory as input")
        browse_dir_btn = ModernButton("Browse")
        browse_dir_btn.setFixedWidth(100)
        browse_dir_btn.clicked.connect(self.select_output_dir)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.output_dir)
        dir_layout.addWidget(browse_dir_btn)
        
        options_layout = QVBoxLayout()
        options_layout.setSpacing(15)
        self.overwrite_existing = ModernCheckBox("Overwrite existing files")
        self.create_backup = ModernCheckBox("Create backup of existing files")
        options_layout.addWidget(self.overwrite_existing)
        options_layout.addWidget(self.create_backup)
        
        layout.addLayout(filename_layout)
        layout.addLayout(dir_layout)
        layout.addLayout(options_layout)
        
        output_group.setLayout(layout)
        parent_layout.addWidget(output_group)

    def create_exe_settings(self, parent_layout):
        exe_group = ModernGroupBox("EXE Compilation Settings")
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.compile_to_exe = ModernCheckBox("Compile to EXE")
        self.compile_to_exe.stateChanged.connect(self.toggle_exe_options)
        
        exe_options_layout = QVBoxLayout()
        exe_options_layout.setSpacing(15)
        
        icon_layout = QHBoxLayout()
        icon_layout.setSpacing(15)
        icon_label = QLabel("Icon file:")
        icon_label.setMinimumWidth(120)
        self.icon_path = ModernLineEdit()
        self.icon_path.setPlaceholderText("Select .ico file (optional)")
        browse_icon_btn = ModernButton("Browse")
        browse_icon_btn.setFixedWidth(100)
        browse_icon_btn.clicked.connect(self.select_icon_file)
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.icon_path)
        icon_layout.addWidget(browse_icon_btn)
        
        self.hide_console = ModernCheckBox("Hide console window")
        self.one_file = ModernCheckBox("Create single file")
        self.one_file.setChecked(True)
        
        self.uac_admin = ModernCheckBox("Request admin privileges")
        self.add_version = ModernCheckBox("Add version info")
        

        version_layout = QHBoxLayout()
        version_layout.setSpacing(15)
        version_label = QLabel("Version:")
        version_label.setMinimumWidth(120)
        self.version_number = ModernLineEdit()
        self.version_number.setPlaceholderText("1.0.0")
        self.version_number.setMaximumWidth(150)
        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_number)
        version_layout.addStretch()
        
        company_layout = QHBoxLayout()
        company_layout.setSpacing(15)
        company_label = QLabel("Company name:")
        company_label.setMinimumWidth(120)
        self.company_name = ModernLineEdit()
        self.company_name.setPlaceholderText("Your company name")
        company_layout.addWidget(company_label)
        company_layout.addWidget(self.company_name)
        
        exe_options_layout.addLayout(icon_layout)
        exe_options_layout.addWidget(self.hide_console)
        exe_options_layout.addWidget(self.one_file)
        exe_options_layout.addWidget(self.uac_admin)
        exe_options_layout.addWidget(self.add_version)
        exe_options_layout.addLayout(version_layout)
        exe_options_layout.addLayout(company_layout)
        
        layout.addWidget(self.compile_to_exe)
        layout.addLayout(exe_options_layout)
        
        self.toggle_exe_options(False)
        
        exe_group.setLayout(layout)
        parent_layout.addWidget(exe_group)

    def toggle_exe_options(self, state):
        for widget in [self.icon_path, self.hide_console, self.one_file,
                      self.uac_admin, self.add_version, self.version_number,
                      self.company_name]:
            widget.setEnabled(state)

    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir.setText(directory)

    def select_icon_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Icon File",
            "",
            "Icon Files (*.ico);;All Files (*.*)"
        )
        if filename:
            self.icon_path.setText(filename)

    def get_output_path(self, input_path):
        if self.output_filename.text():
            filename = self.output_filename.text()
        else:
            filename = os.path.splitext(os.path.basename(input_path))[0] + '_encoded'
        
        if self.output_dir.text():
            output_dir = self.output_dir.text()
        else:
            output_dir = os.path.dirname(input_path)
            
        return os.path.join(output_dir, filename + '.py')

    def compile_to_executable(self, script_path):
        try:
            cmd = ['pyinstaller', '--noconfirm', '--clean']
            
            if self.one_file.isChecked():
                cmd.append('--onefile')
            
            if self.hide_console.isChecked():
                cmd.append('--noconsole')
            
            if self.icon_path.text():
                cmd.extend(['--icon', self.icon_path.text()])
            
            if self.uac_admin.isChecked():
                cmd.append('--uac-admin')
            
            if self.add_version.isChecked() and self.version_number.text():
                cmd.extend(['--version-file', self.create_version_file()])
            
            cmd.append(script_path)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"PyInstaller error:\n{stderr}")
            
            exe_path = os.path.join('dist', os.path.splitext(os.path.basename(script_path))[0] + '.exe')
            self.result_text.append("\n✨ EXE compilation successful!")
            self.result_text.append(f"📦 EXE saved to: {exe_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "EXE Compilation Error", str(e))

    def create_version_file(self):
        version_info = {
            'version': self.version_number.text(),
            'company_name': self.company_name.text(),
            'file_description': 'Encoded Python Application',
            'internal_name': self.output_filename.text() or 'encoded_app',
            'legal_copyright': f'© {self.company_name.text()}' if self.company_name.text() else '',
            'original_filename': f"{self.output_filename.text() or 'encoded_app'}.exe",
            'product_name': self.output_filename.text() or 'Encoded Application'
        }
        
        version_file = 'version.txt'
        with open(version_file, 'w') as f:
            for key, value in version_info.items():
                f.write(f'# {key}={value}\n')
        
        return version_file

    def encode_with_animation(self):
        sender = self.sender()
        pos = sender.pos()
        self._animation = QPropertyAnimation(sender, b"pos")
        self._animation.setDuration(100)
        self._animation.setStartValue(pos)
        self._animation.setEndValue(pos + QPoint(0, 5))
        self._animation.start()
        
        QTimer.singleShot(100, self.encode_file)

    def select_input_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Python File",
            "",
            "Python Files (*.py);;All Files (*.*)"
        )
        if filename:
            self.input_path.setText(filename)
            self.statusBar.showMessage(f"Selected file: {os.path.basename(filename)}")
            
    def generate_junk_code(self, size):
        junk = []
        variables = [f"var_{i}" for i in range(random.randint(5, 10))]
        functions = [f"func_{i}" for i in range(random.randint(3, 7))]
        
        for _ in range(size):
            choice = random.randint(1, 4)
            if choice == 1:
                var = random.choice(variables)
                value = random.choice([
                    str(random.randint(-1000, 1000)),
                    f'"{self.generate_random_string(10)}"',
                    f"[{', '.join([str(random.randint(0, 100)) for _ in range(3)])}]",
                    f"{{{', '.join([f'{random.randint(0, 100)}: {random.randint(0, 100)}' for _ in range(2)])}}}"
                ])
                junk.append(f"{var} = {value}")
            elif choice == 2:
                var = random.choice(variables)
                junk.append(f"if {var}:")
                junk.append(f"    pass")
            elif choice == 3:
                func = random.choice(functions)
                args = ', '.join(random.sample(variables, random.randint(0, 3)))
                junk.append(f"def {func}({args}):")
                junk.append(f"    return None")
            elif choice == 4:
                var = random.choice(variables)
                junk.append(f"for _ in range({random.randint(1, 5)}):")
                junk.append(f"    {var} = {random.randint(0, 100)}")
        
        return '\n'.join(junk)
    
    def generate_random_string(self, length):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    def encrypt_strings(self, content):
        def encode_string(match):
            s = match.group(1)
            encoded = ''.join(chr(ord(c) ^ 42) for c in s)
            return f"'{''.join(f'\\x{ord(c):02x}' for c in encoded)}'"
        
        return re.sub(r"'([^']*)'", encode_string, content)
    
    def rename_variables(self, content):
        class VariableRenamer(ast.NodeTransformer):
            def __init__(self):
                self.counter = 0
                self.mapping = {}
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    if node.id not in self.mapping:
                        self.mapping[node.id] = f"var_{self.counter}"
                        self.counter += 1
                return ast.Name(id=self.mapping.get(node.id, node.id), ctx=node.ctx)
        
        try:
            tree = ast.parse(content)
            transformer = VariableRenamer()
            transformed = transformer.visit(tree)
            return ast.unparse(transformed)
        except:
            return content
    
    def generate_decoder(self):
        imports = []
        decode_steps = []
        
        if self.use_marshal.isChecked():
            imports.append("import marshal")
        if self.use_base64.isChecked():
            imports.append("import base64")
        if self.use_zlib.isChecked():
            imports.append("import zlib")
        if self.use_binascii.isChecked():
            imports.append("import binascii")
        
        decoder = "# -*- coding: utf-8 -*-\n"
        decoder += "\n".join(imports) + "\n\n"
        decoder += "def decode(encoded):\n"
        decoder += "    try:\n"
        
        if self.use_base64.isChecked():
            decode_steps.append("        encoded = base64.b85decode(encoded)")
        
        if self.use_binascii.isChecked():
            decode_steps.append("        encoded = binascii.unhexlify(encoded)")
        
        if self.use_zlib.isChecked():
            decode_steps.append("        encoded = zlib.decompress(encoded)")
        
        if self.use_marshal.isChecked():
            decode_steps.append("        encoded = marshal.loads(encoded)")
        
        decoder += "\n".join(decode_steps)
        decoder += "\n        return encoded"
        decoder += "\n    except Exception as e:"
        decoder += '\n        print("Decoding error:", str(e))'
        decoder += "\n        return None"
        
        return decoder
    
    def encode_file(self):
        input_path = self.input_path.text()
        if not input_path or not os.path.exists(input_path):
            QMessageBox.critical(self, "Error", "Please select an input file!")
            return
        
        try:
            output_path = self.get_output_path(input_path)
            
            if os.path.exists(output_path):
                if not self.overwrite_existing.isChecked():
                    QMessageBox.critical(self, "Error", "Output file already exists!")
                    return
                if self.create_backup.isChecked():
                    backup_path = output_path + '.bak'
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    os.rename(output_path, backup_path)
            
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                compile(content, '<string>', 'exec')
            except SyntaxError as e:
                QMessageBox.critical(self, "Syntax Error", f"Source file contains an error:\n{str(e)}")
                return
            
            if self.use_marshal.isChecked():
                try:
                    encoded = marshal.dumps(compile(content, '<string>', 'exec'))
                except Exception as e:
                    QMessageBox.critical(self, "Marshal Error", f"Error using marshal: {str(e)}")
                    return
            else:
                encoded = content.encode()
            
            if self.use_zlib.isChecked():
                try:
                    encoded = zlib.compress(encoded, level=9 if self.use_compress.isChecked() else 6)
                except Exception as e:
                    QMessageBox.critical(self, "Zlib Error", f"Compression error: {str(e)}")
                    return
            
            if self.use_binascii.isChecked():
                try:
                    encoded = binascii.hexlify(encoded)
                except Exception as e:
                    QMessageBox.critical(self, "Binascii Error", f"Error using binascii: {str(e)}")
                    return
            
            if self.use_base64.isChecked():
                try:
                    encoded = base64.b85encode(encoded)
                except Exception as e:
                    QMessageBox.critical(self, "Base64 Error", f"Error encoding base64: {str(e)}")
                    return
            
            decoder = self.generate_decoder()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(decoder)
                f.write('\n\nencoded = ' + repr(encoded) + '\n\n')
                f.write('result = decode(encoded)\n')
                f.write('if result is not None:\n')
                f.write('    exec(result)')
            
            self.result_text.clear()
            self.result_text.append("✅ File successfully encoded!")
            self.result_text.append(f"📁 Result saved to: {output_path}")
            self.result_text.append(f"🔄 Encoding methods applied: {sum([
                self.use_marshal.isChecked(),
                self.use_zlib.isChecked(),
                self.use_base64.isChecked(),
                self.use_binascii.isChecked()
            ])}")
            self.result_text.append(f"📊 Source file size: {os.path.getsize(input_path):,} bytes")
            self.result_text.append(f"📊 Encoded file size: {os.path.getsize(output_path):,} bytes")
            
            self.statusBar.showMessage("Encoding completed successfully!", 5000)
            
            if self.compile_to_exe.isChecked():
                self.compile_to_executable(output_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error during encoding:\n{str(e)}")
    
    def clear_all(self):
        self.input_path.clear()
        self.result_text.clear()
        self.layers_spin.setValue(1)
        self.junk_spin.setValue(100)
        self.statusBar.showMessage("All fields cleared", 3000)

    def create_buttons(self, parent_layout):
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.encode_button = ModernButton("Encode")
        self.encode_button.setMinimumWidth(150)
        self.encode_button.clicked.connect(self.encode_with_animation)
        
        self.clear_button = ModernButton("Clear")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        self.clear_button.clicked.connect(self.clear_all)
        
        buttons_layout.addWidget(self.encode_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        
        parent_layout.addLayout(buttons_layout)

def main():
    app = QApplication(sys.argv)
    window = EncoderApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()