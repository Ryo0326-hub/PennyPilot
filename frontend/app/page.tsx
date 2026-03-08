"use client";

import { useState } from "react";
import UploadStatementForm from "../components/UploadStatementForm";
import TransactionTable from "../components/TransactionTable";
import SummaryCards from "../components/SummaryCards";
import CategoryBreakdown from "../components/CategoryBreakdown";
import CategoryBarChart from "../components/CategoryBarChart";
import CategoryPieChart from "../components/CategoryPieChart";
import AIInsightsCard from "../components/AIInsightsCard";
import { api } from "../lib/api";
import {
  ParseResponse,
  StatementSummary,
  InsightsResponse,
} from "../types/transaction";
import StrategySimulator from "../components/StrategySimulator";

type SectionHeadingProps = {
  title: string;
  subtitle: string;
  badge?: string;
};

function SectionHeading({ title, subtitle, badge }: SectionHeadingProps) {
  return (
    <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-start">
      <div className="space-y-1">
        <h2 className="text-xl font-bold tracking-tight text-white sm:text-2xl">{title}</h2>
        <p className="text-sm text-slate-300">{subtitle}</p>
      </div>
      {badge ? (
        <span className="rounded-full border border-cyan-300/35 bg-cyan-300/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-cyan-200 sm:mt-0">
          {badge}
        </span>
      ) : null}
    </div>
  );
}

export default function Home() {
  const [parsedData, setParsedData] = useState<ParseResponse | null>(null);
  const [summary, setSummary] = useState<StatementSummary | null>(null);
  const [insights, setInsights] = useState<string | null>(null);
  const [loadingInsights, setLoadingInsights] = useState(false);

  const handleParsed = async (data: ParseResponse) => {
    setParsedData(data);
    setInsights(null);

    try {
      const summaryResponse = await api.get<StatementSummary>(
        `/summary/${data.statement_id}`
      );
      setSummary(summaryResponse.data);
    } catch (error) {
      console.error("Failed to fetch summary:", error);
      setSummary(null);
    }

    try {
      setLoadingInsights(true);
      const insightsResponse = await api.get<InsightsResponse>(
        `/insights/${data.statement_id}`
      );
      setInsights(insightsResponse.data.insights);
    } catch (error) {
      console.error("Failed to fetch insights:", error);
      setInsights("Failed to generate AI insights.");
    } finally {
      setLoadingInsights(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden px-3 py-6 sm:px-6 sm:py-8 lg:px-8">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-24 left-1/3 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute top-1/3 -left-16 h-72 w-72 rounded-full bg-blue-500/15 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 h-80 w-80 rounded-full bg-emerald-500/15 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl space-y-6 sm:space-y-8">
        <header className="rounded-3xl border border-white/15 bg-gradient-to-br from-slate-900/95 via-slate-900/85 to-cyan-950/80 p-5 shadow-[0_20px_70px_rgba(7,12,26,0.45)] sm:p-8">
          <div className="max-w-3xl space-y-3">
            <span className="inline-flex rounded-full border border-cyan-300/35 bg-cyan-300/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-cyan-200 sm:text-xs sm:tracking-[0.2em]">
              Money Coach, Powered by AI
            </span>
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-4xl">
              PennyPilot
            </h1>
            <p className="text-sm leading-7 text-slate-200 sm:text-base">
              Drop your bank statement and see where your money goes and how to save more
            </p>
            <p className="text-xs font-medium tracking-wide text-emerald-300 sm:text-sm">
              Upload your bank statement pdf. We sort your spending, show simple charts, and give
              easy tips you can actually use.
            </p>
          </div>
        </header>

        <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-1 shadow-xl backdrop-blur">
          <UploadStatementForm onParsed={handleParsed} />
        </div>

        {parsedData && (
          <section className="space-y-4">
            <div className="rounded-3xl border border-white/15 bg-gradient-to-r from-slate-900/80 to-slate-800/70 p-5 shadow-lg backdrop-blur sm:p-6">
              <SectionHeading
                title="Uploaded Statement"
                subtitle="Parsed file and ingestion metadata."
                badge="Input"
              />
              <div className="mt-4 grid gap-3 text-sm text-slate-200 md:grid-cols-3">
                <p className="break-all">Filename: {parsedData.filename}</p>
                <p>Statement ID: {parsedData.statement_id}</p>
                <p>Rows parsed: {parsedData.row_count}</p>
              </div>
            </div>
          </section>
        )}

        {summary && (
          <section className="space-y-6">
            <SectionHeading
              title="Dashboard"
              subtitle="Spending metrics and distributions from debit transactions."
              badge="Analytics"
            />

            <SummaryCards summary={summary} />

            <div className="grid gap-6 xl:grid-cols-2">
              <CategoryBarChart summary={summary} />
              <CategoryPieChart summary={summary} />
            </div>

            <CategoryBreakdown summary={summary} />
          </section>
        )}

        {loadingInsights && (
          <section className="space-y-4">
            <div className="animate-pulse space-y-6 rounded-3xl border border-cyan-300/20 bg-gradient-to-br from-slate-900/85 to-cyan-950/60 p-6 shadow-[0_12px_40px_rgba(6,50,77,0.3)]">
              <div className="flex items-center gap-2 text-sm text-cyan-200">
                <div className="h-2 w-2 animate-pulse rounded-full bg-cyan-300"></div>
                AI analyzing your spending patterns...
              </div>

              <div className="space-y-2">
                <div className="h-6 w-40 rounded bg-white/20"></div>
                <div className="h-4 w-64 rounded bg-white/15"></div>
              </div>

              <div className="space-y-3">
                <div className="h-4 w-full rounded bg-white/15"></div>
                <div className="h-4 w-5/6 rounded bg-white/15"></div>
                <div className="h-4 w-4/6 rounded bg-white/15"></div>
              </div>

              <div className="space-y-3">
                <div className="h-5 w-32 rounded bg-white/20"></div>
                <div className="h-4 w-full rounded bg-white/15"></div>
                <div className="h-4 w-5/6 rounded bg-white/15"></div>
              </div>

              <div className="space-y-3">
                <div className="h-5 w-40 rounded bg-white/20"></div>
                <div className="h-4 w-full rounded bg-white/15"></div>
                <div className="h-4 w-4/6 rounded bg-white/15"></div>
              </div>
            </div>
          </section>
        )}

        {!loadingInsights && insights && (
          <section className="space-y-4">
            <AIInsightsCard insights={insights} />
          </section>
        )}

        {parsedData && (
          <section className="space-y-4">
            <StrategySimulator
              statementId={parsedData.statement_id}
              categoryTotals={summary?.category_totals ?? []}
            />
          </section>
        )}

        {parsedData && (
          <section className="space-y-4">
            <SectionHeading
              title="Parsed Transactions"
              subtitle="Normalized records after parsing and categorization."
              badge="Data"
            />

            <TransactionTable transactions={parsedData.transactions} />
          </section>
        )}
      </div>
    </main>
  );
}
