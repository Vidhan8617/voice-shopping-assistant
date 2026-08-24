interface TranscriptBarProps {
  interimTranscript: string;
  lastMessage: string | null;
  errorMessage: string | null;
}

/**
 * Shows real-time visual feedback of what's being heard and what happened
 * as a result — the assignment explicitly calls for this ("show added
 * items or confirmations"). Printed like a receipt feed: newest line
 * animates in at the top.
 */
export function TranscriptBar({ interimTranscript, lastMessage, errorMessage }: TranscriptBarProps) {
  const hasContent = interimTranscript || lastMessage || errorMessage;

  return (
    <div className="min-h-[3rem] flex items-center justify-center px-4 text-center" aria-live="polite">
      {!hasContent && (
        <p className="font-mono text-sm text-ink-soft">
          Try "add milk" or "I need two bottles of water"
        </p>
      )}
      {interimTranscript && (
        <p className="font-mono text-base text-ink italic animate-print-in">"{interimTranscript}"</p>
      )}
      {!interimTranscript && errorMessage && (
        <p className="font-mono text-sm text-rust animate-print-in">{errorMessage}</p>
      )}
      {!interimTranscript && !errorMessage && lastMessage && (
        <p className="font-mono text-sm text-forest animate-print-in">{lastMessage}</p>
      )}
    </div>
  );
}
