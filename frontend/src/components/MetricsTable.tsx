import type { MetricEntry } from '../types/router';

type MetricsTableProps = {
  entries: MetricEntry[];
};

export function MetricsTable({ entries }: MetricsTableProps) {
  return (
    <section className="card">
      <h2>Métricas de la sesión</h2>
      {entries.length === 0 ? (
        <p className="status-text">Aún no hay registros.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="metrics-table">
            <thead>
              <tr>
                <th>Hora</th>
                <th>Modelo</th>
                <th>Latencia</th>
                <th>Costo</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.timestamp + entry.chosen_model}>
                  <td>{formatTimestamp(entry.timestamp)}</td>
                  <td>{entry.chosen_model}</td>
                  <td>{Number(entry.latency_ms).toFixed(0)} ms</td>
                  <td>${entry.cost_usd.toFixed(4)}</td>
                  <td>{(entry.quality_score * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function formatTimestamp(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
