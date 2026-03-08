import { StatementSummary } from "../types/transaction";
import { formatCurrency } from "../lib/format";

type Props = {
  summary: StatementSummary;
};

export default function SummaryCards({ summary }: Props) {
  const cards = [
    {
      label: "💸 Total Spent",
      value: formatCurrency(summary.total_spent),
      classes: "border-cyan-300/25 bg-cyan-400/5 text-cyan-100",
    },
    {
      label: "🧾 Transactions",
      value: String(summary.transaction_count),
      classes: "border-blue-300/25 bg-blue-400/5 text-blue-100",
    },
    {
      label: "📉 Debits",
      value: String(summary.debit_count),
      classes: "border-amber-300/25 bg-amber-400/5 text-amber-100",
    },
    {
      label: "📈 Credits",
      value: String(summary.credit_count),
      classes: "border-emerald-300/25 bg-emerald-400/5 text-emerald-100",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`rounded-2xl border p-5 shadow-[0_12px_35px_rgba(0,0,0,0.3)] transition-all hover:-translate-y-0.5 hover:brightness-110 ${card.classes}`}
        >
          <p className="text-sm font-medium text-slate-300">{card.label}</p>
          <p className="mt-3 text-3xl font-bold tracking-tight text-white">{card.value}</p>
        </div>
      ))}
    </div>
  );
}
