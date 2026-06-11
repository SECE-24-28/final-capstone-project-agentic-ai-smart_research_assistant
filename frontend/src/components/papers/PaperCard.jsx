import { useState } from 'react';
import { usePaper } from '../../contexts/PaperContext';
import { Check, Plus, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function PaperCard({ paper }) {
  const { selectedPaperIds, addSelectedPaper, removeSelectedPaper } = usePaper();
  const [isExpanded, setIsExpanded] = useState(false);
  
  const isSelected = selectedPaperIds.includes(paper.id);

  const toggleSelection = () => {
    if (isSelected) {
      removeSelectedPaper(paper.id);
    } else {
      addSelectedPaper(paper);
    }
  };

  return (
    <div 
      className={`relative w-full rounded-[13px] transition-all duration-300
        ${isSelected ? 'p-[1px] agent-gradient-bg scale-[1.01]' : 'p-0 bg-transparent'}`}
      style={isSelected ? { boxShadow: '0 0 20px color-mix(in srgb, var(--agent-primary) 15%, transparent)' } : {}}
    >
      <div 
        className={`w-full h-full rounded-xl bg-[var(--bg-card)] transition-all duration-300
          ${!isSelected && 'border border-[var(--border-color)] hover:border-[var(--text-secondary)] shadow-sm'}`}
      >
        <div className="p-4 flex flex-col gap-3">
          {/* Header: Title and Select Button */}
          <div className="flex justify-between items-start gap-4">
            <h4 className="font-medium text-sm text-[var(--text-primary)] leading-snug">
              {paper.title}
            </h4>
            <button
              onClick={toggleSelection}
              className={`shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors text-sm font-medium
                ${isSelected ? 'text-[var(--agent-primary)] bg-[var(--agent-primary)] bg-opacity-10' : 'bg-[var(--bg-sidebar)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--border-color)]'}`}
            >
              {isSelected ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Selected</span>
                </>
              ) : (
                <Plus className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Metadata */}
          <div className="text-xs text-[var(--text-secondary)] flex flex-wrap gap-x-4 gap-y-1">
            {paper.authors && <span>👨‍🔬 {paper.authors.split(',')[0]} et al.</span>}
            {paper.year && <span>📅 {paper.year}</span>}
            {paper.doi && (
              <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-[var(--text-primary)] transition-colors">
                🔗 DOI <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>

          {/* Abstract Toggle */}
          {paper.abstract && (
            <div>
              <button 
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] flex items-center gap-1 transition-colors"
              >
                {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                {isExpanded ? 'Hide Abstract' : 'View Abstract'}
              </button>
              <AnimatePresence>
                {isExpanded && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <p className="mt-2 text-xs text-[var(--text-secondary)] leading-relaxed border-t border-[var(--border-color)] pt-2">
                      {paper.abstract}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
