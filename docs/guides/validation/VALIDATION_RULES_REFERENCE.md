# Guía de Referencia: Reglas de Validación del Formulario de Envío

## Tabla de Validaciones Implementadas

| Campo | Tipo | Requerido | Validaciones | Ejemplo Válido | Ejemplo Inválido |
|-------|------|-----------|--------------|----------------|------------------|
| **Nombre Completo** | Text | Sí | • Min: 3 caracteres<br>• Max: 100 caracteres<br>• Solo letras y espacios<br>• Sin espacios múltiples<br>• Debe tener apellido | "Juan Pérez García" | "dsdad"<br>"Juan"<br>"Juan  Pérez" |
| **Teléfono Celular** | Tel | Sí | • Exactamente 10 dígitos<br>• Debe iniciar con 3<br>• Solo números<br>• Formato colombiano | "3001234567"<br>"3123456789" | "123456789"<br>"4001234567"<br>"300123456" |
| **Dirección** | Text | Sí | • Min: 10 caracteres<br>• Max: 200 caracteres<br>• Debe incluir números<br>• Caracteres permitidos: letras, números, #, -, ,, ., ° | "Carrera 15 # 93-47, Apto 501" | "DSADSDS"<br>"Calle sin numero" |
| **Ciudad** | Text | Sí | • Min: 3 caracteres<br>• Max: 50 caracteres<br>• Solo letras y espacios | "Bogotá"<br>"Medellín"<br>"Cali" | "DSAFDF"<br>"123" |
| **Departamento** | Select | Sí | • Debe estar en lista de 32 departamentos colombianos | "Cundinamarca"<br>"Antioquia"<br>"Valle del Cauca" | "California"<br>"" (vacío) |
| **Código Postal** | Text | Sí | • Exactamente 6 dígitos<br>• Solo números | "110111"<br>"050001" | "101234"<br>"12345"<br>"1234567" |
| **Información Adicional** | Textarea | No | • Max: 200 caracteres<br>• Caracteres permitidos: letras, números, ., ,, -, :, ;, °, # | "Casa de dos pisos, portón negro" | "A5f?a" (si tiene ? u otros símbolos raros) |

## Mensajes de Error por Campo

### Nombre Completo
```
❌ Campo vacío → "El nombre completo es requerido"
❌ Menos de 3 caracteres → "El nombre debe tener al menos 3 caracteres"
❌ Más de 100 caracteres → "El nombre no puede exceder 100 caracteres"
❌ Contiene números/símbolos → "El nombre solo puede contener letras y espacios"
❌ Espacios múltiples → "No se permiten espacios múltiples"
❌ Solo un nombre → "Debe incluir nombre y apellido"
✅ Válido: "Juan Pérez García"
```

### Teléfono Celular
```
❌ Campo vacío → "El número de teléfono es requerido"
❌ No inicia con 3 → "Debe ser un celular colombiano válido (10 dígitos comenzando con 3)"
❌ No tiene 10 dígitos → "Formato inválido. Ej: 3001234567"
❌ Contiene letras → "Debe ser un celular colombiano válido (10 dígitos comenzando con 3)"
✅ Válido: "3001234567"
```

### Dirección
```
❌ Campo vacío → "La dirección es requerida"
❌ Menos de 10 caracteres → "La dirección debe tener al menos 10 caracteres"
❌ Más de 200 caracteres → "La dirección no puede exceder 200 caracteres"
❌ Caracteres raros → "La dirección contiene caracteres no permitidos"
❌ Sin números → "La dirección debe incluir números"
❌ Solo espacios → "La dirección es muy corta"
✅ Válido: "Carrera 15 # 93-47, Apartamento 501"
```

### Ciudad
```
❌ Campo vacío → "La ciudad es requerida"
❌ Menos de 3 caracteres → "El nombre de la ciudad debe tener al menos 3 caracteres"
❌ Más de 50 caracteres → "El nombre de la ciudad es muy largo"
❌ Contiene números/símbolos → "El nombre de la ciudad solo puede contener letras y espacios"
✅ Válido: "Bogotá"
```

### Departamento
```
❌ No seleccionado → "Debe seleccionar un departamento"
❌ Valor no en lista → "Departamento inválido"
✅ Válido: "Cundinamarca", "Antioquia", "Valle del Cauca", etc.
```

### Código Postal
```
❌ Campo vacío → "El código postal es requerido"
❌ No tiene 6 dígitos → "El código postal debe tener exactamente 6 dígitos"
❌ Contiene letras → "El código postal debe tener exactamente 6 dígitos"
✅ Válido: "110111"
```

### Información Adicional (Opcional)
```
❌ Más de 200 caracteres → "La información adicional no puede exceder 200 caracteres"
❌ Caracteres raros → "Contiene caracteres no permitidos"
✅ Válido: "Casa de dos pisos color blanco, portón negro"
✅ Válido: "" (vacío, es opcional)
```

## Lista de Departamentos Colombianos Válidos

```
1. Amazonas
2. Antioquia
3. Arauca
4. Atlántico
5. Bolívar
6. Boyacá
7. Caldas
8. Caquetá
9. Casanare
10. Cauca
11. Cesar
12. Chocó
13. Córdoba
14. Cundinamarca
15. Guainía
16. Guaviare
17. Huila
18. La Guajira
19. Magdalena
20. Meta
21. Nariño
22. Norte de Santander
23. Putumayo
24. Quindío
25. Risaralda
26. San Andrés y Providencia
27. Santander
28. Sucre
29. Tolima
30. Valle del Cauca
31. Vaupés
32. Vichada
```

