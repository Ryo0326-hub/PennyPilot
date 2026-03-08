import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  insights: string;
};

type InsightSection = {
  title: string;
  body: string;
};

const SECTION_STYLES: Record<
  string,
  { container: string; heading: string; badge: string }
> = {
  "spending overview": {
    container: "border-cyan-400/30 bg-cyan-400/5",
    heading: "text-cyan-200",
    badge: "border-cyan-300/40 bg-cyan-300/10 text-cyan-200",
  },
  "key patterns": {
    container: "border-amber-400/30 bg-amber-400/5",
    heading: "text-amber-200",
    badge: "border-amber-300/40 bg-amber-300/10 text-amber-200",
  },
  suggestions: {
    container: "border-emerald-400/30 bg-emerald-400/5",
    heading: "text-emerald-200",
    badge: "border-emerald-300/40 bg-emerald-300/10 text-emerald-200",
  },
};

function normalizeTitle(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9 ]/g, "").trim();
}

function parseSections(markdown: string): InsightSection[] {
  const lines = markdown.split(/\r?\n/);
  const sections: InsightSection[] = [];

  let currentTitle = "";
  let currentBody: string[] = [];

  const pushCurrent = () => {
    if (!currentTitle) return;
    sections.push({
      title: currentTitle,
      body: currentBody.join("\n").trim(),
    });
  };

  for (const line of lines) {
    const match = line.match(/^###\s+(.+)$/);
    if (match) {
      pushCurrent();
      currentTitle = match[1].trim();
      currentBody = [];
      continue;
    }
    currentBody.push(line);
  }

  pushCurrent();

  return sections.filter((section) => section.body.length > 0);
}

export default function AIInsightsCard({ insights }: Props) {
  const sections = parseSections(insights);

  return (
    <div className="overflow-hidden rounded-3xl border border-cyan-300/20 bg-gradient-to-br from-slate-900/90 via-slate-900/80 to-cyan-950/60 shadow-[0_16px_48px_rgba(6,26,50,0.35)]">
      <div className="border-b border-white/15 bg-white/[0.03] px-6 py-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-xl font-semibold tracking-tight text-white">
              AI CFO Insights
            </h3>
            <p className="mt-1 text-sm text-slate-300">
              Gemini-generated interpretation of your spending patterns.
            </p>
          </div>

          <div className="rounded-full border border-emerald-300/40 bg-emerald-300/10 px-3 py-1 text-xs font-semibold text-emerald-200">
            AI Analysis
          </div>
        </div>
      </div>

      <div className="px-6 py-6">
        {sections.length > 0 ? (
          <div className="space-y-5">
            {sections.map((section) => {
              const style = SECTION_STYLES[normalizeTitle(section.title)] ?? {
                container: "border-white/10 bg-white/[0.03]",
                heading: "text-white",
                badge: "border-white/20 bg-white/10 text-gray-200",
              };

              return (
                <section
                  key={section.title}
                  className={`rounded-2xl border px-5 py-4 ${style.container}`}
                >
                  <div className="mb-3">
                    <h4 className={`text-base font-bold ${style.heading}`}>
                      {section.title}
                    </h4>
                  </div>

                  <div className="prose prose-invert max-w-none prose-p:my-3 prose-p:text-[15px] prose-p:leading-7 prose-p:text-gray-200 prose-ul:my-3 prose-ul:text-[15px] prose-ul:leading-7 prose-ul:text-gray-200 prose-ol:my-3 prose-ol:text-[15px] prose-ol:leading-7 prose-ol:text-gray-200 prose-li:my-1 prose-strong:font-bold prose-strong:text-white prose-hr:border-white/15">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{ hr: () => null }}
                    >
                      {section.body}
                    </ReactMarkdown>
                  </div>
                </section>
              );
            })}
          </div>
        ) : (
          <div className="prose prose-invert max-w-none prose-headings:scroll-mt-24 prose-headings:font-semibold prose-headings:tracking-tight prose-h3:mb-3 prose-h3:mt-8 prose-h3:text-xl prose-p:leading-7 prose-p:text-gray-200 prose-strong:font-bold prose-strong:text-white prose-ul:my-4 prose-ul:text-gray-200 prose-li:my-1 prose-hr:border-white/10">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{ hr: () => null }}
            >
              {insights}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
