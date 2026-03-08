"use client";

import { useEffect, useState } from "react";
import UploadStatementForm from "../components/UploadStatementForm";
import TransactionTable from "../components/TransactionTable";
import SummaryCards from "../components/SummaryCards";
import CategoryBarChart from "../components/CategoryBarChart";
import CategoryPieChart from "../components/CategoryPieChart";
import AIInsightsCard from "../components/AIInsightsCard";
import { api, setAuthTokenProvider, setAuthUserIdProvider } from "../lib/api";
import {
  ParseResponse,
  StatementSummary,
  InsightsResponse,
} from "../types/transaction";
import StrategySimulator from "../components/StrategySimulator";

type Auth0User = {
  sub?: string;
  email?: string;
  name?: string;
};

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
  const [authLoading, setAuthLoading] = useState(true);
  const [user, setUser] = useState<Auth0User | null>(null);
  const [parsedData, setParsedData] = useState<ParseResponse | null>(null);
  const [summary, setSummary] = useState<StatementSummary | null>(null);
  const [insights, setInsights] = useState<string | null>(null);
  const [loadingInsights, setLoadingInsights] = useState(false);

  useEffect(() => {
    const resolveUser = async () => {
      try {
        const response = await fetch("/auth/profile", { credentials: "include" });
        if (!response.ok) {
          setUser(null);
          return;
        }
        const profile = (await response.json()) as Auth0User;
        setUser(profile);
      } catch {
        setUser(null);
      } finally {
        setAuthLoading(false);
      }
    };

    resolveUser();

    setAuthTokenProvider(async () => {
      try {
        const response = await fetch("/auth/access-token", { credentials: "include" });
        if (!response.ok) {
          return null;
        }
        const payload = (await response.json()) as { token?: string; accessToken?: string };
        return payload.token ?? payload.accessToken ?? null;
      } catch {
        return null;
      }
    });
    setAuthUserIdProvider(() => user?.sub ?? null);
    return () => {
      setAuthTokenProvider(null);
      setAuthUserIdProvider(null);
    };
  }, [user?.sub]);

  const handleParsed = async (data: ParseResponse) => {
    if (!user) {
      setSummary(null);
      setInsights("Please sign in to view statement data.");
      return;
    }

    setParsedData(data);
    setInsights(null);

    try {
      const summaryResponse = await api.get<StatementSummary>(
        `/summary/${data.statement_id}`
      );
      setSummary(summaryResponse.data);
    } catch (error) {
      console.error("Failed to fetch summary:", error);
      if (typeof error === "object" && error !== null && "response" in error) {
        const status = (error as { response?: { status?: number } }).response?.status;
        if (status === 401 || status === 403) {
          setInsights("Your session expired. Please sign in again.");
        }
      }
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
      if (typeof error === "object" && error !== null && "response" in error) {
        const status = (error as { response?: { status?: number } }).response?.status;
        if (status === 401 || status === 403) {
          setInsights("Your session expired. Please sign in again.");
        } else {
          setInsights("Failed to generate AI insights.");
        }
      } else {
        setInsights("Failed to generate AI insights.");
      }
    } finally {
      setLoadingInsights(false);
    }
  };

  if (authLoading) {
    return (
      <main className="min-h-screen px-3 py-6 text-slate-200 sm:px-6 sm:py-8 lg:px-8">
        Loading...
      </main>
    );
  }

  return (
    <main className="relative min-h-screen overflow-hidden px-3 py-6 sm:px-6 sm:py-8 lg:px-8">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-24 left-1/3 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute top-1/3 -left-16 h-72 w-72 rounded-full bg-blue-500/15 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 h-80 w-80 rounded-full bg-emerald-500/15 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl space-y-6 sm:space-y-8">
        <header className="rounded-3xl border border-white/15 bg-gradient-to-br from-slate-900/95 via-slate-900/85 to-cyan-950/80 p-5 shadow-[0_20px_70px_rgba(7,12,26,0.45)] sm:p-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
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

            {user ? (
              <div className="space-y-2 text-sm">
                <p className="text-slate-200">Signed in as {user.email ?? user.name ?? "user"}</p>
                <a
                  href="/auth/logout"
                  className="inline-flex rounded-lg border border-white/20 px-3 py-2 text-cyan-100 hover:bg-white/10"
                >
                  Log out
                </a>
              </div>
            ) : (
              <div className="space-y-2 text-sm">
                <a
                  href="/auth/login?screen_hint=signup"
                  className="inline-flex rounded-lg border border-white/20 px-3 py-2 text-cyan-100 hover:bg-white/10"
                >
                  Signup
                </a>
                <a
                  href="/auth/login"
                  className="ml-2 inline-flex rounded-lg bg-cyan-300 px-3 py-2 font-semibold text-slate-900 hover:brightness-105"
                >
                  Login
                </a>
              </div>
            )}
          </div>
        </header>

        {user ? (
          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-1 shadow-xl backdrop-blur">
            <UploadStatementForm onParsed={handleParsed} />
          </div>
        ) : (
          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6 text-center shadow-xl backdrop-blur">
            <p className="text-sm text-slate-200">
              Sign in to upload statements and view private financial insights.
            </p>
            <div className="mt-4">
              <a
                href="/auth/login"
                className="rounded-xl bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-900 hover:brightness-105"
              >
                Sign In
              </a>
            </div>
          </div>
        )}

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
