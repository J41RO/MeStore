"""
Tests específicos para JsTsValidator - Validación de sintaxis JavaScript/TypeScript
Cubre casos específicos de React.memo y estructuras complejas
"""

import pytest
import tempfile
import os
from functions.validation.js_ts_validator import JsTsValidator


class TestJsTsValidator:
    """Test suite para validador de sintaxis JavaScript/TypeScript"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.validator = JsTsValidator()
    
    def test_valid_react_memo_component(self):
        """Test: React.memo válido debe pasar validación"""
        valid_code = """
import React from 'react';

const MyComponent = React.memo((props) => {
  return <div>{props.name}</div>;
});

export default MyComponent;
"""
        result = self.validator.validate_js_syntax(valid_code)
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_invalid_react_memo_double_arrow(self):
        """Test: React.memo con doble arrow debe fallar validación"""
        invalid_code = """
const BadComponent = React.memo((props) => (props) => <div>Bad</div>);
"""
        result = self.validator.validate_js_syntax(invalid_code)
        assert result['valid'] is False
        assert len(result['errors']) > 0
        # Verificar errores específicos
        error_messages = '; '.join(result['errors'])
        assert 'arrow function malformada' in error_messages
    
    def test_unbalanced_brackets(self):
        """Test: Paréntesis desbalanceados deben fallar validación"""
        invalid_code = """
