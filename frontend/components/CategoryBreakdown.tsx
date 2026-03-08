import { StatementSummary } from "../types/transaction";
import { formatCurrency } from "../lib/format";

type Props = {
  summary: StatementSummary;
};

export default function CategoryBreakdown({ summary }: Props) {
  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <div className="rounded-2xl border border-cyan-300/20 bg-gradient-to-br from-slate-900/85 to-cyan-950/45 p-5 shadow-[0_12px_40px_rgba(6,40,66,0.3)]">
        <h3 className="text-lg font-semibold text-cyan-100">Category Totals</h3>

        {summary.category_totals.length === 0 ? (
          <p className="mt-4 text-sm text-slate-300">No debit spending found.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {summary.category_totals.map((item) => (
              <div
                key={item.category}
                className="flex items-center justify-between rounded-xl border border-white/15 bg-white/[0.03] px-4 py-3 transition-colors hover:bg-white/[0.08]"
              >
                <span className="capitalize text-slate-100">{item.category}</span>
                <span className="font-semibold text-cyan-100">{formatCurrency(item.total)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-emerald-300/20 bg-gradient-to-br from-slate-900/85 to-emerald-950/40 p-5 shadow-[0_12px_40px_rgba(5,45,35,0.32)]">
        <h3 className="text-lg font-semibold text-emerald-100">Top Merchants</h3>

        {summary.top_merchants.length === 0 ? (
          <p className="mt-4 text-sm text-slate-300">No merchants found.</p>
        ) : (
          <div className="mt-4 space-y-3">
            {summary.top_merchants.map((item) => (
              <div
                key={item.merchant}
                className="flex items-center justify-between rounded-xl border border-white/15 bg-white/[0.03] px-4 py-3 transition-colors hover:bg-white/[0.08]"
              >
                <span className="max-w-[70%] truncate text-slate-100">{item.merchant}</span>
                <span className="font-semibold text-emerald-100">{formatCurrency(item.total)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
