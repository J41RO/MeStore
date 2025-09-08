"""
Tests for FileExplorer functionality
Testing file exploration, line ranges, context operations and CLI integration
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from functions.analysis.file_explorer import FileExplorer


class TestFileExplorer:
    """Test suite for FileExplorer class"""
    
    @pytest.fixture
    def explorer(self):
        """Fixture to provide FileExplorer instance"""
        return FileExplorer()
    
    @pytest.fixture
    def sample_file(self):
        """Fixture to create temporary test file"""
        content = "line 1\nline 2\nline 3\nline 4\nline 5\nline 6\nline 7\nline 8\nline 9\nline 10\n"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_read_file_lines_success(self, explorer, sample_file):
        """Test successful file reading"""
        lines = explorer.read_file_lines(sample_file)
        assert len(lines) == 10
        assert lines[0] == "line 1\n"
        assert lines[9] == "line 10\n"
    
    def test_read_file_lines_file_not_found(self, explorer):
        """Test FileNotFoundError when file doesn't exist"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            explorer.read_file_lines("/nonexistent/file.txt")
    
    def test_read_file_lines_not_a_file(self, explorer, tmp_path):
        """Test ValueError when path is directory"""
        with pytest.raises(ValueError, match="Path is not a file"):
            explorer.read_file_lines(str(tmp_path))
    
    def test_get_lines_range_valid(self, explorer):
        """Test valid line range extraction"""
        lines = ["line1\n", "line2\n", "line3\n", "line4\n", "line5\n"]
        result = explorer.get_lines_range(lines, 2, 4)
        assert result == ["line2\n", "line3\n", "line4\n"]
    
    def test_get_lines_range_invalid_start(self, explorer):
        """Test ValueError for start < 1"""
        lines = ["line1\n", "line2\n"]
        with pytest.raises(ValueError, match="Start line must be >= 1"):
            explorer.get_lines_range(lines, 0, 2)
    
    def test_get_lines_range_invalid_end(self, explorer):
        """Test ValueError for end < start"""
        lines = ["line1\n", "line2\n"]
        with pytest.raises(ValueError, match="End line must be >= start line"):
            explorer.get_lines_range(lines, 3, 2)
    
    def test_get_lines_range_start_exceeds_file(self, explorer):
        """Test ValueError when start exceeds file length"""
        lines = ["line1\n", "line2\n"]
        with pytest.raises(ValueError, match="Start line .* exceeds file length"):
            explorer.get_lines_range(lines, 5, 6)
    
    def test_get_context_around_valid(self, explorer):
        """Test valid context extraction around line"""
        lines = ["1\n", "2\n", "3\n", "4\n", "5\n", "6\n", "7\n"]
        context_lines, start_line = explorer.get_context_around(lines, 4, 2)
        assert context_lines == ["2\n", "3\n", "4\n", "5\n", "6\n"]
        assert start_line == 2
    
    def test_get_context_around_beginning_boundary(self, explorer):
        """Test context at beginning of file"""
        lines = ["1\n", "2\n", "3\n", "4\n", "5\n"]
        context_lines, start_line = explorer.get_context_around(lines, 1, 3)
        assert context_lines == ["1\n", "2\n", "3\n", "4\n"]
        assert start_line == 1
    
    def test_get_context_around_end_boundary(self, explorer):
        """Test context at end of file"""
        lines = ["1\n", "2\n", "3\n", "4\n", "5\n"]
        context_lines, start_line = explorer.get_context_around(lines, 5, 3)
        assert context_lines == ["2\n", "3\n", "4\n", "5\n"]
        assert start_line == 2
    
    def test_get_context_around_invalid_line(self, explorer):
        """Test ValueError for invalid line number"""
        lines = ["1\n", "2\n", "3\n"]
        with pytest.raises(ValueError, match="Line number .* is out of range"):
            explorer.get_context_around(lines, 5, 2)
    
    def test_get_context_around_negative_context(self, explorer):
        """Test ValueError for negative context"""
        lines = ["1\n", "2\n", "3\n"]
        with pytest.raises(ValueError, match="Context must be non-negative"):
            explorer.get_context_around(lines, 2, -1)
    
    def test_format_output_basic(self, explorer):
        """Test basic output formatting"""
        lines = ["first line\n", "second line\n"]
        result = explorer.format_output(lines)
        expected = " 1: first line\n 2: second line"
        assert result == expected
    
    def test_format_output_with_start_line(self, explorer):
        """Test output formatting with custom start line"""
        lines = ["line A\n", "line B\n"]
        result = explorer.format_output(lines, start_line=10)
        expected = " 10: line A\n 11: line B"
        assert result == expected
    
    def test_format_output_with_highlight(self, explorer):
        """Test output formatting with highlighted line"""
        lines = ["line A\n", "line B\n", "line C\n"]
        result = explorer.format_output(lines, start_line=5, highlight_line=6)
        expected = " 5: line A\n→6: line B\n 7: line C"
        assert result == expected
    
    def test_format_output_empty_lines(self, explorer):
        """Test formatting empty lines list"""
        result = explorer.format_output([])
        assert result == "No lines to display."
    
    def test_parse_lines_range_valid(self, explorer):
        """Test valid lines range parsing"""
        start, end = explorer.parse_lines_range("10:20")
        assert start == 10
        assert end == 20
    
    def test_parse_lines_range_invalid_format(self, explorer):
        """Test ValueError for invalid format"""
        with pytest.raises(ValueError, match="Lines range must be in format 'start:end'"):
            explorer.parse_lines_range("10-20")
    
    def test_parse_lines_range_too_many_parts(self, explorer):
        """Test ValueError for too many colons"""
        with pytest.raises(ValueError, match="Lines range must be in format 'start:end'"):
            explorer.parse_lines_range("10:20:30")
    
    def test_parse_lines_range_non_integer(self, explorer):
        """Test ValueError for non-integer values"""
        with pytest.raises(ValueError, match="Line numbers must be integers"):
            explorer.parse_lines_range("abc:def")
    
    def test_parse_lines_range_negative_numbers(self, explorer):
        """Test ValueError for negative line numbers"""
        with pytest.raises(ValueError, match="Line numbers must be positive"):
            explorer.parse_lines_range("-5:10")


