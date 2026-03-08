"use client";

import { useState } from "react";
import { api } from "../lib/api";
import { formatCurrency } from "../lib/format";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  CategoryReductionRecommendation,
  CategoryTotal,
  EstimatedGoalCost,
  GoalFundingPlan,
  GoalInput,
  SimulationInsightResponse,
  SimulationResult,
  StrategyRequest,
} from "../types/transaction";

type Props = {
  statementId: number;
  categoryTotals: CategoryTotal[];
};

type SliderRowProps = {
  label: string;
  value: number;
  recordedAmount: number;
  reductionAmount: number;
  projectedAmount: number;
  onChange: (value: number) => void;
};

type GoalDraft = GoalInput & { id: string };

function SliderRow({
  label,
  value,
  recordedAmount,
  reductionAmount,
  projectedAmount,
  onChange,
}: SliderRowProps) {
  return (
    <div className="rounded-2xl border border-white/15 bg-white/[0.03] p-4 shadow-sm">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <label className="text-sm font-medium text-slate-100">{label}</label>
        <span className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-sm font-semibold text-cyan-100">
          {value}%
        </span>
      </div>

      <input
        type="range"
        min={0}
        max={100}
        step={5}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-cyan-300"
      />

      <div className="mt-2 flex justify-between text-xs text-slate-400">
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </div>

      <div className="mt-3 grid gap-2 rounded-xl border border-white/15 bg-white/[0.03] px-3 py-2 text-xs sm:grid-cols-3">
        <div>
          <p className="text-slate-400">Recorded</p>
          <p className="font-semibold text-slate-100">{formatCurrency(recordedAmount)}</p>
        </div>
        <div>
          <p className="text-slate-400">Reduction ({value}%)</p>
          <p className="font-semibold text-emerald-300">-{formatCurrency(reductionAmount)}</p>
        </div>
        <div>
          <p className="text-slate-400">Projected</p>
          <p className="font-semibold text-cyan-100">{formatCurrency(projectedAmount)}</p>
        </div>
      </div>
    </div>
  );
}

function GoalCard({
  goal,
  onChange,
  onRemove,
}: {
  goal: GoalDraft;
  onChange: (goalId: string, patch: Partial<GoalDraft>) => void;
  onRemove: (goalId: string) => void;
}) {
  return (
    <div className="rounded-2xl border border-white/15 bg-white/[0.03] p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-100">Goal</p>
        <button
          type="button"
          onClick={() => onRemove(goal.id)}
          className="text-xs text-rose-300 hover:text-rose-200"
        >
          Remove
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <input
          value={goal.name ?? ""}
          onChange={(e) => onChange(goal.id, { name: e.target.value })}
          placeholder="Goal name (e.g., Camera lens)"
          className="rounded-xl border border-white/20 bg-slate-900/70 px-3 py-2 text-sm text-white placeholder:text-slate-500"
        />
        <input
          value={goal.target_amount ?? ""}
          onChange={(e) =>
            onChange(goal.id, {
              target_amount: e.target.value === "" ? undefined : Number(e.target.value),
            })
          }
          type="number"
          min={0}
          step="0.01"
          placeholder="Target amount (optional)"
          className="rounded-xl border border-white/20 bg-slate-900/70 px-3 py-2 text-sm text-white placeholder:text-slate-500"
        />
        <input
          value={goal.target_date ?? ""}
          onChange={(e) => onChange(goal.id, { target_date: e.target.value || undefined })}
          type="date"
          lang="en-US"
          aria-label="Target date (optional)"
          title="Target date (optional)"
          className="goal-date-input rounded-xl border border-white/20 bg-slate-900/70 px-3 py-2 text-sm text-white"
        />
      </div>

      <input
        value={goal.description ?? ""}
        onChange={(e) => onChange(goal.id, { description: e.target.value })}
        placeholder="Description (optional)"
        className="mt-3 w-full rounded-xl border border-white/20 bg-slate-900/70 px-3 py-2 text-sm text-white placeholder:text-slate-500"
      />

      {goal.target_amount == null && (
        <p className="mt-2 text-xs text-cyan-200">
          Auto-estimate amount: AI will estimate this goal using web context.
        </p>
      )}
    </div>
  );
}

