import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError } from "./api/client";
import { LanguageSelector } from "./components/LanguageSelector";
import { MicButton } from "./components/MicButton";
import { SearchPanel } from "./components/SearchPanel";
import { ShoppingList } from "./components/ShoppingList";
import { SuggestionsPanel } from "./components/SuggestionsPanel";
import { TranscriptBar } from "./components/TranscriptBar";
import { useSpeechRecognition } from "./hooks/useSpeechRecognition";
import type { Product, ShoppingItem, Suggestion } from "./types";

export default function App() {
  const [items, setItems] = useState<ShoppingItem[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isListLoading, setIsListLoading] = useState(true);
  const [isSuggestionsLoading, setIsSuggestionsLoading] = useState(true);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [language, setLanguage] = useState("en-US");
  const [backendReachable, setBackendReachable] = useState(true);

  const [searchQuery, setSearchQuery] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [isSearchLoading, setIsSearchLoading] = useState(false);

  // Ref so the speech recognition callback (created once) always calls the
  // latest handler without needing to be re-created on every render.
  const handleVoiceResultRef = useRef<(transcript: string) => void>(() => {});

  const refreshList = useCallback(async () => {
    try {
      const data = await api.getList();
      setItems(data);
      setBackendReachable(true);
    } catch (err) {
      if (err instanceof ApiError && err.status === 0) setBackendReachable(false);
    } finally {
      setIsListLoading(false);
    }
  }, []);

  const refreshSuggestions = useCallback(async () => {
    try {
      const data = await api.getSuggestions();
      setSuggestions(data);
    } catch {
      // Suggestions are non-critical — fail silently rather than blocking the UI
    } finally {
      setIsSuggestionsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshList();
    refreshSuggestions();
  }, [refreshList, refreshSuggestions]);

  const runSearch = useCallback(async (query: string) => {
    setSearchQuery(query);
    setIsSearchLoading(true);
    try {
      const results = await api.searchProducts(query);
      setSearchResults(results);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearchLoading(false);
    }
  }, []);

  const handleVoiceResult = useCallback(
    async (transcript: string) => {
      try {
        const result = await api.sendVoiceCommand(transcript, language.split("-")[0]);
        setLastMessage(result.message);

        if (result.intent.action === "add" || result.intent.action === "remove") {
          await refreshList();
          await refreshSuggestions();
        }
        if (result.intent.action === "search" && result.intent.item) {
          await runSearch(result.intent.item);
        }
        resetToIdle();
      } catch (err) {
        setLastMessage(
          err instanceof ApiError ? err.message : "Something went wrong processing that command."
        );
      }
    },
    [language, refreshList, refreshSuggestions, runSearch] // eslint-disable-line react-hooks/exhaustive-deps
  );

  handleVoiceResultRef.current = handleVoiceResult;

  const stableOnFinalTranscript = useCallback((transcript: string) => {
    handleVoiceResultRef.current(transcript);
  }, []);

  const { status, interimTranscript, errorMessage, isSupported, startListening, stopListening, resetToIdle } =
    useSpeechRecognition({ language, onFinalTranscript: stableOnFinalTranscript });

  const handleMicClick = () => {
    if (status === "listening") {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleQuickAdd = async (name: string) => {
    try {
      await api.addItem(name);
      setLastMessage(`Added ${name} to your list.`);
      await refreshList();
      await refreshSuggestions();
    } catch (err) {
      setLastMessage(err instanceof ApiError ? err.message : "Couldn't add that item.");
    }
  };

  const handleRemove = async (id: number) => {
    const removed = items.find((i) => i.id === id);
    try {
      await api.removeItem(id);
      if (removed) setLastMessage(`Removed ${removed.name} from your list.`);
      await refreshList();
    } catch (err) {
      setLastMessage(err instanceof ApiError ? err.message : "Couldn't remove that item.");
    }
  };

  return (
    <div className="min-h-screen bg-paper">
      <header className="bg-forest text-paper px-4 py-5">
        <div className="max-w-md mx-auto flex items-center justify-between">
          <div>
            <h1 className="font-display text-xl font-semibold tracking-tight">ListenList</h1>
            <p className="font-mono text-[11px] text-paper/70 mt-0.5">voice shopping assistant</p>
          </div>
          <LanguageSelector value={language} onChange={setLanguage} />
        </div>
      </header>

      <main className="max-w-md mx-auto px-4 pb-16">
        {!backendReachable && (
          <div className="mt-4 rounded-lg bg-rust-light border border-rust/30 px-4 py-3">
            <p className="font-mono text-xs text-rust">
              Can't reach the backend. Make sure the API server is running, then reload this page.
            </p>
          </div>
        )}

        {isSupported === false && (
          <div className="mt-4 rounded-lg bg-mustard/15 border border-mustard/40 px-4 py-3">
            <p className="font-mono text-xs text-mustard-dark">
              Voice input isn't supported in this browser. Try Chrome or Edge, or add items using the list below.
            </p>
          </div>
        )}

        <div className="py-8 flex flex-col items-center gap-4">
          <MicButton status={status} onClick={handleMicClick} disabled={!isSupported} />
          <TranscriptBar
            interimTranscript={interimTranscript}
            lastMessage={lastMessage}
            errorMessage={errorMessage}
          />
        </div>

        {searchQuery !== null && (
          <div className="mb-6">
            <SearchPanel
              query={searchQuery}
              results={searchResults}
              isLoading={isSearchLoading}
              onClose={() => setSearchQuery(null)}
              onAddToList={handleQuickAdd}
            />
          </div>
        )}

        <div className="mb-6">
          <SuggestionsPanel
            suggestions={suggestions}
            onAdd={handleQuickAdd}
            isLoading={isSuggestionsLoading}
          />
        </div>

        {/* The "receipt" — the core list, printed on a paper card */}
        <div className="bg-white/50 rounded-lg border border-paper-line px-4 py-5 shadow-sm">
          <ShoppingList items={items} onRemove={handleRemove} isLoading={isListLoading} />
        </div>
      </main>
    </div>
  );
}
