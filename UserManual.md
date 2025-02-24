# Certificate Generator User Manual

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Features](#features)
- [Usage Guide](#usage-guide)
- [Technical Specifications](#technical-specifications)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

## Overview

The Certificate Generator is a professional tool designed for creating academic certificates at Sandford International School. It offers three flexible methods for certificate generation:

1. Single Certificate Generation
2. Group Certificate Generation
3. File Import Generation

## Installation

### System Requirements
- Windows, macOS, or Linux operating system
- Python 3.7 or higher
- Minimum 4GB RAM
- 100MB free disk space

### Required Software

1. **Python Packages**
```bash
pip install pandas pdfkit PyQt5 PyPDF2 pdfplumber
```

2. **wkhtmltopdf**
- Windows: Download installer from [wkhtmltopdf website](https://wkhtmltopdf.org/downloads.html)
- Linux: `sudo apt-get install wkhtmltopdf`
- macOS: `brew install wkhtmltopdf`

### Setup Steps

1. Clone or download the application files
2. Create required folders:
   ```
   project_folder/
   ├── Assets/
   │   └── logo.png
   ├── main.py
   └── certificate_template.html
   ```
3. Place school logo in the Assets folder
4. Verify wkhtmltopdf installation

## Getting Started

### First-Time Setup

1. Launch the application:
   ```bash
   python main.py
   ```
2. Verify the certificate template loads correctly
3. Test generate a sample certificate

## Features

### Single Certificate Generation
- Individual certificate creation
- Custom award types
- Automatic certificate numbering
- Date customization

### Group Certificate Generation
- Multiple certificates at once
- Bulk name processing
- Preview functionality
- Consistent formatting

### File Import Generation
- Excel file support (.xlsx, .xls)
- PDF text extraction
- Batch processing
- Data preview

## Usage Guide

### Single Certificate Generation

1. Select "Single Certificate" tab
2. Enter certificate details:
   - Award Type (select or create new)
   - Student Name
   - Signatory Name
   - Signatory Position
   - Award Date
3. Optional: Enable certificate numbering
4. Click "Generate Certificate"

### Group Certificate Generation

1. Select "Group Certificates" tab
2. Choose award type
3. Enter student names (one per line)
4. Click "Preview List" to verify
5. Click "Generate Group Certificates"

### File Import Generation

1. Select "File Import" tab
2. Prepare input file:
   - Excel: Columns must be "Student Name" and "Award Type"
   - PDF: Structured text with clear name/award separation
3. Click "Choose File"
4. Review preview table
5. Click "Generate Certificates from File"

## Technical Specifications

### Certificate Format
- Size: A4 Landscape
- File Type: PDF
- Resolution: 300 DPI
- Naming: XXX_StudentName.pdf

### File Structure
```
output_folder/
└── Cert/
    ├── 001_StudentName.pdf
    ├── 002_StudentName.pdf
    └── ...
```

### Certificate Numbering
- Format: SIS-YYYY-XXXX
- Auto-incrementing
- Year updates automatically
- Optional feature

## Troubleshooting

### Common Issues

1. **Certificates Not Generating**
   - Verify wkhtmltopdf installation
   - Check folder permissions
   - Ensure all required fields are filled

2. **Missing Images**
   - Verify logo.png exists in Assets folder
   - Check file paths
   - Confirm file permissions

3. **Import Problems**
   - Verify file format
   - Check column names
   - Ensure proper text formatting

### Error Messages

| Error | Solution |
|-------|----------|
| "wkhtmltopdf not found" | Reinstall wkhtmltopdf |
| "Template not found" | Check certificate_template.html location |
| "Permission denied" | Check folder permissions |

## Support

### Getting Help
- Review this documentation
- Check error messages
- Contact system administrator

### Reporting Issues
- Document the problem
- Note any error messages
- Describe steps to reproduce

### Updates and Maintenance
- Regular backups recommended
- Keep Python packages updated
- Check for wkhtmltopdf updates

---

**Note**: This documentation is maintained by the IT department. For internal support, contact your system administrator.