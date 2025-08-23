def test_escapes():
    # Test newlines
    text = """Line 1
Line 2
Line 3"""
    
    # Test quotes
    quoted = 'He said "Hello World"'
    single_quoted = "It's working"
    
    # Simple assertions
    assert "Line 1" in text
    assert "Line 2" in text
    assert "Hello World" in quoted
    assert "It's" in single_quoted
    
    print("All escape tests passed!")

if __name__ == "__main__":
    test_escapes()
