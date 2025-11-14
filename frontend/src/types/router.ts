export type RouteRequestPayload = {
  user_query: string;
  importance_precision: number;
  importance_latency: number;
  importance_cost: number;
};

export type RouteResponse = {
  output_text: string;
  chosen_model: string;
  latency_ms: number;
  cost_usd: number;
  quality_score: number;
  routing_explanation: string;
  timestamp: string;
};

export type MetricEntry = RouteResponse;
