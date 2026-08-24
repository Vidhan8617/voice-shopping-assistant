import type { Product } from "../types";

interface SearchPanelProps {
  query: string | null;
  results: Product[];
  isLoading: boolean;
  onClose: () => void;
  onAddToList: (name: string) => void;
}

/**
 * Shown when the parsed voice intent is "search" — surfaces matching mock
 * catalog products (name/brand/category/price) with a way to add any
 * result straight to the shopping list.
 */
export function SearchPanel({ query, results, isLoading, onClose, onAddToList }: SearchPanelProps) {
  if (query === null) return null;

  return (
    <div className="rounded-lg border border-paper-line bg-white/60 p-4 animate-print-in">
      <div className="flex items-center justify-between mb-3">
        <p className="font-mono text-xs text-ink-soft">
          Results for <span className="text-ink">"{query}"</span>
        </p>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close search results"
          className="text-ink-soft hover:text-ink text-lg leading-none"
        >
          ×
        </button>
      </div>

      {isLoading && (
        <div className="space-y-2 animate-pulse" aria-busy="true">
          <div className="h-8 rounded bg-paper-line/60" />
          <div className="h-8 rounded bg-paper-line/60" />
        </div>
      )}

      {!isLoading && results.length === 0 && (
        <p className="font-body text-sm text-ink-soft py-2">No matching products found.</p>
      )}

      {!isLoading && results.length > 0 && (
        <ul className="space-y-1">
          {results.map((product) => (
            <li
              key={product.id}
              className="flex items-center justify-between gap-3 py-1.5 receipt-divider last:border-b-0"
            >
              <div className="min-w-0">
                <p className="font-body text-sm text-ink truncate">
                  {product.name}
                  {product.brand && <span className="text-ink-soft"> · {product.brand}</span>}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="font-mono text-sm text-forest">${product.price.toFixed(2)}</span>
                <button
                  type="button"
                  onClick={() => onAddToList(product.name)}
                  aria-label={`Add ${product.name} to list`}
                  className="rounded-full bg-forest text-paper h-6 w-6 flex items-center justify-center hover:bg-forest-light transition-colors text-sm leading-none"
                >
                  +
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
