interface LanguageSelectorProps {
  value: string;
  onChange: (lang: string) => void;
}

// BCP-47 codes the Web Speech API expects. Kept short — these are the
// languages the LLM fallback in the backend is prompted to handle well.
const LANGUAGES = [
  { code: "en-US", label: "English" },
  { code: "hi-IN", label: "हिन्दी" },
  { code: "es-ES", label: "Español" },
  { code: "fr-FR", label: "Français" },
];

export function LanguageSelector({ value, onChange }: LanguageSelectorProps) {
  return (
    <label className="inline-flex items-center gap-1.5">
      <span className="sr-only">Voice input language</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="font-mono text-xs bg-transparent text-ink-soft border border-paper-line rounded px-2 py-1
          hover:border-sage focus:border-forest transition-colors cursor-pointer"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
    </label>
  );
}
