# CLI v6.0 - Ejemplos Prácticos del Comando CREATE con --from-stdin

## Introducción
El flag `--from-stdin` permite crear archivos con contenido complejo que sería difícil de manejar con argumentos de línea de comandos directos.

## EJEMPLO 1: Código Python con f-strings y comillas complejas

```bash
cat <<EOF | python3 cli.py create complex_function.py --from-stdin
def process_user_data(name, age, items):
    """Procesa datos de usuario con formateo complejo."""
    
    # F-strings con comillas anidadas
    greeting = f"Hola {name}, tienes {age} años"
    
    # Query SQL con comillas triples y variables
    query = f'''
    SELECT * FROM users 
    WHERE name = "{name}" 
    AND age >= {age}
    AND status = 'active'
    '''
    
    # Diccionario con strings complejos
    result = {
        'message': f"Usuario {name} procesado exitosamente",
        'query': query,
        'items': [f"Item {i}: {item}" for i, item in enumerate(items, 1)]
    }
    
    return result

# Ejemplo de uso
if __name__ == "__main__":
    user_items = ["laptop", "mouse", "keyboard"]
    data = process_user_data("Juan", 30, user_items)
    print(data)




## EJEMPLO 2: Componente React con JSX complejo

```bash
echo 'import React, { useState } from "react";

const UserCard = ({ user, onEdit }) => {
  const [isEditing, setIsEditing] = useState(false);
  
  return (
    <div className="user-card bg-white rounded-lg p-6">
      {isEditing ? (
        <input 
          value={user.name} 
          onChange={(e) => onEdit(user.id, e.target.value)}
          className="w-full p-2 border rounded"
        />
      ) : (
        <h3 className="text-xl font-bold">{user.name}</h3>
      )}
        {isEditing ? "Guardar" : "Editar"}
      </button>
    </div>
  );
};

export default UserCard;' | python3 cli.py create UserCard.jsx --from-stdin
```



## EJEMPLO 3: Configuración JSON con estructura compleja

```bash
echo '{
  "app": {
    "name": "MeStocker Advanced",
    "version": "2.1.0",
    "database": {
      "host": "localhost",
      "port": 5432,
      "credentials": {
        "user": "app_user",
        "password": "secure_pass"
      }
    },
    "api": {
      "endpoints": {
        "users": "/api/v2/users",
        "products": "/api/v2/products"
      },
      "cors": {
        "origins": ["https://app.com", "https://admin.com"]
      }
    }
  }
}' | python3 cli.py create advanced_config.json --from-stdin
```