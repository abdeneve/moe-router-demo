import type { RouteResponse } from '../types/router';

type RouterDecisionCardProps = {
  result: RouteResponse | null;
  isLoading: boolean;
};

export function RouterDecisionCard({ result, isLoading }: RouterDecisionCardProps) {
  return (
    <section className="card">
      <h2>Decisión del router</h2>
      {isLoading && <p className="status-text">Evaluando heurísticas...</p>}
      {!isLoading && !result && <p className="status-text">Envía una consulta para ver resultados.</p>}

      {result && (
        <div>
          <div className="grid-two-columns">
            <InfoBlock label="Modelo elegido" value={result.chosen_model} />
            <InfoBlock label="Score estimado" value={(result.quality_score * 100).toFixed(1) + '%'} />
            <InfoBlock label="Latencia" value={`${result.latency_ms.toFixed(0)} ms`} />
            <InfoBlock label="Costo" value={`$${result.cost_usd.toFixed(4)}`} />
          </div>
          <p style={{ marginTop: '1rem', color: '#0b1f32' }}>{result.routing_explanation}</p>
          <div className="response-output">{result.output_text}</div>
        </div>
      )}
    </section>
  );
}

type InfoBlockProps = {
  label: string;
  value: string;
};

function InfoBlock({ label, value }: InfoBlockProps) {
  return (
    <div>
      <p style={{ margin: 0, fontSize: '0.85rem', color: '#5b6784' }}>{label}</p>
      <p style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600, color: '#13223b' }}>{value}</p>
    </div>
  );
}
