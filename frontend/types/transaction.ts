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
  category_reductions: Record<string, number>;
};

export type GoalInput = {
  name: string;
  description?: string;
  target_amount?: number;
  target_date?: string;
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
  applied_strategy: Record<string, number>;
  updated_category_totals: UpdatedCategoryTotal[];
};

export type SimulationResponse = {
  statement_id: number;
  filename: string;
  simulation: SimulationResult;
};

export type EstimatedGoalCost = {
  name: string;
  description: string | null;
  estimated_amount: number;
  source: "user_input" | "web_estimate" | "fallback_estimate";
  confidence: "high" | "medium" | "low";
  rationale: string;
  target_date: string | null;
  horizon_months: number;
};

export type GoalFundingItem = {
  name: string;
  estimated_amount: number;
  target_date: string | null;
  horizon_months: number;
  required_monthly_savings: number;
};

export type GoalFundingPlan = {
  total_goal_amount: number;
  required_monthly_savings: number;
  projected_monthly_savings: number;
  projected_annual_savings: number;
  monthly_shortfall: number;
  feasible: boolean;
  goals: GoalFundingItem[];
};

export type CategoryReductionRecommendation = {
  category: string;
  current_monthly_spend: number;
  recommended_reduction_amount: number;
  recommended_reduction_pct: number;
  projected_monthly_spend: number;
  priority: number;
};

export type SimulationInsightResponse = {
  statement_id: number;
  filename: string;
  simulation: SimulationResult;
  estimated_goal_costs: EstimatedGoalCost[];
  goal_funding_plan: GoalFundingPlan;
  recommended_category_reductions: CategoryReductionRecommendation[];
  habit_challenges: string[];
  ai_explanation: string;
};