import type { RouteRequestPayload, RouteResponse } from '../types/router';

const DEFAULT_BASE_URL = 'http://localhost:8000';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? DEFAULT_BASE_URL).replace(/\/$/, '');

export async function routeQuery(payload: RouteRequestPayload): Promise<RouteResponse> {
  const response = await fetch(`${API_BASE_URL}/route`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'No se pudo contactar al backend');
  }

  const data = (await response.json()) as RouteResponse;

  return data;
}
