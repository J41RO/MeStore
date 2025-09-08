import unittest
from functions.react.jsx_parser import JSXParser
from functions.react.hook_manager import HookManager
from functions.react.component_analyzer import ComponentAnalyzer
from functions.react.props_manager import PropsManager

class TestReactFunctions(unittest.TestCase):
    
    def setUp(self):
        self.jsx_parser = JSXParser()
        self.hook_manager = HookManager()
        self.component_analyzer = ComponentAnalyzer()
        self.props_manager = PropsManager()
        
    def test_jsx_parsing(self):
        """Test parsing de JSX básico"""
        jsx_code = "<div><span>Hello</span></div>"
        result = self.jsx_parser.validate_jsx_syntax(jsx_code)
        self.assertTrue(result)
        
    def test_hook_detection(self):
        """Test detección de hooks"""
        component_code = "const [count, setCount] = useState(0); useEffect(() => {}, []);"
        hooks = self.hook_manager.detect_existing_hooks(component_code)
        self.assertIn('useState', hooks)
        self.assertIn('useEffect', hooks)
        
    def test_component_analysis(self):
        """Test análisis de componente"""
        component_code = """
        const Button: React.FC<ButtonProps> = ({label, onClick}) => {
          const [active, setActive] = useState(false);
          return <button onClick={onClick}>{label}</button>;
        };
        """
        analysis = self.component_analyzer.analyze_component_structure(component_code)
        self.assertEqual(analysis['name'], 'Button')
        self.assertIn('useState', analysis['hooks'])
        self.assertTrue(analysis['jsx_structure']['has_jsx'])
        
    def test_props_management(self):
        """Test gestión de props"""
        component_code = "const Button = ({label}) => <button>{label}</button>;"
        updated = self.props_manager.add_prop_to_interface(component_code, 'onClick', '() => void')
        self.assertIn('onClick', updated)
        self.assertIn('() => void', updated)

if __name__ == '__main__':
    unittest.main()