function StrategyAnalysisLoading() {
  return (
    <div className="rounded-2xl border border-emerald-300/25 bg-emerald-400/5 p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-emerald-400" />
        <p className="text-sm font-medium text-emerald-300">
          Gemini is analyzing your strategy...
        </p>
      </div>

      <p className="mt-2 text-sm text-slate-300">
        This can take a few seconds while it evaluates trade-offs and savings opportunities.
      </p>

      <div className="mt-4 space-y-3">
        <div className="h-4 w-full animate-pulse rounded bg-white/10" />
        <div className="h-4 w-5/6 animate-pulse rounded bg-white/10" />
        <div className="h-4 w-4/6 animate-pulse rounded bg-white/10" />
      </div>
    </div>
  );
}

function toReadableStrategyMarkdown(markdown: string) {
  const lines = markdown.split(/\r?\n/);
  const output: string[] = [];

  const flushMetricStreak = (streak: string[]) => {
    if (streak.length < 2) {
      output.push(...streak);
      return;
    }

    for (const line of streak) {
      const match = line.match(/^(\*\*)?([^:*]+)(\*\*)?:\s*(.+)$/);
      if (!match) {
        output.push(line);
        continue;
      }
      const label = match[2].trim();
      const value = match[4].trim();
      output.push(`- **${label}:** ${value}`);
    }
  };

  const isMetricLine = (line: string) =>
    /^(\*\*)?[^:*][^:]{1,40}(\*\*)?:\s+.+$/.test(line.trim());

  let streak: string[] = [];
  for (const line of lines) {
    if (isMetricLine(line)) {
      streak.push(line.trim());
      continue;
    }
    if (streak.length > 0) {
      flushMetricStreak(streak);
      streak = [];
    }
    output.push(line);
  }

  if (streak.length > 0) {
    flushMetricStreak(streak);
  }

  return output.join("\n");
}

function findRecordedTotal(categoryTotals: CategoryTotal[], aliases: string[]) {
  const normalizedAliases = aliases.map((alias) => alias.toLowerCase());
  const found = categoryTotals.find((item) =>
    normalizedAliases.includes(item.category.toLowerCase())
  );
  return found?.total ?? 0;
}

