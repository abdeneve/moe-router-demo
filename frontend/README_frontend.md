# Frontend MoE Router

Cliente React + TypeScript para la demo del router Mixture-of-Experts.

## Scripts

- `pnpm install` / `npm install`
- `npm run dev` – inicia Vite en `http://localhost:5173`.
- `npm run build` – compila a producción.
- `npm run preview` – sirve el build.
- `npm run lint` – valida tipos con `tsc`.

## Variables de entorno

Configura un archivo `.env` (o variables de shell) con:

```ini
VITE_API_BASE_URL=http://localhost:8000
```

Si tu backend expone `/api/route`, ajusta el valor a `http://localhost:8000/api`.

## Arquitectura

- `src/components/QueryForm.tsx`: entrada de prompt + sliders de prioridad.
- `src/components/RouterDecisionCard.tsx`: muestra el modelo elegido y la salida.
- `src/components/MetricsTable.tsx`: historial local de métricas (timestamp, modelo, latencia, costo, score).
- `src/services/apiClient.ts`: cliente `fetch` con tipado estricto.
- `src/types/router.ts`: contratos compartidos con el backend.

El estado principal vive en `src/App.tsx`, donde se coordina el llamado al backend y la actualización del historial.
