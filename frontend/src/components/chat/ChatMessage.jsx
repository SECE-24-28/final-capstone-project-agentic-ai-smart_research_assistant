import ReactMarkdown from 'react-markdown';
import { useAgent } from '../../contexts/AgentContext';
import PaperCard from '../papers/PaperCard';
import CitationCard from '../papers/CitationCard';

export default function ChatMessage({ message }) {
  const { selectedAgent } = useAgent();
  const isUser = message.role === 'user';
  const isStreaming = message.isStreaming === true;

  if (isUser) {
    return (
      <div className="flex justify-end w-full">
        <div className="max-w-[80%] bg-[var(--bg-card)] border border-[var(--border-color)] px-5 py-3 rounded-3xl rounded-tr-sm text-[var(--text-primary)] shadow-sm">
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
      <div className="flex-1 min-w-0 flex flex-col gap-4">
        {message.content && (
          <div className="text-[var(--text-primary)] markdown-body">
            <ReactMarkdown
              components={{
                a: ({ href, children, ...props }) => {
                  if (href === '#cursor') {
                    return <span className="streaming-cursor"></span>;
                  }
                  return <a href={href} {...props}>{children}</a>;
                }
              }}
            >
              {isStreaming ? `${message.content} [#cursor](#cursor)` : message.content}
            </ReactMarkdown>
          </div>
        )}
        
        {/* Render Papers if returned by Search Agent */}
        {message.papers && message.papers.length > 0 && (
          <div className="grid grid-cols-1 gap-3 mt-2">
            {message.papers.map(paper => (
              <PaperCard key={paper.id} paper={paper} />
            ))}
          </div>
        )}

        {/* Render Citations if returned by Citation Agent */}
        {message.citations && message.citations.length > 0 && (
          <div className="mt-2">
            <CitationCard citations={message.citations} />
          </div>
        )}
      </div>
    </div>
  );
}
