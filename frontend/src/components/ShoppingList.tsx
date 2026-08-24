import type { ShoppingItem } from "../types";

interface ShoppingListProps {
  items: ShoppingItem[];
  onRemove: (id: number) => void;
  isLoading: boolean;
}

function groupByCategory(items: ShoppingItem[]): Map<string, ShoppingItem[]> {
  const groups = new Map<string, ShoppingItem[]>();
  for (const item of items) {
    const existing = groups.get(item.category) ?? [];
    existing.push(item);
    groups.set(item.category, existing);
  }
  return groups;
}

export function ShoppingList({ items, onRemove, isLoading }: ShoppingListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3 animate-pulse" aria-busy="true" aria-label="Loading your list">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-10 rounded bg-paper-line/60" />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="font-display text-lg text-ink-soft">Your list is empty</p>
        <p className="mt-1 font-mono text-xs text-ink-soft">
          Tap the mic and say "add" something to get started
        </p>
      </div>
    );
  }

  const grouped = groupByCategory(items);

  return (
    <div>
      {[...grouped.entries()].map(([category, categoryItems]) => (
        <div key={category} className="mb-4">
          <p className="font-mono text-[11px] font-medium uppercase tracking-widest text-sage px-1 mb-1.5">
            {category}
          </p>
          <ul>
            {categoryItems.map((item) => (
              <li
                key={item.id}
                className="receipt-divider flex items-center justify-between gap-3 py-2.5 px-1 last:border-b-0"
              >
                <div className="flex items-baseline gap-2 min-w-0">
                  <span className="font-mono text-sm text-ink-soft shrink-0">
                    {item.quantity}{item.unit ? ` ${item.unit}` : "×"}
                  </span>
                  <span className="font-body text-[15px] text-ink truncate capitalize">{item.name}</span>
                </div>
                <button
                  type="button"
                  onClick={() => onRemove(item.id)}
                  aria-label={`Remove ${item.name} from list`}
                  className="shrink-0 rounded-full p-1.5 text-ink-soft hover:bg-rust-light hover:text-rust transition-colors"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <p className="font-mono text-xs text-ink-soft text-center pt-2 border-t border-paper-line">
        {items.length} {items.length === 1 ? "item" : "items"} total
      </p>
    </div>
  );
}
