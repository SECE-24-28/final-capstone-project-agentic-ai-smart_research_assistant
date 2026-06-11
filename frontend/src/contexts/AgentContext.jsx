import React, { createContext, useContext, useState, useEffect } from 'react';

export const AGENTS = [
  { id: 'auto', name: 'Auto', icon: 'Sparkles', color: '#64748B' },
  { id: 'search', name: 'Search Agent', icon: 'Search', color: '#E11D48' },
  { id: 'summary', name: 'Summary Agent', icon: 'FileText', color: '#14B8A6' },
  { id: 'chat', name: 'Chat Agent', icon: 'MessageSquare', color: '#64748B' },
  { id: 'comparison', name: 'Comparison Agent', icon: 'GitCompare', color: '#6B8E23' },
  { id: 'gap', name: 'Gap Analysis Agent', icon: 'Crosshair', color: '#7C3AED' },
  { id: 'review', name: 'Literature Review Agent', icon: 'BookOpen', color: '#1E3A8A' }
];

const AgentContext = createContext();

export function AgentProvider({ children }) {
  const [selectedAgentId, setSelectedAgentId] = useState('search');

  useEffect(() => {
    document.body.setAttribute('data-agent', selectedAgentId);
  }, [selectedAgentId]);

  const selectedAgent = AGENTS.find(a => a.id === selectedAgentId) || AGENTS[1];

  return (
    <AgentContext.Provider value={{ selectedAgentId, setSelectedAgentId, selectedAgent, AGENTS }}>
      {children}
    </AgentContext.Provider>
  );
}

export const useAgent = () => useContext(AgentContext);