export default function StrategySimulator({ statementId, categoryTotals }: Props) {
  const [strategy, setStrategy] = useState<StrategyRequest>({
    restaurants_reduction_pct: 40,
    subscriptions_reduction_pct: 20,
    shopping_reduction_pct: 25,
  });

  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [estimatedGoalCosts, setEstimatedGoalCosts] = useState<EstimatedGoalCost[]>([]);
  const [goalFundingPlan, setGoalFundingPlan] = useState<GoalFundingPlan | null>(null);
  const [recommendedCuts, setRecommendedCuts] = useState<CategoryReductionRecommendation[]>([]);
  const [habitChallenges, setHabitChallenges] = useState<string[]>([]);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [goals, setGoals] = useState<GoalDraft[]>([
    { id: "goal-1", name: "", description: "", target_amount: undefined, target_date: "" },
  ]);

  const restaurantsRecorded = findRecordedTotal(categoryTotals, [
    "restaurants",
    "restaurant",
  ]);
  const subscriptionsRecorded = findRecordedTotal(categoryTotals, [
    "subscriptions",
    "subscription",
  ]);
  const shoppingRecorded = findRecordedTotal(categoryTotals, ["shopping", "shop"]);

  const runSimulation = async () => {
    try {
      setLoading(true);
      setError(null);
      setAiExplanation(null);
      setSimulation(null);
      setEstimatedGoalCosts([]);
      setGoalFundingPlan(null);
      setRecommendedCuts([]);
      setHabitChallenges([]);

      const normalizedGoals = goals
        .filter((goal) => goal.name?.trim())
        .map((goal) => ({
          name: goal.name.trim(),
          description: goal.description?.trim() || undefined,
          target_amount: goal.target_amount,
          target_date: goal.target_date || undefined,
        }));

      const response = await api.post<SimulationInsightResponse>(
        `/simulation-insights/${statementId}`,
        {
          strategy,
          goals: normalizedGoals,
        }
      );

      setSimulation(response.data.simulation);
      setEstimatedGoalCosts(response.data.estimated_goal_costs);
      setGoalFundingPlan(response.data.goal_funding_plan);
      setRecommendedCuts(response.data.recommended_category_reductions);
      setHabitChallenges(response.data.habit_challenges);
      setAiExplanation(response.data.ai_explanation);
    } catch (err) {
      console.error("Simulation failed:", err);
      setError("Failed to run simulation.");
      setSimulation(null);
      setEstimatedGoalCosts([]);
      setGoalFundingPlan(null);
      setRecommendedCuts([]);
      setHabitChallenges([]);
      setAiExplanation(null);
    } finally {
      setLoading(false);
    }
  };

  const updateGoal = (goalId: string, patch: Partial<GoalDraft>) => {
    setGoals((prev) => prev.map((goal) => (goal.id === goalId ? { ...goal, ...patch } : goal)));
  };

  const addGoal = () => {
    const goalId = `goal-${Date.now()}`;
    setGoals((prev) => [
      ...prev,
      { id: goalId, name: "", description: "", target_amount: undefined, target_date: "" },
    ]);
  };

  const removeGoal = (goalId: string) => {
    setGoals((prev) => {
      if (prev.length <= 1) {
        return prev;
      }
      return prev.filter((goal) => goal.id !== goalId);
    });
  };

  return (
    <div className="space-y-6 rounded-3xl border border-violet-300/20 bg-gradient-to-br from-slate-900/90 via-slate-900/80 to-violet-950/50 p-4 shadow-[0_16px_45px_rgba(26,18,63,0.35)] sm:p-6">
      <div className="space-y-1">
        <h3 className="text-lg font-semibold text-white sm:text-xl">Strategy Simulator</h3>
        <p className="text-sm text-slate-300">
          Add savings goals, then test how reducing discretionary spending can fund them.
        </p>
      </div>

      <div className="space-y-3 rounded-2xl border border-cyan-300/20 bg-cyan-500/5 p-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-cyan-100">Personal Goals</h4>
          <button
            type="button"
            onClick={addGoal}
            disabled={goals.length >= 5}
            className="rounded-lg border border-cyan-300/40 px-3 py-1 text-xs font-semibold text-cyan-100 hover:bg-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Add goal
          </button>
        </div>

        <div className="space-y-3">
          {goals.map((goal) => (
            <GoalCard key={goal.id} goal={goal} onChange={updateGoal} onRemove={removeGoal} />
          ))}
        </div>
      </div>

      <div className="grid gap-4">
        <SliderRow
          label="Restaurant reduction"
          value={strategy.restaurants_reduction_pct}
          recordedAmount={restaurantsRecorded}
          reductionAmount={
            (restaurantsRecorded * strategy.restaurants_reduction_pct) / 100
          }
          projectedAmount={
            restaurantsRecorded -
            (restaurantsRecorded * strategy.restaurants_reduction_pct) / 100
          }
          onChange={(value) =>
            setStrategy((prev) => ({
              ...prev,
              restaurants_reduction_pct: value,
            }))
          }
        />

        <SliderRow
          label="Subscription reduction"
          value={strategy.subscriptions_reduction_pct}
          recordedAmount={subscriptionsRecorded}
          reductionAmount={
            (subscriptionsRecorded * strategy.subscriptions_reduction_pct) / 100
          }
          projectedAmount={
            subscriptionsRecorded -
            (subscriptionsRecorded * strategy.subscriptions_reduction_pct) / 100
          }
          onChange={(value) =>
            setStrategy((prev) => ({
              ...prev,
              subscriptions_reduction_pct: value,
            }))
          }
        />

        <SliderRow
          label="Shopping reduction"
          value={strategy.shopping_reduction_pct}
          recordedAmount={shoppingRecorded}
          reductionAmount={
            (shoppingRecorded * strategy.shopping_reduction_pct) / 100
          }
          projectedAmount={
            shoppingRecorded - (shoppingRecorded * strategy.shopping_reduction_pct) / 100
          }
          onChange={(value) =>
            setStrategy((prev) => ({
              ...prev,
              shopping_reduction_pct: value,
            }))
          }
        />
      </div>

      <div className="flex flex-col items-start gap-3 sm:flex-row sm:items-center">
        <button
          onClick={runSimulation}
          disabled={loading}
          className="w-full rounded-2xl bg-gradient-to-r from-cyan-300 via-blue-300 to-violet-300 px-5 py-3 font-semibold text-slate-900 transition hover:brightness-110 disabled:opacity-50 sm:w-auto"
        >
          {loading ? "Running..." : "Run Simulation"}
        </button>

        <div className="text-sm text-slate-400 sm:max-w-md">
          Adjust the sliders, then generate a savings scenario.
        </div>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {loading && <StrategyAnalysisLoading />}

      {simulation && (
        <div className="space-y-5">
          {estimatedGoalCosts.length > 0 && (
            <div className="rounded-2xl border border-white/15 bg-white/[0.03] p-5 shadow-sm">
              <h4 className="text-base font-semibold text-white">Goal Cost Estimates</h4>
              <div className="mt-4 space-y-3">
                {estimatedGoalCosts.map((goal) => (
                  <div
                    key={`${goal.name}-${goal.target_date ?? "none"}`}
                    className="rounded-xl border border-white/15 px-4 py-3"
                  >
                    <p className="font-medium text-slate-100">{goal.name}</p>
                    <p className="text-sm text-slate-300">
                      {formatCurrency(goal.estimated_amount)} ({goal.source.replace("_", " ")},{" "}
                      {goal.confidence} confidence)
                    </p>
                    <p className="text-xs text-slate-400">{goal.rationale}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {goalFundingPlan && (
            <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/5 p-5 shadow-sm">
              <h4 className="text-base font-semibold text-emerald-100">Goal Funding Plan</h4>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">Total goals</p>
                  <p className="text-lg font-semibold text-white">
                    {formatCurrency(goalFundingPlan.total_goal_amount)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">Required monthly</p>
                  <p className="text-lg font-semibold text-cyan-100">
                    {formatCurrency(goalFundingPlan.required_monthly_savings)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Projected monthly
                  </p>
                  <p className="text-lg font-semibold text-emerald-200">
                    {formatCurrency(goalFundingPlan.projected_monthly_savings)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">Monthly shortfall</p>
                  <p className="text-lg font-semibold text-amber-200">
                    {formatCurrency(goalFundingPlan.monthly_shortfall)}
                  </p>
                </div>
              </div>
            </div>
          )}

          {recommendedCuts.length > 0 && (
            <div className="rounded-2xl border border-violet-300/20 bg-violet-500/5 p-5 shadow-sm">
              <h4 className="text-base font-semibold text-violet-100">
                Recommended Category Reductions
              </h4>
              <div className="mt-4 space-y-2">
                {recommendedCuts.map((cut) => (
                  <div
                    key={`${cut.category}-${cut.priority}`}
                    className="flex items-center justify-between rounded-xl border border-white/15 px-4 py-3 text-sm"
                  >
                    <p className="capitalize text-slate-200">{cut.category}</p>
                    <p className="font-semibold text-emerald-200">
                      -{formatCurrency(cut.recommended_reduction_amount)} ({cut.recommended_reduction_pct}%)
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {habitChallenges.length > 0 && (
            <div className="rounded-2xl border border-cyan-300/20 bg-cyan-500/5 p-5 shadow-sm">
              <h4 className="text-base font-semibold text-cyan-100">Challenges This Week</h4>
              <ul className="mt-4 space-y-2">
                {habitChallenges.map((challenge, index) => (
                  <li
                    key={`${index}-${challenge}`}
                    className="rounded-xl border border-white/15 px-4 py-3 text-sm text-slate-200"
                  >
                    {challenge}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-2xl border border-slate-300/20 bg-white/[0.03] p-5 shadow-sm transition-colors hover:bg-white/[0.07]">
              <p className="text-sm text-slate-300">Original Spending</p>
              <p className="mt-3 text-2xl font-bold text-white">
                {formatCurrency(simulation.original_total_spent)}
              </p>
            </div>

            <div className="rounded-2xl border border-cyan-300/20 bg-cyan-400/5 p-5 shadow-sm transition-colors hover:bg-cyan-400/10">
              <p className="text-sm text-slate-300">Projected Spending</p>
              <p className="mt-3 text-2xl font-bold text-cyan-100">
                {formatCurrency(simulation.projected_total_spent)}
              </p>
            </div>

            <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/5 p-5 shadow-sm transition-colors hover:bg-emerald-400/10">
              <p className="text-sm text-slate-300">Monthly Savings</p>
              <p className="mt-3 text-2xl font-bold text-emerald-200">
                {formatCurrency(simulation.monthly_savings)}
              </p>
            </div>

            <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/5 p-5 shadow-sm transition-colors hover:bg-emerald-400/10">
              <p className="text-sm text-slate-300">Annual Savings</p>
              <p className="mt-3 text-2xl font-bold text-emerald-200">
                {formatCurrency(simulation.annual_savings)}
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-white/15 bg-white/[0.03] p-5 shadow-sm">
            <h4 className="text-base font-semibold text-white">Projected Category Totals</h4>

            <div className="mt-4 space-y-3">
              {simulation.updated_category_totals.map((item) => {
                const savings = item.original_total - item.projected_total;

                return (
                  <div
                    key={item.category}
                    className="flex items-center justify-between rounded-2xl border border-white/15 px-4 py-4 transition-colors hover:bg-white/[0.08]"
                  >
                    <div className="space-y-1">
                      <p className="capitalize font-medium text-slate-100">{item.category}</p>
                      <p className="text-sm text-slate-300">
                        {formatCurrency(item.original_total)} →{" "}
                        {formatCurrency(item.projected_total)}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-xs uppercase tracking-wide text-slate-400">
                        Savings
                      </p>
                      <p className="font-semibold text-emerald-300">
                        {formatCurrency(savings)}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {aiExplanation && !loading && (
            <div className="rounded-2xl border border-violet-300/20 bg-violet-500/5 p-5 shadow-sm">
              <h4 className="text-base font-semibold text-violet-100">AI Strategy Analysis</h4>
              <div className="prose prose-invert mt-4 max-w-4xl prose-headings:scroll-mt-24 prose-headings:font-semibold prose-headings:tracking-tight prose-h3:mb-3 prose-h3:mt-6 prose-h3:text-lg prose-p:my-4 prose-p:leading-8 prose-p:text-gray-200 prose-strong:font-bold prose-strong:text-white prose-ul:my-4 prose-ul:text-gray-200 prose-li:my-1">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h3: ({ children }) => (
                      <div className="mt-6 rounded-xl border border-violet-300/20 bg-violet-400/10 px-4 py-3">
                        <h3 className="m-0 text-base font-bold text-white">{children}</h3>
                      </div>
                    ),
                    h4: ({ children }) => (
                      <h4 className="mt-5 text-sm font-bold uppercase tracking-wide text-emerald-300">
                        {children}
                      </h4>
                    ),
                    p: ({ children }) => (
                      <p className="my-3 text-sm leading-7 text-gray-200">{children}</p>
                    ),
                    ul: ({ children }) => (
                      <ul className="my-4 list-none space-y-2 pl-0 text-sm leading-7 text-gray-200">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="my-3 list-decimal space-y-1.5 pl-6 text-sm leading-7 text-gray-200">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2">
                        {children}
                      </li>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-bold text-white">{children}</strong>
                    ),
                    hr: () => null,
                    blockquote: ({ children }) => (
                      <blockquote className="my-4 rounded-r-xl border-l-4 border-emerald-400/70 bg-emerald-400/5 px-4 py-3 text-sm text-gray-200">
                        {children}
                      </blockquote>
                    ),
                  }}
                >
                  {toReadableStrategyMarkdown(aiExplanation)}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
