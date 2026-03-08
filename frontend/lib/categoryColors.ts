const BASE_CATEGORY_COLORS: Record<string, string> = {
  groceries: "#38bdf8",
  restaurants: "#34d399",
  subscriptions: "#f59e0b",
  transportation: "#f97316",
  shopping: "#60a5fa",
  payments: "#10b981",
  income: "#a78bfa",
  telecom: "#22d3ee",
  health: "#f472b6",
  other: "#9ca3af",
};

function normalizeCategory(category: string) {
  return category.trim().toLowerCase();
}

export function buildCategoryColorMap(categories: string[]) {
  const map: Record<string, string> = { ...BASE_CATEGORY_COLORS };
  const unknown = categories
    .map(normalizeCategory)
    .filter((category) => category && !map[category]);

  const uniqueUnknown = Array.from(new Set(unknown)).sort();

  uniqueUnknown.forEach((category, index) => {
    const hue = Math.round((index * 137.508 + 18) % 360);
    map[category] = `hsl(${hue} 78% 62%)`;
  });

  return map;
}

export function getCategoryColor(
  colorMap: Record<string, string>,
  category: string,
  fallback = "#94a3b8"
) {
  return colorMap[normalizeCategory(category)] ?? fallback;
}
