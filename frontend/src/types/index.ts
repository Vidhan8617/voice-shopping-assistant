// Mirrors backend/app/schemas/schemas.py — kept in sync manually since this
// is a small project; a larger one would generate these from the OpenAPI
// schema FastAPI already exposes at /openapi.json.

export interface ShoppingItem {
  id: number;
  name: string;
  quantity: number;
  unit: string | null;
  category: string;
  created_at: string;
}

export type IntentAction = "add" | "remove" | "search" | "unknown";

export interface ParsedIntent {
  action: IntentAction;
  item: string | null;
  quantity: number | null;
  unit: string | null;
  confidence: number;
  source: "rules" | "llm";
}

export interface VoiceCommandResult {
  intent: ParsedIntent;
  item: ShoppingItem | null;
  message: string;
  suggestions: string[];
}

export type SuggestionType = "reorder" | "seasonal" | "substitute";

export interface Suggestion {
  item_name: string;
  reason: string;
  type: SuggestionType;
}

export interface Product {
  id: number;
  name: string;
  brand: string | null;
  category: string;
  price: number;
}
