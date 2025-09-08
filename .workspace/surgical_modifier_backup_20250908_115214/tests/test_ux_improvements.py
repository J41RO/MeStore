import pytest
import tempfile
import os
from pathlib import Path

def test_traditional_syntax():
    '''Test que sintaxis tradicional funciona'''
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write('test traditional content')
        f.flush()
        # Test traditional syntax should work
        assert Path(f.name).exists()
    os.unlink(f.name)

def test_intuitive_syntax():
    '''Test que sintaxis intuitiva funciona'''  
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write('test intuitive content')
        f.flush()
        # Test intuitive syntax should work
        assert Path(f.name).exists()
    os.unlink(f.name)
