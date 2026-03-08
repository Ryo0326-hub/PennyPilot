"use client";

import { useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { StatementSummary } from "../types/transaction";
import { formatCurrency } from "../lib/format";
import { buildCategoryColorMap, getCategoryColor } from "../lib/categoryColors";

type Props = {
  summary: StatementSummary;
};

export default function CategoryBarChart({ summary }: Props) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const data = useMemo(() => summary.category_totals, [summary.category_totals]);
  const categoryColorMap = useMemo(
    () => buildCategoryColorMap(data.map((item) => item.category)),
    [data]
  );

  return (
    <div className="rounded-2xl border border-blue-300/20 bg-gradient-to-br from-slate-900/85 to-blue-950/45 p-4 shadow-[0_14px_35px_rgba(8,29,77,0.35)]">
      <h3 className="text-lg font-semibold text-blue-100">Spending by Category</h3>
      <p className="mt-1 text-sm text-slate-300">Debit transactions only.</p>

      <div className="mt-4 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
            <XAxis dataKey="category" stroke="#bfdbfe" />
            <YAxis stroke="#bfdbfe" />
            <Tooltip
              formatter={(value: unknown) => formatCurrency(Number(value))}
              contentStyle={{
                backgroundColor: "#0a1124",
                border: "1px solid rgba(125,211,252,0.35)",
                borderRadius: "12px",
              }}
              labelStyle={{
                color: "#ffffff",
                textTransform: "capitalize",
                fontWeight: 600,
              }}
              itemStyle={{
                color: "#ffffff",
                fontWeight: 500,
              }}
              cursor={{ fill: "rgba(56,189,248,0.12)" }}
            />
            <Bar
              dataKey="total"
              radius={[8, 8, 0, 0]}
              isAnimationActive
              animationDuration={700}
              animationEasing="ease-out"
              onMouseEnter={(_, index: number) => setActiveIndex(index)}
              onMouseLeave={() => setActiveIndex(null)}
            >
              {data.map((entry, index) => {
                const baseColor = getCategoryColor(categoryColorMap, entry.category);
                const isActive = activeIndex === index;

                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={baseColor}
                    fillOpacity={isActive || activeIndex === null ? 1 : 0.45}
                    stroke={isActive ? "#ffffff" : "none"}
                    strokeWidth={isActive ? 2 : 0}
                  />
                );
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
