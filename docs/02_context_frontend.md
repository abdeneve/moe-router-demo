# Contexto para generación de frontend (Codex)

## Estilo

- React + TypeScript.
- UI simple y legible:
  - Form arriba.
  - Resultado + métricas abajo.

## Componentes

- `QueryForm`
  - Textarea para `user_query`.
  - Sliders o selects para importancia de precisión/latencia/costo.
  - Botón "Enviar".

- `RouterDecisionCard`
  - Muestra:
    - modelo elegido,
    - explicación corta (por qué se eligió),
    - texto de salida del modelo.

- `MetricsTable`
  - Tabla con un registro por request:
    - timestamp,
    - modelo,
    - latencia,
    - costo,
    - score.

## Comunicación con backend

- `services/apiClient.ts`
  - Función `routeQuery(payload)` -> `Promise<RouterResult>`.
  - URL base configurada en una constante.
