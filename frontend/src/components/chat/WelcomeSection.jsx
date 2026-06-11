import { useAgent } from '../../contexts/AgentContext';
import { motion } from 'framer-motion';

export default function WelcomeSection({ onSuggestionClick }) {
  const { selectedAgentId } = useAgent();

  const getGreeting = () => {
    switch (selectedAgentId) {
      case 'search': return "Find research papers and academic publications.";
      case 'summary': return "Summarize research into key insights.";
      case 'comparison': return "Compare methodologies and findings.";
      case 'gap': return "Discover unexplored research opportunities.";
      case 'review': return "Generate academic literature reviews.";
      default: return "How can I help you with your research today?";
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
      case 'gap': return [
        "Find research gaps",
        "Discover future work",
        "Identify unexplored areas"
      ];
      case 'review': return [
        "Generate literature review",
        "Create survey paper",
        "Review existing research"
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
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <div className="w-16 h-16 mx-auto mb-6 rounded-2xl agent-gradient-bg flex items-center justify-center shadow-lg transition-colors duration-300">
          <span className="text-white text-2xl font-bold">AI</span>
        </div>
        <h2 className="text-2xl md:text-3xl font-semibold text-[var(--text-primary)] mb-3">
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
            className="p-4 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl text-[var(--text-secondary)] text-sm hover:text-[var(--text-primary)] hover:border-[var(--agent-primary)] hover:shadow-md transition-all duration-300 text-left"
          >
            {text}
          </button>
        ))}
      </motion.div>
    </div>
  );
}
