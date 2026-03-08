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
      <table className="min-w-full text-sm text-slate-100">
        <thead className="border-b border-white/15 bg-gradient-to-r from-slate-800 to-slate-700 text-slate-100">
          <tr>
            <th className="px-4 py-3 text-left font-semibold">Date</th>
            <th className="px-4 py-3 text-left font-semibold">Merchant</th>
            <th className="px-4 py-3 text-left font-semibold">Description</th>
            <th className="px-4 py-3 text-left font-semibold">Amount</th>
            <th className="px-4 py-3 text-left font-semibold">Direction</th>
            <th className="px-4 py-3 text-left font-semibold">Category</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, index) => (
            <tr
              key={`${tx.date}-${tx.description}-${index}`}
              className="border-b border-white/10 transition-colors odd:bg-white/[0.02] hover:bg-cyan-300/10"
            >
              <td className="px-4 py-3 text-slate-200">{tx.date}</td>
              <td className="px-4 py-3 font-medium text-white">{tx.merchant}</td>
              <td className="px-4 py-3 text-slate-200">{tx.description}</td>
              <td className="px-4 py-3 font-semibold text-cyan-100">{formatCurrency(tx.amount)}</td>
              <td className="px-4 py-3 text-slate-200">{tx.direction}</td>
              <td className="px-4 py-3 capitalize text-slate-100">{tx.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
