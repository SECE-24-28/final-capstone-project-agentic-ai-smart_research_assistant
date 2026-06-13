import React, { createContext, useContext, useState, useEffect } from 'react';

export const AGENTS = [
  {
    id: 'auto',
    name: 'Auto Research Mode',
    shortName: 'Auto',
    icon: 'Sparkles',
    color: '#6366F1',
    secondaryColor: '#A855F7',
    description: 'AI automatically plans and executes the full research workflow',
    placeholder: 'Ask anything about a research topic…',
    examples: [
      'Compare recent Edge AI papers',
      'What are the key methodologies in Healthcare AI?',
    ],
  },
  {
    id: 'search',
    name: 'Search Agent',
    shortName: 'Search',
    icon: 'Search',
    color: '#E11D48',
    secondaryColor: '#22C55E',
    description: 'Discover papers on any research topic via OpenAlex',
    placeholder: 'Enter a research topic to search for papers…',
    examples: ['Federated Learning Security', 'Healthcare AI', 'Edge Computing'],
  },
  {
    id: 'summary',
    name: 'Summary Agent',
    shortName: 'Summary',
    icon: 'FileText',
    color: '#14B8A6',
    secondaryColor: '#EC4899',
    description: 'Generate structured summaries of selected papers',
    placeholder: 'Select papers and type "summarize" to begin…',
    examples: ['Summarize all selected papers', 'What are the key findings?'],
  },
  {
    id: 'chat',
    name: 'Chat Agent',
    shortName: 'Chat',
    icon: 'MessageSquare',
    color: '#64748B',
    secondaryColor: '#94A3B8',
    description: 'Ask questions about uploaded paper content',
    placeholder: 'Ask a question about your uploaded papers…',
    examples: ['What methodology was used?', 'Explain the results section'],
  },
  {
    id: 'comparison',
    name: 'Comparison Agent',
    shortName: 'Compare',
    icon: 'GitCompare',
    color: '#6B8E23',
    secondaryColor: '#84CC16',
    description: 'Compare methodologies and findings across papers',
    placeholder: 'Select 2+ papers and ask to compare…',
    examples: ['Compare the methodologies', 'Which paper has better results?'],
  },
];

const AgentContext = createContext();

export function AgentProvider({ children }) {
  const [selectedAgentId, setSelectedAgentId] = useState('auto');
  const [currentSessionId, setCurrentSessionId] = useState(null);

  useEffect(() => {
    document.body.setAttribute('data-agent', selectedAgentId);
    // Set CSS custom properties for secondary color too
    const agent = AGENTS.find(a => a.id === selectedAgentId) || AGENTS[0];
    document.documentElement.style.setProperty('--agent-secondary-color', agent.secondaryColor || agent.color);
  }, [selectedAgentId]);

  const selectedAgent = AGENTS.find(a => a.id === selectedAgentId) || AGENTS[0];

  return (
    <AgentContext.Provider value={{ 
      selectedAgentId, setSelectedAgentId, selectedAgent, AGENTS,
      currentSessionId, setCurrentSessionId
    }}>
      {children}
    </AgentContext.Provider>
  );
}

export const useAgent = () => useContext(AgentContext);
