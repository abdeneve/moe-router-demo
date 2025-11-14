import { useCallback, useState } from 'react';
import { QueryForm } from './components/QueryForm';
import { RouterDecisionCard } from './components/RouterDecisionCard';
import { MetricsTable } from './components/MetricsTable';
import { routeQuery } from './services/apiClient';
import type { MetricEntry, RouteRequestPayload, RouteResponse } from './types/router';

const MAX_HISTORY = 20;

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastDecision, setLastDecision] = useState<RouteResponse | null>(null);
  const [history, setHistory] = useState<MetricEntry[]>([]);

  const handleSubmit = useCallback(async (payload: RouteRequestPayload) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await routeQuery(payload);
      setLastDecision(result);
      setHistory((prev) => {
        const next = [...prev, result];
        if (next.length > MAX_HISTORY) {
          next.shift();
        }
        return next;
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="app-shell">
      <header style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <p style={{ fontSize: '0.9rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: '#4c5c7a' }}>
          Demo Mixture-of-Experts Router
        </p>
        <h1 style={{ margin: '0.35rem 0 0.75rem', fontSize: '2.2rem', color: '#0b1f32' }}>
          Balancea precisión, latencia y costo
        </h1>
        <p style={{ margin: 0, color: '#5b6784' }}>
          Envía cualquier prompt y observa cómo el router selecciona el modelo óptimo.
        </p>
      </header>

      <QueryForm onSubmit={handleSubmit} isSubmitting={isLoading} />

      {error && <p className="status-text error-text">{error}</p>}

      <RouterDecisionCard result={lastDecision} isLoading={isLoading} />

      <MetricsTable entries={history} />
    </div>
  );
}
