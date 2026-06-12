import { useState, useRef, useEffect } from 'react';
import { useAgent } from '../contexts/AgentContext';
import { ChevronDown, Sparkles, Search, FileText, MessageSquare, GitCompare } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

const iconMap = {
  Sparkles, Search, FileText, MessageSquare, GitCompare
};

export default function AgentSelector() {
  const { selectedAgentId, setSelectedAgentId, selectedAgent, AGENTS } = useAgent();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-[var(--bg-card)] transition-colors group"
      >
        <span className="font-semibold text-lg text-[var(--text-primary)] hidden sm:inline">
          Smart Research
        </span>
        <div className="flex items-center gap-2 text-[var(--text-secondary)] text-sm sm:ml-2 px-3 py-1 rounded-full border border-[var(--border-color)] group-hover:border-[var(--agent-primary)] transition-colors duration-300 bg-[var(--bg-card)] shadow-sm">
          {/* Gradient Status Dot */}
          <div className="w-2 h-2 rounded-full agent-gradient-bg agent-glow animate-pulse" />
          <span className="font-medium text-[var(--text-primary)]">{selectedAgent.name}</span>
          <ChevronDown className="w-4 h-4 ml-1 opacity-70" />
        </div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute top-full left-0 mt-2 w-64 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl shadow-xl overflow-hidden z-50 origin-top-left"
          >
            <div className="p-1.5 space-y-0.5">
              {AGENTS.map((agent) => {
                const AgentIcon = iconMap[agent.icon];
                const isActive = agent.id === selectedAgentId;
                return (
                  <button
                    key={agent.id}
                    onClick={() => {
                      setSelectedAgentId(agent.id);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-left transition-all duration-200 border-l-2 ${
                      isActive 
                        ? 'bg-[var(--bg-sidebar)] font-medium agent-left-border shadow-sm' 
                        : 'text-[var(--text-secondary)] hover:bg-[var(--bg-sidebar)] hover:text-[var(--text-primary)] border-transparent'
                    }`}
                  >
                    <AgentIcon 
                      className={`w-4 h-4 transition-colors ${isActive ? 'agent-gradient-text' : ''}`} 
                      style={{ color: isActive ? 'var(--agent-primary)' : 'currentColor' }} 
                    />
                    <span className={isActive ? 'agent-gradient-text' : ''}>{agent.name}</span>
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
