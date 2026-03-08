export type Transaction = {
  date: string;
  merchant: string;
  description: string;
  amount: number;
  direction: string;
  category: string;
};

export type ParseResponse = {
  filename: string;
  statement_id: number;
  row_count: number;
  transactions: Transaction[];
};

export type CategoryTotal = {
  category: string;
  total: number;
};

export type MerchantTotal = {
  merchant: string;
  total: number;
};

export type StatementSummary = {
  statement_id: number;
  filename: string;
  total_spent: number;
  transaction_count: number;
  debit_count: number;
  credit_count: number;
  category_totals: CategoryTotal[];
  top_merchants: MerchantTotal[];
};

export type InsightsResponse = {
  statement_id: number;
  filename: string;
  insights: string;
};

export type StrategyRequest = {
  restaurants_reduction_pct: number;
  subscriptions_reduction_pct: number;
  shopping_reduction_pct: number;
};

export type UpdatedCategoryTotal = {
  category: string;
  original_total: number;
  projected_total: number;
};

export type SimulationResult = {
  original_total_spent: number;
  projected_total_spent: number;
  monthly_savings: number;
  annual_savings: number;
  applied_strategy: StrategyRequest;
  updated_category_totals: UpdatedCategoryTotal[];
};

export type SimulationResponse = {
  statement_id: number;
  filename: string;
  simulation: SimulationResult;
};

export type SimulationInsightResponse = {
  statement_id: number
  filename: string
  simulation: SimulationResult
  ai_explanation: string
}