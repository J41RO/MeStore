def test_escapes():
    # Test newlines
    text = "Line 1\nLine 2\nLine 3"
    
    # Test quotes  
    quoted = "He said "Hello World""
    single_quoted = 'It's working'
    
    # Test tabs
    tabbed = "Column1\tColumn2\tColumn3"
    
    return text, quoted, single_quoted, tabbed