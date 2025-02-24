import os
import sys
import pandas as pd
import pdfkit
import PyPDF2
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                           QPushButton, QFileDialog, QCheckBox, QMessageBox,
                           QTabWidget, QTextEdit, QGroupBox, QScrollArea,
                           QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import pdfplumber
import re
from shutil import which

class CertificateGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.certificate_number = 1
        self.group_data = []
        
        # Check if template exists
        if not os.path.exists('certificate_template.html'):
            QMessageBox.critical(
                self, 
                'Configuration Error',
                'certificate_template.html not found in the application directory.'
            )
            sys.exit(1)
        
        # Configure wkhtmltopdf path
        self.wkhtmltopdf_path = self.find_wkhtmltopdf()
        if not self.wkhtmltopdf_path:
            QMessageBox.critical(
                self, 
                'Configuration Error',
                'wkhtmltopdf not found. Please ensure it is installed and in your PATH.'
            )
            sys.exit(1)
            
        pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
        
        self.initUI()
        self.setupStyles()
        self.load_award_types()  # Load saved award types
        
    def setupStyles(self):
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
                color: #333;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                min-width: 200px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #0055a4;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #003b73;
            }
            QGroupBox {
                margin-top: 15px;
                font-weight: bold;
            }
            QTableWidget {
                border: 1px solid #ccc;
                gridline-color: #f0f0f0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #0055a4;
                color: white;
                padding: 6px;
            }
        """)

    def initUI(self):
        self.setWindowTitle('Certificate Generator')
        self.setGeometry(100, 100, 1000, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Single Certificate Tab
        single_tab = QWidget()
        single_layout = QVBoxLayout(single_tab)
        self.setup_single_certificate_ui(single_layout)
        tabs.addTab(single_tab, "Single Certificate")
        
        # Group Certificate Tab
        group_tab = QWidget()
        group_layout = QVBoxLayout(group_tab)
        self.setup_group_certificate_ui(group_layout)
        tabs.addTab(group_tab, "Group Certificates")
        
        # File Import Tab
        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        self.setup_file_import_ui(file_layout)
        tabs.addTab(file_tab, "File Import")
        
        layout.addWidget(tabs)

    def setup_single_certificate_ui(self, layout):
        # Award type selection
        award_group = QGroupBox("Award Details")
        award_layout = QVBoxLayout()
        
        # Add horizontal layout for award type and add button
        award_type_layout = QHBoxLayout()
        
        self.award_type = QComboBox()
        self.award_type.setEditable(True)  # Make combobox editable
        self.award_type.addItems([
            'Perfect Attendance Award',
            'Distinguished Excellence in Classroom Conduct',
            'Student Ambassador Award',
            'House Points Achievement',
            'Academic Excellence Award',
            'Custom Award'
        ])
        
        add_award_btn = QPushButton('Add to List')
        add_award_btn.setMaximumWidth(100)
        add_award_btn.clicked.connect(self.add_award_type)
        
        award_type_layout.addWidget(QLabel('Award Type:'))
        award_type_layout.addWidget(self.award_type)
        award_type_layout.addWidget(add_award_btn)
        
        award_layout.addLayout(award_type_layout)
        
        # Student details
        self.student_name = QLineEdit()
        award_layout.addWidget(QLabel('Student Name:'))
        award_layout.addWidget(self.student_name)
        
        award_group.setLayout(award_layout)
        layout.addWidget(award_group)
        
        # Signatory details
        sig_group = QGroupBox("Signatory Details")
        sig_layout = QVBoxLayout()
        
        self.signatory_name = QLineEdit()
        self.signatory_position = QLineEdit()
        sig_layout.addWidget(QLabel('Signatory Name:'))
        sig_layout.addWidget(self.signatory_name)
        sig_layout.addWidget(QLabel('Position:'))
        sig_layout.addWidget(self.signatory_position)
        
        sig_group.setLayout(sig_layout)
        layout.addWidget(sig_group)
        
        # Options
        options_group = QGroupBox("Certificate Options")
        options_layout = QVBoxLayout()
        
        self.award_date = QLineEdit(datetime.now().strftime('%d %B %Y'))
        options_layout.addWidget(QLabel('Award Date:'))
        options_layout.addWidget(self.award_date)
        
        self.include_number = QCheckBox('Include Certificate Number')
        self.include_number.setChecked(True)
        options_layout.addWidget(self.include_number)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Generate button
        generate_btn = QPushButton('Generate Certificate')
        generate_btn.clicked.connect(self.generate_single_certificate)
        layout.addWidget(generate_btn)
        
        layout.addStretch()

    def setup_group_certificate_ui(self, layout):
        # Group details
        group_details = QGroupBox("Group Award Details")
        group_layout = QVBoxLayout()
        
        # Award type with horizontal layout
        award_type_layout = QHBoxLayout()
        
        self.group_award_type = QComboBox()
        self.group_award_type.setEditable(True)
        
        # Award types will be populated when loading saved awards
        award_type_layout.addWidget(QLabel('Award Type:'))
        award_type_layout.addWidget(self.group_award_type)
        
        group_layout.addLayout(award_type_layout)
        
        # Names input
        group_layout.addWidget(QLabel('Enter Names (one per line):'))
        self.names_input = QTextEdit()
        group_layout.addWidget(self.names_input)
        
        group_details.setLayout(group_layout)
        layout.addWidget(group_details)
        
        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(2)
        self.preview_table.setHorizontalHeaderLabels(['Name', 'Award Type'])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.preview_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        preview_btn = QPushButton('Preview List')
        preview_btn.clicked.connect(self.preview_group)
        generate_group_btn = QPushButton('Generate Group Certificates')
        generate_group_btn.clicked.connect(self.generate_group_certificates)
        btn_layout.addWidget(preview_btn)
        btn_layout.addWidget(generate_group_btn)
        layout.addLayout(btn_layout)

    def setup_file_import_ui(self, layout):
        # File selection
        file_group = QGroupBox("File Import")
        file_layout = QVBoxLayout()
        
        file_select_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        file_button = QPushButton('Choose File')
        file_button.clicked.connect(self.choose_file)
        file_select_layout.addWidget(self.file_path)
        file_select_layout.addWidget(file_button)
        
        file_layout.addLayout(file_select_layout)
        
        # Preview area
        self.file_preview = QTableWidget()
        self.file_preview.setColumnCount(2)
        self.file_preview.setHorizontalHeaderLabels(['Name', 'Award Type'])
        self.file_preview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        file_layout.addWidget(self.file_preview)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Generate button
        generate_btn = QPushButton('Generate Certificates from File')
        generate_btn.clicked.connect(self.generate_batch_certificates)
        layout.addWidget(generate_btn)

    def preview_group(self):
        names = self.names_input.toPlainText().strip().split('\n')
        award_type = self.group_award_type.currentText()
        
        self.preview_table.setRowCount(len(names))
        for i, name in enumerate(names):
            name_item = QTableWidgetItem(name.strip())
            award_item = QTableWidgetItem(award_type)
            self.preview_table.setItem(i, 0, name_item)
            self.preview_table.setItem(i, 1, award_item)

    def extract_text_from_pdf(self, pdf_path):
        try:
            extracted_data = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    # Smart name detection
                    # Look for patterns like:
                    # - Capitalized words
                    # - Names followed by awards
                    # - List items with names
                    lines = text.split('\n')
                    for line in lines:
                        # Basic name pattern (two or more capitalized words)
                        name_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
                        names = re.findall(name_pattern, line)
                        
                        for name in names:
                            # Try to find associated award
                            award = "Award"  # Default
                            if "attendance" in line.lower():
                                award = "Perfect Attendance Award"
                            elif "excellence" in line.lower():
                                award = "Academic Excellence Award"
                            elif "conduct" in line.lower():
                                award = "Distinguished Excellence in Classroom Conduct"
                            
                            extracted_data.append({
                                'Student Name': name.strip(),
                                'Award Type': award
                            })
            
            return pd.DataFrame(extracted_data)
        except Exception as e:
            QMessageBox.warning(self, 'PDF Processing Error', 
                              f'Error processing PDF: {str(e)}')
            return pd.DataFrame()

    def choose_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select Input File', '',
            'Excel Files (*.xlsx *.xls);;PDF Files (*.pdf);;All Files (*.*)'
        )
        if file_name:
            self.file_path.setText(file_name)
            self.preview_file_data(file_name)

    def preview_file_data(self, file_path):
        try:
            if (file_path.lower().endswith(('.xlsx', '.xls'))):
                df = pd.read_excel(file_path)
            elif (file_path.lower().endswith('.pdf')):
                df = self.extract_text_from_pdf(file_path)
            else:
                QMessageBox.warning(self, 'File Error', 
                                  'Unsupported file format')
                return
            
            self.file_preview.setRowCount(len(df))
            for i, (_, row) in enumerate(df.iterrows()):
                name_item = QTableWidgetItem(str(row['Student Name']))
                award_item = QTableWidgetItem(str(row['Award Type']))
                self.file_preview.setItem(i, 0, name_item)
                self.file_preview.setItem(i, 1, award_item)
                
        except Exception as e:
            QMessageBox.warning(self, 'Preview Error', 
                              f'Error previewing file: {str(e)}')

    def generate_group_certificates(self):
        try:
            names = self.names_input.toPlainText().strip().split('\n')
            award_type = self.group_award_type.currentText()
            
            if not names:
                QMessageBox.warning(self, 'Input Error', 
                                  'Please enter at least one name.')
                return
                
            for name in names:
                if name.strip():
                    html_content = self.create_certificate_html(
                        name.strip(),
                        award_type,
                        self.signatory_name.text(),
                        self.signatory_position.text(),
                        self.award_date.text(),
                        self.generate_certificate_number()
                    )
                    self.save_certificate(html_content, name.strip())
            
            QMessageBox.information(
                self, 'Success',
                f'Generated {len(names)} certificates successfully!'
            )
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

    def create_certificate_html(self, student_name, award_type, signatory_name, signatory_position, award_date, cert_number=None):
        try:
            with open('certificate_template.html', 'r', encoding='utf-8') as file:
                template = file.read()

            # Get absolute path for logo
            logo_path = os.path.abspath(os.path.join('Assets', 'logo.png'))
            logo_url = f"file:///{logo_path.replace(os.sep, '/')}"
            
            # Replace all placeholders in one go
            replacements = {
                './Assets/logo.png': logo_url,
                '[Student Name]': student_name,
                '[Award Type]': award_type,
                '[Signatory Name]': signatory_name,
                '[Position]': signatory_position,
                '[Date]': award_date,
                'SIS-2024-[XXXX]': cert_number if cert_number else ''
            }
            
            for old, new in replacements.items():
                template = template.replace(old, new)

            return template

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Template processing failed: {str(e)}')
            return None

    def save_certificate(self, html_content, student_name):
        try:
            # Create directory
            os.makedirs('Cert', exist_ok=True)

            # Create safe filename
            safe_name = ''.join(c for c in student_name if c.isalnum() or c in (' ', '-', '_'))
            filename = f"{self.certificate_number-1:03d}_{safe_name}"
            pdf_path = os.path.join('Cert', f"{filename}.pdf")

            # Configure PDF generation with custom settings
            config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
            options = {
                'page-size': 'A4',
                'orientation': 'Landscape',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
                'encoding': 'UTF-8',
                'enable-local-file-access': True,
                # Add more options as needed
                'dpi': 300,
                'no-outline': None,
                'zoom': 1.4

            }

            # Generate PDF with custom options
            pdfkit.from_string(html_content, pdf_path, 
                              options=options,
                              configuration=config)
            return True

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save certificate: {str(e)}')
            return False

    def generate_certificate_number(self):
        if not self.include_number.isChecked():
            return None
        number = f"SIS-{datetime.now().year}-{self.certificate_number:04d}"
        self.certificate_number += 1
        return number

    def generate_single_certificate(self):
        try:
            # Validate inputs
            if not self.validate_certificate_inputs(self.student_name.text(), self.signatory_name.text()):
                return
                
            # Generate certificate
            html_content = self.create_certificate_html(
                self.student_name.text().strip(),
                self.award_type.currentText(),
                self.signatory_name.text(),
                self.signatory_position.text(),
                self.award_date.text(),
                self.generate_certificate_number() if self.include_number.isChecked() else None
            )
            
            # Save certificate
            success = self.save_certificate(html_content, self.student_name.text().strip())
            
            if success:
                QMessageBox.information(self, 'Success', 'Certificate generated successfully!')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

    def generate_batch_certificates(self):
        try:
            # Check if file is selected
            if not self.file_path.text():
                QMessageBox.warning(self, 'Input Error', 'Please select a file first.')
                return

            file_path = self.file_path.text()
            
            # Load data based on file type
            if file_path.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.lower().endswith('.pdf'):
                df = self.extract_text_from_pdf(file_path)
            else:
                QMessageBox.warning(self, 'File Error', 'Unsupported file format')
                return
                
            # Generate certificates for each row
            successful_count = 0
            for _, row in df.iterrows():
                student_name = str(row['Student Name']).strip()
                award_type = str(row['Award Type']).strip()
                
                if student_name and award_type:
                    html_content = self.create_certificate_html(
                        student_name,
                        award_type,
                        self.signatory_name.text(),
                        self.signatory_position.text(),
                        self.award_date.text(),
                        self.generate_certificate_number() if self.include_number.isChecked() else None
                    )
                    
                    if self.save_certificate(html_content, student_name):
                        successful_count += 1
            
            if successful_count > 0:
                QMessageBox.information(
                    self, 'Success',
                    f'Generated {successful_count} certificates successfully!'
                )
            else:
                QMessageBox.warning(
                    self, 'Warning',
                    'No certificates were generated. Please check the input file format.'
                )
                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

    def find_wkhtmltopdf(self):
        """Find the wkhtmltopdf executable path"""
        # Check if wkhtmltopdf is in PATH
        wkhtmltopdf = which('wkhtmltopdf')
        if (wkhtmltopdf):
            return wkhtmltopdf
            
        # Check common installation paths on Windows
        common_paths = [
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
                
        return None

    def add_award_type(self):
        new_award = self.award_type.currentText().strip()
        
        if not new_award:
            return
            
        # Check if award already exists
        existing_awards = [self.award_type.itemText(i) for i in range(self.award_type.count())]
        
        if new_award not in existing_awards:
            # Add to both single and group certificate comboboxes
            self.award_type.addItem(new_award)
            self.group_award_type.addItem(new_award)
            
            # Optional: Save to configuration file
            self.save_award_types()
            
            QMessageBox.information(self, 'Success', f'Added new award type: {new_award}')

    def save_award_types(self):
        try:
            awards = [self.award_type.itemText(i) for i in range(self.award_type.count())]
            with open('award_types.txt', 'w') as f:
                for award in awards:
                    f.write(f"{award}\n")
        except Exception as e:
            QMessageBox.warning(self, 'Save Error', f'Failed to save award types: {str(e)}')

    def load_award_types(self):
        try:
            if os.path.exists('award_types.txt'):
                with open('award_types.txt', 'r') as f:
                    awards = [line.strip() for line in f.readlines()]
                    
                # Update both comboboxes
                self.award_type.clear()
                self.group_award_type.clear()
                
                self.award_type.addItems(awards)
                self.group_award_type.addItems(awards)
        except Exception as e:
            QMessageBox.warning(self, 'Load Error', f'Failed to load award types: {str(e)}')

    # Add new method for certificate generation validation
    def validate_certificate_inputs(self, student_name, signatory_name):
        if not student_name.strip():
            QMessageBox.warning(self, 'Input Error', 'Please enter a student name.')
            return False
            
        if not signatory_name.strip():
            QMessageBox.warning(self, 'Input Error', 'Please enter a signatory name.')
            return False
        
        return True

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont('Segoe UI', 10))
    
    ex = CertificateGenerator()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()