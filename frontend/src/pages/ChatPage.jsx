import { useState } from 'react';
import TopBar from '../components/layout/TopBar';
import WelcomeSection from '../components/chat/WelcomeSection';
import ChatMessage from '../components/chat/ChatMessage';
import ChatInput from '../components/chat/ChatInput';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = (text) => {
    // Add user message
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);

    // Mock assistant response
    setTimeout(() => {
      setMessages([...newMessages, { 
        role: 'assistant', 
        content: `Here is a mocked response to: **${text}**\n\n- It supports markdown.\n- And lists.\n\n### H3 Heading\nWe will connect this to the backend later.` 
      }]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full relative">
      <TopBar />
      
      <div className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth">
        <div className="max-w-4xl mx-auto flex flex-col gap-6">
          {messages.length === 0 ? (
            <WelcomeSection onSuggestionClick={handleSendMessage} />
          ) : (
            <div className="space-y-6 pb-24">
              {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} />
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[var(--bg-page)] via-[var(--bg-page)] to-transparent">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={handleSendMessage} />
          <div className="text-center text-xs text-[var(--text-secondary)] mt-3">
            Smart Research Assistant can make mistakes. Consider verifying important information.
          </div>
        </div>
      </div>
    </div>
  );
}
