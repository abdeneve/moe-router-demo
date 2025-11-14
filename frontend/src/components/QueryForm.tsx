import { FormEvent, useState } from 'react';
import type { RouteRequestPayload } from '../types/router';

export type QueryFormValues = RouteRequestPayload;

type QueryFormProps = {
  initialValues?: QueryFormValues;
  isSubmitting: boolean;
  onSubmit: (values: QueryFormValues) => void;
};

const precisionLabel = 'Precisión';
const latencyLabel = 'Latencia';
const costLabel = 'Costo';

const defaultValues: QueryFormValues = {
  user_query: '',
  importance_precision: 0.7,
  importance_latency: 0.5,
  importance_cost: 0.3
};

export function QueryForm({
  initialValues = defaultValues,
  isSubmitting,
  onSubmit
}: QueryFormProps) {
  const [values, setValues] = useState<QueryFormValues>(initialValues);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!values.user_query.trim()) {
      return;
    }
    onSubmit(values);
  };

  const handleSliderChange = (key: keyof QueryFormValues) => (event: FormEvent<HTMLInputElement>) => {
    const nextValue = Number(event.currentTarget.value);
    setValues((prev) => ({
      ...prev,
      [key]: nextValue
    }));
  };

  const handleQueryChange = (event: FormEvent<HTMLTextAreaElement>) => {
    const nextQuery = event.currentTarget.value;
    setValues((prev) => ({
      ...prev,
      user_query: nextQuery
    }));
  };


  return (
    <form onSubmit={handleSubmit} className="card">
      <h2>Probar router</h2>
      <label htmlFor="user-query">Prompt</label>
      <textarea
        id="user-query"
        value={values.user_query}
        onInput={handleQueryChange}
        rows={4}
        placeholder="Ejemplo: Resume este artículo con foco en ideas accionables..."
        disabled={isSubmitting}
        style={{
          width: '100%',
          borderRadius: 12,
          border: '1px solid #d0d7e6',
          padding: '0.85rem',
          fontSize: '1rem',
          resize: 'vertical'
        }}
      />
      <div className="grid-two-columns" style={{ marginTop: '1.5rem' }}>
        <SliderControl
          id="precision"
          label={precisionLabel}
          value={values.importance_precision}
          onChange={handleSliderChange('importance_precision')}
          disabled={isSubmitting}
        />
        <SliderControl
          id="latency"
          label={latencyLabel}
          value={values.importance_latency}
          onChange={handleSliderChange('importance_latency')}
          disabled={isSubmitting}
        />
        <SliderControl
          id="cost"
          label={costLabel}
          value={values.importance_cost}
          onChange={handleSliderChange('importance_cost')}
          disabled={isSubmitting}
        />
      </div>
      <button
        type="submit"
        disabled={isSubmitting || !values.user_query.trim()}
        style={{
          marginTop: '1.5rem',
          width: '100%',
          background: isSubmitting ? '#94a3b8' : '#2563eb',
          color: 'white',
          border: 'none',
          borderRadius: 999,
          padding: '0.9rem 1.25rem',
          fontSize: '1rem',
          fontWeight: 600,
          cursor: isSubmitting ? 'not-allowed' : 'pointer',
          transition: 'background 0.2s ease'
        }}
      >
        {isSubmitting ? 'Enviando...' : 'Enviar al router'}
      </button>
    </form>
  );
}

type SliderControlProps = {
  id: string;
  label: string;
  value: number;
  disabled?: boolean;
  onChange: (event: FormEvent<HTMLInputElement>) => void;
};

function SliderControl({ id, label, value, disabled, onChange }: SliderControlProps) {
  return (
    <label htmlFor={id} style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
      <span style={{ fontWeight: 600, color: '#0f1f38' }}>
        {label}: {(value * 100).toFixed(0)}%
      </span>
      <input
        type="range"
        id={id}
        min={0}
        max={1}
        step={0.05}
        value={value}
        onInput={onChange}
        disabled={disabled}
      />
    </label>
  );
}
