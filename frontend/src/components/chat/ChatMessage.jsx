import ReactMarkdown from 'react-markdown';
import { useAgent } from '../../contexts/AgentContext';

export default function ChatMessage({ message }) {
  const { selectedAgent } = useAgent();
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end w-full">
        <div className="max-w-[80%] bg-[var(--bg-card)] border border-[var(--border-color)] px-5 py-3 rounded-3xl rounded-tr-sm text-[var(--text-primary)]">
          {message.content}
        </div>
      </div>
    );
  }

  // Assistant Message
  return (
    <div className="flex w-full gap-4 items-start">
      <div className="w-8 h-8 shrink-0 rounded-full agent-gradient-bg flex items-center justify-center shadow-sm transition-colors duration-300 mt-1">
        <span className="text-white text-xs font-bold">AI</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[var(--text-primary)] markdown-body">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
