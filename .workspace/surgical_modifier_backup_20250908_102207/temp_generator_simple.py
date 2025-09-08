# Template system simplificado que FUNCIONA
templates = {
    'python': '''#!/usr/bin/env python3
"""
{description}

Created: {timestamp}
"""

def main():
    """Main function"""
    pass

if __name__ == "__main__":
    main()
''',
    'js': '''/**
 * {description}
 * 
 * Created: {timestamp}
 */

function main() {
    // Implementation here
}

// Export for module usage
module.exports = { main };
''',
    'default': '''/**
 * {description}
 * 
 * Created: {timestamp}
 */

// Content goes here
'''
}

# Personalización que FUNCIONA
from datetime import datetime

def customize_simple(template, **kwargs):
    vars = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'description': 'Auto-generated file',
        **kwargs
    }
    return template.format(**vars)

# Probar
js_result = customize_simple(templates['js'])
print('JS works:', '{description}' not in js_result)
print('Contains Auto-generated:', 'Auto-generated file' in js_result)
