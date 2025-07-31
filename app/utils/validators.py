"""
Validadores específicos para MeStore.

Validadores especializados para datos colombianos:
- Celulares colombianos (solo móviles)
- Cédulas colombianas
- Otros validadores específicos
"""

import re
from typing import Optional


def validate_celular_colombiano(phone: Optional[str]) -> str:
    """
    Validar que el teléfono sea ESPECÍFICAMENTE un celular colombiano.
    
    SOLO acepta códigos móviles colombianos:
    - 300-305 (Tigo)
    - 310-319 (Movistar)
    - 320-334 (Claro)
    - 350-353 (Avantel)
    - 371-373 (Virgin Mobile)
    - 380-381 (Virgin Mobile)
    
    Args:
        phone: Número de teléfono en cualquier formato
        
    Returns:
        str: Teléfono normalizado en formato +57 XXXXXXXXXX
        
    Raises:
        ValueError: Si no es un celular colombiano válido
    """
    if phone is None:
        raise ValueError("Teléfono celular es requerido")
    
    # Limpiar formato
    phone_clean = re.sub(r"[\s\-\(\)]", "", str(phone))
    
    # Remover código de país si existe
    if phone_clean.startswith("+57"):
        phone_clean = phone_clean[3:]
    elif phone_clean.startswith("57") and len(phone_clean) > 10:
        phone_clean = phone_clean[2:]
    
    # Validar longitud
    if not phone_clean.isdigit() or len(phone_clean) != 10:
        raise ValueError("Celular debe tener 10 dígitos")
    
    # CÓDIGOS MÓVILES COLOMBIANOS ESPECÍFICOS
    mobile_codes = [
        # Tigo
        "300", "301", "302", "303", "304", "305",
        # Movistar
        "310", "311", "312", "313", "314", "315", "316", "317", "318", "319",
        # Claro
        "320", "321", "322", "323", "324", "325", "326", "327", "328", "329",
        "330", "331", "332", "333", "334",
        # Avantel
        "350", "351", "352", "353",
        # Virgin Mobile
        "371", "372", "373", "380", "381"
    ]
    
    # Verificar que el código sea móvil
    code_3_digits = phone_clean[:3]
    if code_3_digits not in mobile_codes:
        raise ValueError(
            f"Solo se permiten números celulares. "
            f"Código {code_3_digits} no es un operador móvil colombiano válido"
        )
    
    return f"+57 {phone_clean}"


def get_mobile_operators_info() -> dict:
    """Retorna información de operadores móviles colombianos"""
    return {
        "Tigo": ["300", "301", "302", "303", "304", "305"],
        "Movistar": ["310", "311", "312", "313", "314", "315", "316", "317", "318", "319"],
        "Claro": ["320", "321", "322", "323", "324", "325", "326", "327", "328", "329", "330", "331", "332", "333", "334"],
        "Avantel": ["350", "351", "352", "353"],
        "Virgin Mobile": ["371", "372", "373", "380", "381"]
    }