"use client";

import { useMemo, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { StatementSummary } from "../types/transaction";
import { formatCurrency } from "../lib/format";
import { buildCategoryColorMap, getCategoryColor } from "../lib/categoryColors";

type Props = {
  summary: StatementSummary;
};

export default function CategoryPieChart({ summary }: Props) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const data = useMemo(() => summary.category_totals, [summary.category_totals]);
  const total = useMemo(
    () => data.reduce((acc, item) => acc + item.total, 0),
    [data]
  );
  const categoryColorMap = useMemo(
    () => buildCategoryColorMap(data.map((item) => item.category)),
    [data]
  );

  return (
    <div className="rounded-2xl border border-violet-300/20 bg-gradient-to-br from-slate-900/85 to-violet-950/45 p-4 shadow-[0_14px_35px_rgba(46,25,93,0.34)]">
      <h3 className="text-lg font-semibold text-violet-100">Category Share</h3>
      <p className="mt-1 text-sm text-slate-300">
        How your spending is distributed across categories.
      </p>

      <div className="mt-4 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="total"
              nameKey="category"
              cx="50%"
              cy="50%"
              outerRadius={102}
              innerRadius={36}
              label={false}
              minAngle={2}
              paddingAngle={1}
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
                    stroke={isActive ? "#ffffff" : "#0b1324"}
                    strokeWidth={isActive ? 3 : 1}
                  />
                );
              })}
            </Pie>
            <Tooltip
              formatter={(value: unknown) => formatCurrency(Number(value))}
              contentStyle={{
                backgroundColor: "#120c29",
                border: "1px solid rgba(196,181,253,0.4)",
                borderRadius: "12px",
                color: "#ffffff",
              }}
              labelStyle={{ color: "#ffffff", textTransform: "capitalize" }}
            />
            <Legend
              wrapperStyle={{ color: "#ddd6fe" }}
              formatter={(value) => {
                const matched = data.find((item) => item.category === value);
                const pct = matched && total > 0 ? (matched.total / total) * 100 : 0;
                return `${value} (${pct.toFixed(1)}%)`;
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
