def validate_and_execute(coordinator_class, file_path, target, content, action_name):
    """Validación obligatoria antes de cualquier operación quirúrgica"""
    
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    matches = file_content.count(target)
    
    if matches == 0:
        return {
            'success': False,
            'error': f'Target not found: "{target}"',
            'file': file_path,
            'action': action_name
        }
    elif matches > 1:
        lines = file_content.split('\n')
        match_locations = []
        for i, line in enumerate(lines, 1):
            if target in line:
                match_locations.append(f'Line {i}: {line.strip()}')
        
        return {
            'success': False,
            'error': f'Ambiguous target: "{target}" appears {matches} times',
            'locations': match_locations,
            'suggestion': 'Use more specific target pattern',
            'action': action_name
        }
    
    # Target único, ejecutar operación
    print(f'Target validated, executing {action_name}...')
    coordinator = coordinator_class()
    return coordinator.execute(file_path, target, content)

# Ejemplos de uso seguro
if __name__ == "__main__":
    from coordinators.before import BeforeCoordinator
    from coordinators.after import AfterCoordinator
    
    # Uso correcto con validación
    result = validate_and_execute(
        BeforeCoordinator,
        '/tmp/real_dev_project/src/api.py',
        'from datetime import datetime',  # Target específico
        'from pydantic import BaseModel',
        'BEFORE'
    )
    print('Validated execution result:', result.get('success', False))
