import { Transaction } from "../types/transaction";
import { formatCurrency } from "../lib/format";

type Props = {
  transactions: Transaction[];
};

export default function TransactionTable({ transactions }: Props) {
  if (transactions.length === 0) {
    return (
      <div className="rounded-2xl border border-white/15 bg-slate-900/70 p-4">
        <p className="text-slate-200">No transactions parsed yet.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-white/15 bg-slate-900/75 shadow-[0_14px_35px_rgba(0,0,0,0.35)]">
      <table className="min-w-[760px] text-sm text-slate-100 sm:min-w-full">
        <thead className="border-b border-white/15 bg-gradient-to-r from-slate-800 to-slate-700 text-slate-100">
          <tr>
            <th className="px-3 py-2.5 text-left font-semibold sm:px-4 sm:py-3">Date</th>
            <th className="px-3 py-2.5 text-left font-semibold sm:px-4 sm:py-3">Merchant</th>
            <th className="px-3 py-2.5 text-left font-semibold sm:px-4 sm:py-3">Description</th>
            <th className="px-3 py-2.5 text-left font-semibold sm:px-4 sm:py-3">Amount</th>
            <th className="px-3 py-2.5 text-left font-semibold sm:px-4 sm:py-3">Direction</th>
            <th className="px-3 py-2.5 text-left font-semibold sm:px-4 sm:py-3">Category</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, index) => (
            <tr
              key={`${tx.date}-${tx.description}-${index}`}
              className="border-b border-white/10 transition-colors odd:bg-white/[0.02] hover:bg-cyan-300/10"
            >
              <td className="px-3 py-2.5 text-slate-200 sm:px-4 sm:py-3">{tx.date}</td>
              <td className="px-3 py-2.5 font-medium text-white sm:px-4 sm:py-3">{tx.merchant}</td>
              <td className="px-3 py-2.5 text-slate-200 sm:px-4 sm:py-3">{tx.description}</td>
              <td className="px-3 py-2.5 font-semibold text-cyan-100 sm:px-4 sm:py-3">{formatCurrency(tx.amount)}</td>
              <td className="px-3 py-2.5 text-slate-200 sm:px-4 sm:py-3">{tx.direction}</td>
              <td className="px-3 py-2.5 capitalize text-slate-100 sm:px-4 sm:py-3">{tx.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
