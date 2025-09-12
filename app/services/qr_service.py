"""
Servicio de generación de códigos QR para tracking interno de productos.
Archivo: app/services/qr_service.py
Autor: Sistema de desarrollo
Fecha: 2025-01-15
Propósito: Generar QRs únicos, etiquetas imprimibles y gestionar tracking interno
"""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
import os
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime
import uuid


class QRService:
    """Servicio principal para generación y gestión de códigos QR"""
    
    def __init__(self):
        self.qr_directory = "uploads/qr_codes"
        self.label_directory = "uploads/labels"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crear directorios necesarios si no existen"""
        os.makedirs(self.qr_directory, exist_ok=True)
        os.makedirs(self.label_directory, exist_ok=True)
    
    def generate_internal_tracking_id(self, tracking_number: str) -> str:
        """Generar ID interno único para tracking"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:8].upper()
        return f"MS-{timestamp}-{short_uuid}"
    
    def create_qr_code(
        self,
        tracking_number: str,
        internal_id: str,
        product_info: Dict[str, Any],
        style: str = "standard"
    ) -> Dict[str, str]:
        """Crear código QR con información del producto"""
        
        # Preparar datos para el QR
        qr_data = {
            "tracking_number": tracking_number,
            "internal_id": internal_id,
            "timestamp": datetime.now().isoformat(),
            "product_name": product_info.get("name", "N/A"),
            "category": product_info.get("category", "N/A"),
            "verification_url": f"http://192.168.1.137:5173/admin-secure-portal/product/{internal_id}"
        }
        
        # Convertir a string para QR
        qr_content = f"MESTORE:{internal_id}|{tracking_number}|{qr_data['verification_url']}"
        
        # Configurar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Generar imagen según estilo
        if style == "styled":
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer()
            )
        else:
            img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar imagen
        filename = f"qr_{internal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.qr_directory, filename)
        img.save(filepath)
        
        # Convertir a base64 para respuesta
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "qr_filename": filename,
            "qr_filepath": filepath,
            "qr_base64": img_base64,
            "qr_data": qr_data,
            "qr_content": qr_content
        }
    
    def create_product_label(
        self,
        tracking_number: str,
        internal_id: str,
        product_info: Dict[str, Any],
        qr_filepath: str,
        label_size: str = "standard"
    ) -> str:
        """Crear etiqueta completa con QR y información del producto"""
        
        # Dimensiones según tamaño
        if label_size == "small":
            width, height = 400, 300
            font_size = 12
        elif label_size == "large":
            width, height = 800, 600
            font_size = 20
        else:  # standard
            width, height = 600, 400
            font_size = 16
        
        # Crear imagen de etiqueta
        label = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(label)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size + 2)
        except:
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
        
        # Cargar y redimensionar QR
        qr_img = Image.open(qr_filepath)
        qr_size = min(height - 100, 150)
        qr_img = qr_img.resize((qr_size, qr_size))
        
        # Posicionar QR
        qr_x = width - qr_size - 20
        qr_y = 20
        label.paste(qr_img, (qr_x, qr_y))
        
        # Agregar información textual
        y_offset = 20
        
        # Título
        draw.text((20, y_offset), "MeStocker - Producto Verificado", fill="black", font=font_bold)
        y_offset += 35
        
        # Línea separadora
        draw.line([(20, y_offset), (width - qr_size - 40, y_offset)], fill="gray", width=2)
        y_offset += 20
        
        # Información del producto
        info_lines = [
            f"Tracking: {tracking_number}",
            f"ID Interno: {internal_id}",
            f"Producto: {product_info.get('name', 'N/A')[:30]}",
            f"Categoría: {product_info.get('category', 'N/A')}",
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Estado: Verificado"
        ]
        
        for line in info_lines:
            draw.text((20, y_offset), line, fill="black", font=font)
            y_offset += 25
        
        # Instrucciones
        y_offset += 10
        draw.text((20, y_offset), "Escanear QR para información detallada", fill="gray", font=font)
        
        # Guardar etiqueta
        label_filename = f"label_{internal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        label_filepath = os.path.join(self.label_directory, label_filename)
        label.save(label_filepath)
        
        return label_filepath
    
    def decode_qr_content(self, qr_content: str) -> Optional[Dict[str, str]]:
        """Decodificar contenido de QR escaneado"""
        try:
            if qr_content.startswith("MESTORE:"):
                # Formato: MESTORE:internal_id|tracking_number|url
                parts = qr_content.replace("MESTORE:", "").split("|")
                if len(parts) >= 2:
                    return {
                        "internal_id": parts[0],
                        "tracking_number": parts[1],
                        "verification_url": parts[2] if len(parts) > 2 else None
                    }
            return None
        except:
            return None
    
    def get_qr_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de QRs generados"""
        try:
            qr_files = [f for f in os.listdir(self.qr_directory) if f.endswith('.png')]
            label_files = [f for f in os.listdir(self.label_directory) if f.endswith('.png')]
            
            return {
                "total_qr_generated": len(qr_files),
                "total_labels_generated": len(label_files),
                "last_generated": max([
                    os.path.getctime(os.path.join(self.qr_directory, f)) 
                    for f in qr_files
                ]) if qr_files else None
            }
        except:
            return {"total_qr_generated": 0, "total_labels_generated": 0, "last_generated": None}