class TestCLIIntegration:
    """Test CLI integration with explore command"""
    
    @pytest.fixture
    def sample_cli_file(self):
        """Fixture for CLI testing file"""
        content = "\n".join([f"CLI line {i}" for i in range(1, 11)]) + "\n"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_cli_explore_lines_parameter(self, sample_cli_file):
        """Test CLI explore with --lines parameter"""
        from click.testing import CliRunner
        import cli
        
        runner = CliRunner()
        result = runner.invoke(cli.main, ['explore', sample_cli_file, '--lines', '2:4'])
        
        assert result.exit_code == 0
        assert "CLI line 2" in result.output
        assert "CLI line 3" in result.output
        assert "CLI line 4" in result.output
        assert "CLI line 1" not in result.output
        assert "CLI line 5" not in result.output
    
    def test_cli_explore_around_parameter(self, sample_cli_file):
        """Test CLI explore with --around parameter"""
        from click.testing import CliRunner
        import cli
        
        runner = CliRunner()
        result = runner.invoke(cli.main, ['explore', sample_cli_file, '--around', '5', '--context', '2'])
        
        assert result.exit_code == 0
        assert "→5:" in result.output  # Highlighted line
        assert "CLI line 3" in result.output
        assert "CLI line 4" in result.output
        assert "CLI line 5" in result.output
        assert "CLI line 6" in result.output
        assert "CLI line 7" in result.output
    
    def test_cli_explore_analyze_backward_compatibility(self, sample_cli_file):
        """Test backward compatibility with --analyze flag"""
        from click.testing import CliRunner
        import cli
        
        runner = CliRunner()
        result = runner.invoke(cli.main, ['explore', sample_cli_file, '--analyze'])
        
        assert result.exit_code == 0
        assert "Analizando estructura" in result.output
        assert "Total de líneas:" in result.output
    
    def test_cli_explore_invalid_lines_format(self, sample_cli_file):
        """Test CLI error handling for invalid --lines format"""
        from click.testing import CliRunner
        import cli
        
        runner = CliRunner()
        result = runner.invoke(cli.main, ['explore', sample_cli_file, '--lines', '5:2'])
        
        assert result.exit_code == 0  # CLI doesn't exit with error, just prints message
        assert "Error en parámetro --lines" in result.output
    
    def test_cli_explore_nonexistent_file(self):
        """Test CLI error handling for nonexistent file"""
        from click.testing import CliRunner
        import cli
        
        runner = CliRunner()
        result = runner.invoke(cli.main, ['explore', '/nonexistent/file.txt'])
        
        assert result.exit_code == 0  # CLI doesn't exit with error
        assert "Error explorando" in result.output
    
    def test_cli_explore_default_behavior(self, sample_cli_file):
        """Test CLI default behavior (first 20 lines)"""
        from click.testing import CliRunner
        import cli
        
        runner = CliRunner()
        result = runner.invoke(cli.main, ['explore', sample_cli_file])
        
        assert result.exit_code == 0
        assert "Primeras líneas de" in result.output
        assert "CLI line 1" in result.output
        assert "CLI line 10" in result.output


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_unicode_file_handling(self):
        """Test handling of unicode files"""
        content = "línea con ñ\ncarácter especial: ü\n"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            explorer = FileExplorer()
            lines = explorer.read_file_lines(temp_path)
            assert len(lines) == 2
            assert "ñ" in lines[0]
            assert "ü" in lines[1]
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_empty_file_handling(self):
        """Test handling of empty files"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name
        
        try:
            explorer = FileExplorer()
            lines = explorer.read_file_lines(temp_path)
            assert lines == []
            
            # Test formatting empty file
            result = explorer.format_output(lines)
            assert result == "No lines to display."
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_single_line_file(self):
        """Test handling of single line files"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("single line without newline")
            temp_path = f.name
        
        try:
            explorer = FileExplorer()
            lines = explorer.read_file_lines(temp_path)
            assert len(lines) == 1
            assert lines[0] == "single line without newline"
            
            # Test context around the only line
            context_lines, start_line = explorer.get_context_around(lines, 1, 5)
            assert context_lines == lines
            assert start_line == 1
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)