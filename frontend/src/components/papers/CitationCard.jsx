import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

export default function CitationCard({ citations }) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="w-full rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] overflow-hidden shadow-sm">
      <div className="bg-[var(--bg-sidebar)] px-4 py-2 border-b border-[var(--border-color)]">
        <span className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider">Generated Citations</span>
      </div>
      <div className="divide-y divide-[var(--border-color)]">
        {citations.map((cite, index) => (
          <div key={index} className="p-4 flex flex-col gap-2 relative group hover:bg-[var(--bg-sidebar)] transition-colors">
            <div className="flex justify-between items-start">
              <span className="text-xs font-medium agent-gradient-text px-2 py-0.5 rounded bg-[var(--bg-sidebar)] border border-[var(--border-color)]">
                {cite.format || `Format ${index + 1}`}
              </span>
              <button
                onClick={() => handleCopy(cite.text, index)}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--border-color)] rounded-md"
                title="Copy Citation"
              >
                {copiedIndex === index ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-sm text-[var(--text-primary)] font-serif leading-relaxed pr-8">
              {cite.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
