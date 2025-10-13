# Ejemplo de uso del endpoint /ml/recomendacion_personalizada

## Descripción
Este endpoint genera recomendaciones nutricionales personalizadas para niños específicos usando un agente LLM (CORA) que considera:
- Datos personales del niño (edad, peso, talla, estado nutricional)
- Recetas disponibles en la base de datos
- Preguntas específicas del usuario
- Estado nutricional actual

## URL
```
POST /ml/recomendacion_personalizada
```

## Request Body
```json
{
  "id_nino": 1,
  "tipo_comida": "desayuno",
  "pregunta_usuario": "¿Qué puedo darle de desayuno a mi hijo que tenga buen valor nutricional?"
}
```

### Parámetros
- `id_nino` (int, requerido): ID del niño en la base de datos
- `tipo_comida` (string, requerido): Tipo de comida ("desayuno", "almuerzo", "cena", "merienda")
- `pregunta_usuario` (string, opcional): Pregunta específica del usuario

## Response Body
```json
{
  "recomendacion": "Basándome en el estado nutricional de Juan (6 meses, peso normal), te recomiendo para el desayuno: ...",
  "datos_nino": {
    "id": 1,
    "nombre": "Juan Pérez",
    "fecha_nacimiento": "2023-08-15",
    "sexo": "M",
    "peso_kg": 7.5,
    "talla_cm": 65.0,
    "imc": 17.8,
    "edad_meses": 6,
    "estado_nutricional": "NORMAL",
    "diagnostico": "Peso normal para la edad",
    "entidad": "Hospital Central",
    "codigo_entidad": "HC001"
  },
  "recetas_disponibles": [
    {
      "id": 1,
      "nombre": "Avena con frutas",
      "descripcion": "Avena cocida con manzana y plátano",
      "tipo_comida": "desayuno",
      "calorias": 150,
      "proteinas": 4.5,
      "carbohidratos": 28.0,
      "grasas": 2.5,
      "puntuacion": 8.5
    }
  ],
  "estado_nutricional": {
    "diagnostico": "Peso normal para la edad",
    "estado_actual": "NORMAL",
    "imc": 17.8,
    "peso_kg": 7.5,
    "talla_cm": 65.0,
    "edad_meses": 6,
    "sexo": "M"
  },
  "used_llm": true
}
```

## Ejemplos de uso

### 1. Recomendación general para desayuno
```json
{
  "id_nino": 1,
  "tipo_comida": "desayuno"
}
```

### 2. Pregunta específica sobre almuerzo
```json
{
  "id_nino": 2,
  "tipo_comida": "almuerzo",
  "pregunta_usuario": "¿Mi hija puede comer pescado? Tiene 3 años."
}
```

### 3. Recomendación para merienda con consideraciones nutricionales
```json
{
  "id_nino": 3,
  "tipo_comida": "merienda",
  "pregunta_usuario": "¿Qué opciones saludables hay para merienda considerando que tiene sobrepeso?"
}
```

## Funcionalidades

### Integración con Base de Datos
- Consulta datos del niño desde tabla `ninos`
- Obtiene recetas usando procedimiento `sp_top_recetas_por_nombre`
- Incluye información de entidades médicas

### Agente LLM (CORA)
- Genera recomendaciones personalizadas basadas en evidencia científica
- Considera estado nutricional específico del niño
- Adapta recomendaciones según edad y condiciones
- Proporciona consejos seguros y apropiados

### Manejo de Errores
- Niño no encontrado: 404
- Base de datos no disponible: 503
- Errores internos: 500

## Consideraciones de Seguridad
- Recomendaciones no sustituyen consejo médico profesional
- Siempre sugiere consultar con especialistas cuando sea necesario
- Recomendaciones basadas en datos científicos validados