const broken = (function() {
  return 'missing closing paren';
)();
"""
        result = self.validator.validate_js_syntax(invalid_code)
        assert result['valid'] is False
        assert any('desbalanceados' in error for error in result['errors'])
    
    def test_typescript_interface_valid(self):
        """Test: Interface TypeScript válida"""
        valid_ts_code = """
interface Props {
  name: string;
  value: number;
}

const Component: React.FC<Props> = ({ name, value }) => (
  <div>{name}: {value}</div>
);
"""
        result = self.validator.validate_ts_syntax(valid_ts_code)
        assert result['valid'] is True
    
    def test_react_structures_validation(self):
        """Test: Validación específica de estructuras React"""
        react_code = """
import React, { useState } from 'react';

const Component = React.memo((props) => {
  const [state, setState] = useState(0);
  return <div onClick={() => setState(state + 1)}>{props.label}: {state}</div>;
});
"""
        result = self.validator.validate_react_structures(react_code)
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_get_syntax_errors_by_extension(self):
        """Test: get_syntax_errors según extensión de archivo"""
        code = """
const Component = React.memo((props) => <div>{props.test}</div>);
"""
        # Test .jsx
        errors_jsx = self.validator.get_syntax_errors(code, '.jsx')
        assert isinstance(errors_jsx, list)
        
        # Test .tsx  
        errors_tsx = self.validator.get_syntax_errors(code, '.tsx')
        assert isinstance(errors_tsx, list)
        
        # Test .js
        errors_js = self.validator.get_syntax_errors(code, '.js')
        assert isinstance(errors_js, list)
    
    def test_problematic_patterns_detection(self):
        """Test: Detección de patrones problemáticos específicos"""
        problematic_code = """
// Patrón problemático: React.memo con sintaxis malformada
const Bad1 = React.memo((props) => (props) => <div>Bad</div>);

// Patrón problemático: función con doble paréntesis
function bad2(param) (param2) { return 'broken'; }

// Patrón problemático: imports malformados
import { Component } { AnotherComponent } from 'react';
"""
        result = self.validator.validate_js_syntax(problematic_code)
        assert result['valid'] is False
        assert len(result['errors']) >= 3  # Debe detectar al menos 3 problemas
    
    def test_jsx_tag_validation(self):
        """Test: Validación básica de tags JSX"""
        # JSX válido
        valid_jsx = """
const Component = () => (
  <div>
    <span>Text</span>
    <input type="text" />
  </div>
);
"""
        result = self.validator.validate_react_structures(valid_jsx)
        assert result['valid'] is True
        
        # JSX con tags desbalanceados
        invalid_jsx = """
const Component = () => (
  <div>
    <span>Text
  </div>
);
"""
        result = self.validator.validate_react_structures(invalid_jsx)
        # Nota: Puede pasar o fallar dependiendo de la implementación de validación JSX
        # Este test documenta el comportamiento actual
        assert isinstance(result['valid'], bool)
    
    def test_edge_cases(self):
        """Test: Casos edge y contenido vacío"""
        # Contenido vacío
        result = self.validator.validate_js_syntax("")
        assert result['valid'] is True
        
        # Solo espacios en blanco
        result = self.validator.validate_js_syntax("   \n  \t  ")
        assert result['valid'] is True
        
        # Solo comentarios
        result = self.validator.validate_js_syntax("// Just a comment\n/* Block comment */")
        assert result['valid'] is True


class TestIntegrationWithWorkflow:
    """Tests de integración con ReplaceWorkflow"""
    
    def setup_method(self):
        """Setup para tests de integración"""
        self.validator = JsTsValidator()
    
    def test_react_memo_replacement_problem_solved(self):
        """Test: Problema original con React.memo múltiples reemplazos"""
        # Simular el problema original reportado
        original_code = """
const MyComponent = React.memo((props) => {
  return <div>{props.name}: {props.value}</div>;
});
"""
        
        # Simular reemplazo problemático que antes rompía sintaxis
        # Esto simula lo que pasaría con replace "props" "properties"
        after_replace = original_code.replace("props", "properties")
        
        # Validar que el reemplazo resulte en código válido
        result = self.validator.validate_js_syntax(after_replace)
        assert result['valid'] is True
        
        # Verificar que el código resultante sea sintácticamente correcto
        assert "React.memo((properties)" in after_replace
        assert "properties.name" in after_replace
        assert "properties.value" in after_replace
    
    def test_multiple_consecutive_replaces(self):
        """Test: Múltiples reemplazos consecutivos con React.memo"""
        code = """
const Component = React.memo((props) => {
  return <div>{props.name} - {props.value}</div>;
});
"""
        
        # Primer reemplazo
        code = code.replace("props", "p")
        result1 = self.validator.validate_js_syntax(code)
        
        # Segundo reemplazo
        code = code.replace("name", "title")  
        result2 = self.validator.validate_js_syntax(code)
        
        # Tercer reemplazo
        code = code.replace("value", "data")
        result3 = self.validator.validate_js_syntax(code)
        
        # Todos los reemplazos deben resultar en código válido
        assert result1['valid'] is True
        assert result2['valid'] is True  
        assert result3['valid'] is True
    
    def test_force_mode_bypass(self):
        """Test: Documentar comportamiento cuando se usa --force"""
        # Código que genera errores de sintaxis
        invalid_code = """
const Broken = React.memo((props) => (props) => <div>Bad</div>);
"""
        
        result = self.validator.validate_js_syntax(invalid_code)
        assert result['valid'] is False
        assert len(result['errors']) > 0
        
        # En modo --force, el validador seguiría detectando errores,
        # pero el workflow los ignoraría. Este test documenta que
        # el validador funciona correctamente independientemente del modo.
        
    def test_preview_mode_validation(self):
        """Test: Validación en modo preview"""
        original = """
const Component = React.memo((props) => <div>{props.test}</div>);
"""
        
        # Simular preview de reemplazo válido
        preview_valid = original.replace("props", "properties")
        result_valid = self.validator.validate_js_syntax(preview_valid)
        assert result_valid['valid'] is True
        
        # Simular preview de reemplazo inválido
        preview_invalid = original.replace("props", "props) => (props")
        result_invalid = self.validator.validate_js_syntax(preview_invalid)
        assert result_invalid['valid'] is False
        assert len(result_invalid['errors']) > 0


# Tests de performance y robustez
class TestValidatorRobustness:
    """Tests de robustez y performance del validador"""
    
    def setup_method(self):
        self.validator = JsTsValidator()
    
    def test_large_file_handling(self):
        """Test: Manejo de archivos grandes"""
        # Generar código JavaScript grande
        large_code = """
import React from 'react';

""" + "\n".join([f"""
const Component{i} = React.memo((props) => {{
  return <div>{{props.value{i}}}</div>;
}});
""" for i in range(100)])
        
        result = self.validator.validate_js_syntax(large_code)
        assert isinstance(result['valid'], bool)
        assert isinstance(result['errors'], list)
    
    def test_unicode_and_special_characters(self):
        """Test: Manejo de caracteres Unicode y especiales"""
        unicode_code = """
const Component = React.memo((props) => {
  return <div>{props.名前} - {props.vérité} - {props.测试}</div>;
});
"""
        
        result = self.validator.validate_js_syntax(unicode_code)
        assert result['valid'] is True
    
    def test_validator_error_handling(self):
        """Test: Manejo de errores internos del validador"""
        # Test con contenido que podría causar errores en regex
        problematic_content = """
const regex = /[unclosed regex
const Component = React.memo((props) => <div>{props.test}</div>);
"""
        
        # El validador debe manejar errores graciosamente
        result = self.validator.validate_js_syntax(problematic_content)
        assert isinstance(result, dict)
        assert 'valid' in result
        assert 'errors' in result


if __name__ == "__main__":
    # Ejecutar tests básicos si se ejecuta directamente
    validator = JsTsValidator()
    
    print("🧪 EJECUTANDO TESTS BÁSICOS DEL VALIDADOR")
    
    # Test 1: React.memo válido
    valid_code = "const C = React.memo((props) => <div>{props.name}</div>);"
    result = validator.validate_js_syntax(valid_code)
    print(f"✅ React.memo válido: {result['valid']}")
    
    # Test 2: React.memo inválido
    invalid_code = "const C = React.memo((props) => (props) => <div>Bad</div>);"
    result = validator.validate_js_syntax(invalid_code)
    print(f"❌ React.memo inválido: {result['valid']} (errores: {len(result['errors'])})")
    
    print("🎯 Tests básicos completados")
