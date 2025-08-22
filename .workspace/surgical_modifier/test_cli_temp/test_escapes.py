def test_escapes():
    # Test newlines
    text = "Line 1
Line 2
Line 3"
    
    # Test quotes
    quoted = "He said "Hello World""
    single_quoted = 'It's working'
    
    # Test tabs
    tabbed = "Column1	Column2	Column3"
    
    return text, quoted, single_quoted, tabbed