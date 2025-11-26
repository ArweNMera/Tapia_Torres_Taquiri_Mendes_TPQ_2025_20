# Nuevos Endpoints PUT - Actualización de Adherencia y Síntomas

## Adherencia

### PUT `/api/v1/adherencia/{adh_id}`
Actualizar un registro de adherencia existente.

**Parámetros de ruta:**
- `adh_id` (int): ID del registro de adherencia

**Body (todos opcionales):**
```json
{
  "estado": "OK" | "PARCIAL" | "NO",
  "porcentaje": 85.5,
  "dificultad": "NINGUNA" | "BAJA" | "MEDIA" | "ALTA",
  "comentario": "Comentario actualizado"
}
```

**Respuesta 200:**
```json
{
  "adh_id": 123,
  "nin_id": 319,
  "men_id": 45,
  "mei_id": null,
  "fecha": "2025-11-26T00:00:00",
  "estado": "OK",
  "porcentaje": 85.5,
  "dificultad": "BAJA",
  "comentario": "Comentario actualizado"
}
```

**Errores:**
- 400: No se proporcionaron campos para actualizar
- 404: Registro de adherencia no encontrado
- 500: Error interno del servidor

---

## Síntomas

### PUT `/api/v1/sintomas/{sin_id}`
Actualizar un registro de síntoma existente.

**Parámetros de ruta:**
- `sin_id` (int): ID del registro de síntoma

**Body (todos opcionales):**
```json
{
  "tipo": "Dolor de estómago",
  "severidad": "LEVE" | "MODERADO" | "SEVERO",
  "duracion_dias": 3,
  "relacionado_menu": true,
  "notas": "Notas actualizadas"
}
```

**Respuesta 200:**
```json
{
  "sin_id": 456,
  "nin_id": 319,
  "fecha": "2025-11-25",
  "tipo": "Dolor de estómago",
  "severidad": "LEVE",
  "grado": 1,
  "duracion_dias": 3,
  "relacionado_menu": true,
  "notas": "Notas actualizadas",
  "creado_en": "2025-11-25T10:30:00"
}
```

**Errores:**
- 400: No se proporcionaron campos para actualizar
- 404: Registro de síntoma no encontrado
- 500: Error interno del servidor

---

## Características

✅ **Actualización parcial**: Solo se actualizan los campos proporcionados
✅ **Validación**: Verifica que el registro existe antes de actualizar
✅ **Tipo seguro**: Usa enums para valores válidos
✅ **Respuesta completa**: Retorna el registro actualizado
✅ **Manejo de errores**: Respuestas HTTP apropiadas

## Ejemplos de uso

### Actualizar solo el porcentaje de adherencia
```bash
curl -X PUT "https://backend.tecno-express.shop/api/v1/adherencia/123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"porcentaje": 90.0}'
```

### Actualizar severidad de síntoma
```bash
curl -X PUT "https://backend.tecno-express.shop/api/v1/sintomas/456" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"severidad": "MODERADO", "duracion_dias": 5}'
```
