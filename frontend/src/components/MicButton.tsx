import type { VoiceStatus } from "../hooks/useSpeechRecognition";

interface MicButtonProps {
  status: VoiceStatus;
  onClick: () => void;
  disabled?: boolean;
}

const STATUS_LABEL: Record<VoiceStatus, string> = {
  idle: "Tap to speak",
  listening: "Listening…",
  processing: "Thinking…",
  error: "Tap to try again",
};

export function MicButton({ status, onClick, disabled }: MicButtonProps) {
  const isListening = status === "listening";
  const isProcessing = status === "processing";

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative flex items-center justify-center">
        {isListening && (
          <>
            <span className="absolute h-20 w-20 rounded-full bg-mustard/40 animate-sound-ring" />
            <span
              className="absolute h-20 w-20 rounded-full bg-mustard/40 animate-sound-ring"
              style={{ animationDelay: "0.5s" }}
            />
          </>
        )}
        <button
          type="button"
          onClick={onClick}
          disabled={disabled || isProcessing}
          aria-label={STATUS_LABEL[status]}
          aria-pressed={isListening}
          className={`relative z-10 flex h-20 w-20 items-center justify-center rounded-full
            transition-all duration-200 shadow-lg
            disabled:opacity-50 disabled:cursor-not-allowed
            ${
              isListening
                ? "bg-rust scale-105"
                : status === "error"
                ? "bg-rust/80"
                : "bg-forest hover:bg-forest-light active:scale-95"
            }`}
        >
          {isProcessing ? (
            <svg className="h-8 w-8 animate-spin text-paper" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
            </svg>
          ) : (
            <svg className="h-8 w-8 text-paper" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z"
              />
            </svg>
          )}
        </button>
      </div>
      <span className="font-mono text-xs uppercase tracking-wider text-ink-soft">
        {STATUS_LABEL[status]}
      </span>
    </div>
  );
}
