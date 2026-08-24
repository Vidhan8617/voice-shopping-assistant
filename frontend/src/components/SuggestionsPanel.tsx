import type { Suggestion } from "../types";

interface SuggestionsPanelProps {
  suggestions: Suggestion[];
  onAdd: (itemName: string) => void;
  isLoading: boolean;
}

const TYPE_LABEL: Record<Suggestion["type"], string> = {
  reorder: "Running low",
  seasonal: "In season",
  substitute: "Alternative",
};

export function SuggestionsPanel({ suggestions, onAdd, isLoading }: SuggestionsPanelProps) {
  if (isLoading) {
    return <div className="h-16 rounded bg-paper-line/60 animate-pulse" aria-busy="true" />;
  }

  if (suggestions.length === 0) return null;

  return (
    <div>
      <p className="font-mono text-[11px] font-medium uppercase tracking-widest text-ink-soft mb-2">
        Suggestions
      </p>
      <ul className="flex flex-wrap gap-2">
        {suggestions.map((s, idx) => (
          <li key={`${s.item_name}-${idx}`}>
            <button
              type="button"
              onClick={() => onAdd(s.item_name)}
              className="group flex items-center gap-1.5 rounded-full border border-sage/50 bg-sage-light
                px-3 py-1.5 text-left transition-colors hover:border-sage hover:bg-sage/20"
              title={s.reason}
            >
              <span className="font-body text-sm text-forest capitalize">{s.item_name}</span>
              <span className="font-mono text-[10px] uppercase tracking-wide text-sage">
                {TYPE_LABEL[s.type]}
              </span>
              <span className="text-forest opacity-0 group-hover:opacity-100 transition-opacity text-sm leading-none">
                +
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
