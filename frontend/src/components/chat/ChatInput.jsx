import { useState } from 'react';
import { useAgent } from '../../contexts/AgentContext';
import { Paperclip, ArrowUp } from 'lucide-react';

export default function ChatInput({ onSend }) {
  const [text, setText] = useState('');
  const { selectedAgentId } = useAgent();

  const getPlaceholder = () => {
    switch (selectedAgentId) {
      case 'search': return "Search for research papers...";
      case 'summary': return "Summarize selected papers...";
      case 'comparison': return "Compare research papers...";
      case 'gap': return "Find research gaps...";
      case 'review': return "Generate literature review...";
      default: return "Message Smart Research Assistant...";
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className="relative flex items-end w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden focus-within:border-[var(--agent-primary)] focus-within:ring-1 focus-within:ring-[var(--agent-primary)] transition-all duration-300 shadow-sm"
    >
      <button 
        type="button"
        className="p-3 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        <Paperclip className="w-5 h-5" />
      </button>
      
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
        placeholder={getPlaceholder()}
        className="flex-1 max-h-48 py-3 bg-transparent border-none focus:outline-none resize-none text-[var(--text-primary)] placeholder-[var(--text-secondary)]"
        rows={1}
      />

      <button 
        type="submit"
        disabled={!text.trim()}
        className={`m-2 p-2 rounded-xl transition-all duration-300 flex items-center justify-center
          ${text.trim() 
            ? 'bg-[var(--agent-primary)] text-white hover:opacity-90 cursor-pointer' 
            : 'bg-[var(--bg-sidebar)] text-[var(--text-secondary)] cursor-not-allowed'}`}
      >
        <ArrowUp className="w-5 h-5" />
      </button>
    </form>
  );
}
