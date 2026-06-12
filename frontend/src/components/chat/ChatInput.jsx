import { useState } from 'react';
import { useAgent } from '../../contexts/AgentContext';
import { Paperclip, ArrowUp, Square } from 'lucide-react';

export default function ChatInput({ onSend, onStop, isStreaming = false }) {
  const [text, setText] = useState('');
  const { selectedAgentId } = useAgent();

  const getPlaceholder = () => {
    switch (selectedAgentId) {
      case 'search': return "Search for research papers...";
      case 'summary': return "Summarize selected papers...";
      case 'comparison': return "Compare research papers...";

      default: return "Message Smart Research Assistant...";
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || isStreaming) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <div className="agent-gradient-animate agent-glow p-[2px] rounded-[24px] shadow-sm transition-all duration-300">
      <form 
        onSubmit={handleSubmit}
        className="relative flex items-end w-full bg-[var(--bg-card)] rounded-[22px] overflow-hidden"
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
          placeholder={isStreaming ? "Generating response..." : getPlaceholder()}
          disabled={isStreaming}
          className="flex-1 max-h-48 py-3 bg-transparent border-none focus:outline-none resize-none text-[var(--text-primary)] placeholder-[var(--text-secondary)] disabled:opacity-60"
          rows={1}
        />

        {isStreaming ? (
          /* Stop Button */
          <button
            type="button"
            onClick={onStop}
            className="m-2 p-2 rounded-xl transition-all duration-300 flex items-center justify-center
              bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 cursor-pointer shadow-md"
            title="Stop generation"
          >
            <Square className="w-4 h-4 fill-current" />
          </button>
        ) : (
          /* Send Button */
          <button 
            type="submit"
            disabled={!text.trim()}
            className={`m-2 p-2 rounded-xl transition-all duration-200 ease-in-out flex items-center justify-center
              ${text.trim() 
                ? 'bg-[var(--agent-primary)] hover:bg-[var(--agent-secondary)] text-white hover:scale-105 active:scale-95 cursor-pointer shadow-md' 
                : 'bg-[var(--bg-sidebar)] text-[var(--text-secondary)] cursor-not-allowed'}`}
          >
            <ArrowUp className="w-5 h-5" />
          </button>
        )}
      </form>
    </div>
  );
}
