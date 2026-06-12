import { useAgent } from '../../contexts/AgentContext';
import { motion } from 'framer-motion';

export default function WelcomeSection({ onSuggestionClick }) {
  const { selectedAgentId } = useAgent();

  const getGreeting = () => {
    switch (selectedAgentId) {
      case 'search': return (
        <>Find <span className="agent-gradient-text">Research Papers</span> and Academic Publications</>
      );
      case 'summary': return (
        <>Summarize Research into <span className="agent-gradient-text">Key Insights</span></>
      );
      case 'comparison': return (
        <>Compare <span className="agent-gradient-text">Methodologies and Findings</span></>
      );

      default: return (
        <>How can I help with your <span className="agent-gradient-text">Research</span> today?</>
      );
    }
  };

  const getSuggestions = () => {
    switch (selectedAgentId) {
      case 'search': return [
        "Find papers on Federated Learning",
        "Search AI in Healthcare",
        "Discover recent Edge AI papers"
      ];
      case 'summary': return [
        "Summarize selected papers",
        "Extract methodologies",
        "Extract findings"
      ];
      case 'comparison': return [
        "Compare papers",
        "Compare methodologies",
        "Compare results"
      ];

      default: return [
        "Help me brainstorm a topic",
        "Explain federated learning",
        "How do I write a good abstract?"
      ];
    }
  };

  const suggestions = getSuggestions();

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center px-4 relative z-10">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8 relative"
      >

        <div className="w-16 h-16 mx-auto mb-6 rounded-2xl agent-gradient-bg flex items-center justify-center shadow-lg transition-colors duration-300 relative z-10">
          <span className="text-white text-2xl font-bold">AI</span>
        </div>
        
        <h2 className="text-3xl md:text-4xl font-semibold text-[var(--text-primary)] mb-3 tracking-tight">
          {getGreeting()}
        </h2>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-3xl"
      >
        {suggestions.map((text, i) => (
          <button
            key={i}
            onClick={() => onSuggestionClick(text)}
            className="p-4 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl text-[var(--text-secondary)] text-sm font-medium transition-all duration-200 text-left hover:-translate-y-[3px] hover:shadow-md hover:border-[var(--agent-primary)] hover:text-[var(--text-primary)]"
          >
            {text}
          </button>
        ))}
      </motion.div>
    </div>
  );
}
