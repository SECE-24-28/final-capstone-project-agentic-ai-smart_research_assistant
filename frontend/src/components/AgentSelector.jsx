import { useState, useRef, useEffect } from 'react';
import { useAgent } from '../contexts/AgentContext';
import { ChevronDown, Sparkles, Search, FileText, MessageSquare, GitCompare, Crosshair, BookOpen } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

const iconMap = {
  Sparkles, Search, FileText, MessageSquare, GitCompare, Crosshair, BookOpen
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

  const Icon = iconMap[selectedAgent.icon] || Sparkles;

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-[var(--bg-card)] transition-colors group"
      >
        <span className="font-semibold text-lg text-[var(--text-primary)]">
          Smart Research Assistant
        </span>
        <span className="text-[var(--text-secondary)] text-sm ml-2 px-2 py-0.5 rounded-full border border-[var(--border-color)] group-hover:border-[var(--agent-primary)] transition-colors duration-300">
          {selectedAgent.name}
        </span>
        <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full left-0 mt-2 w-64 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl shadow-xl overflow-hidden z-50"
          >
            <div className="p-1">
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
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-left transition-colors duration-150 ${
                      isActive ? 'bg-[var(--bg-sidebar)] font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)] hover:bg-[var(--bg-sidebar)] hover:text-[var(--text-primary)]'
                    }`}
                  >
                    <AgentIcon className="w-4 h-4" style={{ color: isActive ? 'var(--agent-primary)' : 'currentColor' }} />
                    {agent.name}
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
