#!/bin/bash
# Surgical Modifier Wrapper - Manejo seguro de template literals
# Uso: ./sm_wrapper.sh create file.tsx "contenido con template literals"

operation="$1"
file="$2" 
pattern="$3"
content="$4"

# Función para detectar template literals problemáticos
contains_template_literals() {
    local input="$1"
    [[ "$input" == *'${'* ]]
}

# Si el contenido contiene ${, usar archivo temporal
if contains_template_literals "$content"; then
    echo "🔧 Detectados template literals - usando modo seguro..."
    temp_file=$(mktemp)
    echo -n "$content" > "$temp_file"
    python3 cli.py "$operation" "$file" "$pattern" --file-input "$temp_file" "${@:5}"
    rm "$temp_file"
else
    # Uso normal
    python3 cli.py "$operation" "$file" "$pattern" "$content" "${@:5}"
fi
