import { motion } from 'framer-motion';
import { useAgent } from '../../contexts/AgentContext';

export default function AIThinking({ message }) {
  const { selectedAgentId } = useAgent();

  const getDynamicMessage = () => {
    if (message) return message;
    switch (selectedAgentId) {
      case 'search': return "Searching papers...";
      case 'summary': return "Generating summary...";
      case 'comparison': return "Comparing methodologies...";
      case 'gap': return "Finding research gaps...";
      case 'review': return "Writing literature review...";
      default: return "AI is thinking...";
    }
  };

  const activeMessage = getDynamicMessage();

  return (
    <div className="flex items-center gap-4 px-2 py-2">
      <div className="flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-2 h-2 rounded-full bg-[var(--agent-primary)] shadow-[0_0_8px_var(--agent-primary)]"
            animate={{ 
              y: ["0%", "-50%", "0%"],
              opacity: [0.3, 1, 0.3],
              scale: [0.8, 1.2, 0.8]
            }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.15
            }}
          />
        ))}
      </div>
      <motion.span 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-sm agent-gradient-text animate-pulse font-medium tracking-wide"
      >
        {activeMessage}
      </motion.span>
    </div>
  );
}
