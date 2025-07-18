"""
Test básico para verificar funcionamiento del entorno de testing.
Archivo creado según tarea 0.2.4.1.
"""


def test_basic_math():
    """Test básico para verificar que pytest funciona correctamente."""
    assert 1 + 1 == 2


def test_basic_string():
    """Test adicional para verificar operaciones básicas."""
    assert "hello" + " world" == "hello world"


def test_basic_list():
    """Test básico con listas."""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert 2 in test_list