## Patrones Regex Utilizados

```typescript
// Nombre completo - Solo letras (con acentos) y espacios
/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/

// Teléfono celular - 10 dígitos comenzando con 3
/^3\d{9}$/

// Dirección - Letras, números y símbolos permitidos
/^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s#\-,.°]+$/

// Ciudad - Solo letras (con acentos) y espacios
/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/

// Código postal - Exactamente 6 dígitos
/^\d{6}$/

// Información adicional - Letras, números y símbolos comunes
/^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s.,\-:;°#]+$/
```

## Comportamiento del Botón "Guardar Dirección"

### Estado: Deshabilitado (Gris)
```
Condiciones:
• Formulario tiene errores de validación
• Algún campo requerido está vacío
• Está enviando datos (isSubmitting)

Visual:
• Fondo gris (bg-gray-300)
• Texto gris (text-gray-500)
• Cursor no permitido (cursor-not-allowed)
• Tooltip: "Completa todos los campos correctamente para continuar"
```

### Estado: Habilitado (Azul)
```
Condiciones:
• Todos los campos requeridos completos
• Todas las validaciones pasadas
• No está enviando datos

Visual:
• Fondo azul (bg-blue-600)
• Texto blanco (text-white)
• Hover: bg-blue-700
• Clickeable
```

## Flujo de Validación

```
1. Usuario ingresa texto
   ↓
2. React Hook Form valida en tiempo real (onChange)
   ↓
3. Si hay error:
   • Borde del input se pone rojo
   • Mensaje de error aparece debajo del campo
   • Botón se deshabilita
   ↓
4. Usuario corrige el error
   ↓
5. Validación pasa:
   • Borde vuelve a gris
   • Mensaje de error desaparece
   ↓
6. Cuando TODOS los campos son válidos:
   • Botón se habilita (azul)
   • Usuario puede hacer submit
   ↓
7. Al hacer submit:
   • Validación final
   • Si pasa: guarda y continúa
   • Si falla: muestra errores
```

## Casos de Uso

### Caso 1: Usuario intenta datos inválidos (Como el bug original)
```
Input:
{
  name: "dsdad",
  phone: "123456789",
  address: "DSADSDS",
  city: "DSAFDF",
  department: "",
  postal_code: "12345"
}

Resultado:
❌ Nombre: "Debe incluir nombre y apellido"
❌ Teléfono: "Formato inválido. Ej: 3001234567"
❌ Dirección: "La dirección debe incluir números"
❌ Ciudad: "El nombre de la ciudad solo puede contener letras y espacios"
❌ Departamento: "Debe seleccionar un departamento"
❌ Código postal: "El código postal debe tener exactamente 6 dígitos"
🔴 Botón DESHABILITADO
```

### Caso 2: Usuario ingresa datos válidos
```
Input:
{
  name: "Juan Pérez García",
  phone: "3001234567",
  address: "Carrera 15 # 93-47, Apartamento 501",
  city: "Bogotá",
  department: "Cundinamarca",
  postal_code: "110111"
}

Resultado:
✅ Todos los campos válidos
✅ Sin mensajes de error
🟢 Botón HABILITADO
✅ Puede hacer submit
```

### Caso 3: Usuario corrige datos paso a paso
```
1. Ingresa "Juan" → ❌ "Debe incluir nombre y apellido"
2. Corrige a "Juan Pérez" → ✅ Campo válido
3. Ingresa "12345" en código postal → ❌ "Exactamente 6 dígitos"
4. Corrige a "110111" → ✅ Campo válido
5. Todos los campos válidos → 🟢 Botón se habilita
```

## Seguridad

### Prevención de SQL Injection
```typescript
// Los patrones regex solo permiten caracteres seguros:

✅ Permitido: "Carrera 15 # 93-47"
❌ Bloqueado: "'; DROP TABLE usuarios; --"
❌ Bloqueado: "<script>alert('XSS')</script>"
❌ Bloqueado: "../../etc/passwd"
```

### Sanitización Automática
```typescript
// Todos los valores se limpian con .trim()
Input: "  Juan Pérez  "
Guardado: "Juan Pérez"
```

## Testing Manual Checklist

- [ ] Campo nombre acepta "Juan Pérez" → ✅
- [ ] Campo nombre rechaza "Juan" (sin apellido) → ❌
- [ ] Campo teléfono acepta "3001234567" → ✅
- [ ] Campo teléfono rechaza "123456789" (no inicia con 3) → ❌
- [ ] Campo dirección acepta "Calle 123 # 45-67" → ✅
- [ ] Campo dirección rechaza "Calle sin numero" → ❌
- [ ] Campo ciudad acepta "Bogotá" → ✅
- [ ] Campo ciudad rechaza "123" → ❌
- [ ] Campo departamento requiere selección → ❌ (si está vacío)
- [ ] Campo código postal acepta "110111" (6 dígitos) → ✅
- [ ] Campo código postal rechaza "12345" (5 dígitos) → ❌
- [ ] Botón deshabilitado cuando hay errores → ✅
- [ ] Botón habilitado cuando todo es válido → ✅
- [ ] Submit solo funciona con datos válidos → ✅

## Referencias de Implementación

- **Framework**: React Hook Form v7.62.0
- **Modo de validación**: `onChange` (tiempo real)
- **Archivo principal**: `frontend/src/components/checkout/AddressForm.tsx`
- **TypeScript**: Tipos estrictos con interfaces `AddressFormData`
- **Accesibilidad**: Atributos ARIA (`aria-invalid`, `aria-describedby`, `role="alert"`)
