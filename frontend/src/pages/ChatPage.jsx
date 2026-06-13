import { useState, useRef, useEffect, useCallback } from 'react';
import TopBar from '../components/layout/TopBar';
import WelcomeSection from '../components/chat/WelcomeSection';
import ChatMessage from '../components/chat/ChatMessage';
import ChatInput from '../components/chat/ChatInput';
import AIThinking from '../components/chat/AIThinking';
import TaskProgress from '../components/chat/TaskProgress';
import AutoWorkflowProgress from '../components/chat/AutoWorkflowProgress';

import { useAgent } from '../contexts/AgentContext';
import { usePaper } from '../contexts/PaperContext';

import { searchApi } from '../services/searchApi';
import { summaryApi } from '../services/summaryApi';
import { comparisonApi } from '../services/comparisonApi';

import { chatApi } from '../services/chatApi';
import { citationApi } from '../services/citationApi';
import { streamChat } from '../services/streamApi';
import api from '../services/api';
import { getSummaryResult, getCompareResult } from '../services/taskApi';
import { startAutoResearch, getAutoResult } from '../services/autoApi';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [activeTask, setActiveTask] = useState(null);       // non-auto tasks
  const [autoTask, setAutoTask] = useState(null);           // auto coordinator task
  const [autoWorkflowSteps, setAutoWorkflowSteps] = useState([]); // live step statuses
  const messagesEndRef = useRef(null);
  const abortControllerRef = useRef(null);
  const autoPollerRef = useRef(null);

  const { selectedAgentId } = useAgent();
  const { selectedPaperIds, setSearchResults, addSelectedPaper, removeSelectedPaper } = usePaper();
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // ─── Stop Streaming ───────────────────────────────────────────────────────
  const handleStop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setIsLoading(false);
    // Mark last message as done streaming
    setMessages(prev => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1] = { ...updated[updated.length - 1], isStreaming: false };
      }
      return updated;
    });
  }, []);

  // ─── Phase 20: Persistent Chat History ────────────────────────────────────
  const { currentSessionId, setCurrentSessionId } = useAgent();

  const loadSessionHistory = useCallback(async (sessionId) => {
    setIsLoading(true);
    try {
      const session = await chatApi.getSession(sessionId);
      if (session && session.messages) {
        setMessages(session.messages.map(m => ({
          role: m.role,
          content: m.content,
          agent_type: m.agent_type
        })));
      }
    } catch (err) {
      console.error("Failed to load session history:", err);
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (currentSessionId) {
      loadSessionHistory(currentSessionId);
    } else {
      setMessages([]);
    }
  }, [currentSessionId, loadSessionHistory]);

  const currentStreamTextRef = useRef("");

  // ─── Streaming helper ─────────────────────────────────────────────────────
  const startStream = useCallback((streamFn, args, newMessages, thinkingMsg, sessionId) => {
    setLoadingMessage(thinkingMsg);
    setIsLoading(true);

    const streamingMsgIndex = newMessages.length;
    const placeholder = { role: 'assistant', content: '', isStreaming: true };
    const withPlaceholder = [...newMessages, placeholder];
    setMessages(withPlaceholder);
    setIsLoading(false);
    setIsStreaming(true);
    currentStreamTextRef.current = "";

    const startTime = Date.now();
    let firstToken = true;

    const controller = streamFn(...args, {
      onToken: (token) => {
        if (firstToken) {
          const ttft = ((Date.now() - startTime) / 1000).toFixed(2);
          console.log(`[STREAMING] First token in ${ttft}s`);
          firstToken = false;
        }
        currentStreamTextRef.current += token;
        setMessages(prev => {
          const updated = [...prev];
          updated[streamingMsgIndex] = {
            ...updated[streamingMsgIndex],
            content: currentStreamTextRef.current,
            isStreaming: true,
          };
          return updated;
        });
      },
      onDone: async () => {
        const totalTime = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`[STREAMING] Complete in ${totalTime}s`);
        setIsStreaming(false);
        abortControllerRef.current = null;
        
        // Save the final assistant message to the backend
        try {
          if (sessionId) {
            await chatApi.createMessage(sessionId, 'assistant', currentStreamTextRef.current, selectedAgentId);
          }
        } catch (err) {
          console.error("Failed to save assistant message:", err);
        }

        setMessages(prev => {
          const updated = [...prev];
          updated[streamingMsgIndex] = { ...updated[streamingMsgIndex], isStreaming: false };
          return updated;
        });
      },
      onError: (errorMsg) => {
        setIsStreaming(false);
        setIsLoading(false);
        abortControllerRef.current = null;
        setMessages(prev => {
          const updated = [...prev];
          updated[streamingMsgIndex] = {
            ...updated[streamingMsgIndex],
            content: `❌ Streaming error: ${errorMsg}`,
            isStreaming: false,
          };
          return updated;
        });
      },
    });

    abortControllerRef.current = controller;
  }, [selectedAgentId]);

  // ─── Main send handler ────────────────────────────────────────────────────
  const handleSendMessage = async (text) => {
    if (isStreaming) return;

    let activeSessionId = currentSessionId;
    
    // Create new session if none exists
    if (!activeSessionId) {
      try {
        const titleWords = text.split(" ").slice(0, 5).join(" ");
        const newTitle = titleWords + (text.split(" ").length > 5 ? "..." : "");
        const session = await chatApi.createSession(newTitle);
        activeSessionId = session.id;
        setCurrentSessionId(activeSessionId);
      } catch (err) {
        console.error("Failed to create session:", err);
        return; // Halt if DB fails
      }
    }

    // Save user message
    try {
      await chatApi.createMessage(activeSessionId, 'user', text, selectedAgentId);
    } catch (err) {
      console.error("Failed to save user message:", err);
    }

    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      let assistantMsg = { role: 'assistant', content: '' };

      // ── Citation slash command (no streaming needed – fast rule-based) ──
      if (text.trim().toLowerCase() === '/cite') {
        if (selectedPaperIds.length === 0) {
          assistantMsg.content = "⚠️ Please select a paper first to generate citations.";
        } else {
          setLoadingMessage("Generating citations...");
          const apa = await citationApi.generateCitation(selectedPaperIds[0], 'apa');
          const ieee = await citationApi.generateCitation(selectedPaperIds[0], 'ieee');
          const mla = await citationApi.generateCitation(selectedPaperIds[0], 'mla');
          assistantMsg.content = "Here are the formatted citations for your selected paper:\n\n**APA**: " + apa.citation_text + "\n\n**IEEE**: " + ieee.citation_text + "\n\n**MLA**: " + mla.citation_text;
          
          await chatApi.createMessage(activeSessionId, 'assistant', assistantMsg.content, 'citation');
        }
        setMessages([...newMessages, assistantMsg]);
        setIsLoading(false);
        return;
      }

      // ── Search (no LLM – no streaming needed) ──
      if (selectedAgentId === 'search' || selectedAgentId === 'auto' && selectedPaperIds.length === 0) {
        setLoadingMessage("Searching research papers...");
        const searchData = await searchApi.searchPapers(text, 5);
        assistantMsg.content = `I found some relevant papers for **"${text}"**. Select the ones you want to analyze:\n\n` + searchData.map(p => `- ${p.title}`).join('\n');
        assistantMsg.papers = searchData;
        setSearchResults(searchData);
        setMessages([...newMessages, assistantMsg]);
        await chatApi.createMessage(activeSessionId, 'assistant', assistantMsg.content, 'search');
        setIsLoading(false);
        return;
      }

      // ── LLM Agents ─────────────────────────────────────────────────────

      switch (selectedAgentId) {
        // ── Summary: task-tracked ──
        case 'summary': {
          if (selectedPaperIds.length === 0) {
            assistantMsg.content = "⚠️ Please select at least one paper from the search results to summarize.";
            setMessages([...newMessages, assistantMsg]);
            await chatApi.createMessage(activeSessionId, 'assistant', assistantMsg.content, 'summary');
            setIsLoading(false);
            return;
          }
          setIsLoading(false);
          const sumRes = await api.post(`/agent/summary?paper_id=${selectedPaperIds[0]}`);
          setActiveTask({ taskId: sumRes.data.task_id, taskType: 'summary', pendingMessages: newMessages, sessionId: activeSessionId });
          return;
        }

        // ── Comparison: task-tracked ──
        case 'comparison': {
          if (selectedPaperIds.length < 2) {
            assistantMsg.content = "⚠️ Please select at least two papers to run a comparative analysis.";
            setMessages([...newMessages, assistantMsg]);
            await chatApi.createMessage(activeSessionId, 'assistant', assistantMsg.content, 'comparison');
            setIsLoading(false);
            return;
          }
          setIsLoading(false);
          const cmpRes = await api.post('/agent/compare', { paper_ids: selectedPaperIds });
          setActiveTask({ taskId: cmpRes.data.task_id, taskType: 'comparison', pendingMessages: newMessages, sessionId: activeSessionId });
          return;
        }

        // ── Chat: streaming ──
        case 'chat':
        case 'auto':
        default:
          startStream(
            streamChat,
            [text, selectedPaperIds.length > 0 ? selectedPaperIds : null],
            newMessages,
            "Analyzing research context...",
            activeSessionId
          );
          return;
      }

    } catch (error) {
      console.error("Agent API Error:", error);
      let errorMsg = "❌ Error connecting to the Smart Research Assistant backend.";
      if (error.response?.data?.detail) {
        errorMsg += `\n\n**Details:** ${error.response.data.detail}`;
      }
      setMessages([...newMessages, { role: 'assistant', content: errorMsg }]);
      await chatApi.createMessage(activeSessionId, 'assistant', errorMsg, selectedAgentId);
      setIsLoading(false);
    }
  };

  // ── Handle task completion ─────────────────────────────────────────────────
  const handleTaskComplete = useCallback(async (taskStatus) => {
    if (!activeTask) return;
    const { taskId, taskType, pendingMessages, sessionId } = activeTask;
    setActiveTask(null);

    try {
      let result;
      let assistantContent = '';

      if (taskType === 'summary') {
        result = await getSummaryResult(taskId);
        assistantContent = [
          result.objective && `## Objective\n${result.objective}`,
          result.methodology && `## Methodology\n${result.methodology}`,
          result.findings && `## Key Findings\n${result.findings}`,
          result.limitations && `## Limitations\n${result.limitations}`,
          result.contributions && `## Contributions\n${result.contributions}`,
        ].filter(Boolean).join('\n\n');
      } else if (taskType === 'comparison') {
        result = await getCompareResult(taskId);
        assistantContent = result.result || 'Comparison complete.';
      }

      setMessages([...pendingMessages, { role: 'assistant', content: assistantContent }]);
      if (sessionId) {
        await chatApi.createMessage(sessionId, 'assistant', assistantContent, taskType);
      }
    } catch (err) {
      setMessages([...pendingMessages, { role: 'assistant', content: `❌ Failed to retrieve result: ${err.message}` }]);
    }
  }, [activeTask]);

  const handleTaskError = useCallback((errorMsg) => {
    if (!activeTask) return;
    setMessages(prev => [
      ...prev,
      { role: 'assistant', content: `❌ Task failed: ${errorMsg}` }
    ]);
    setActiveTask(null);
  }, [activeTask]);

  // ── Auto Mode: poll task + workflow steps ───────────────────────────────────
  useEffect(() => {
    if (!autoTask) {
      clearInterval(autoPollerRef.current);
      return;
    }
    const { taskId, pendingMessages } = autoTask;

    const poll = async () => {
      try {
        const res = await fetch(`http://localhost:8000/agent/task/${taskId}`);
        if (!res.ok) return;
        const data = await res.json();

        // Update step statuses if result contains them (from task_service result dict)
        if (data.status === 'done') {
          clearInterval(autoPollerRef.current);
          try {
            const fullResult = await getAutoResult(taskId);
            setAutoTask(null);
            setAutoWorkflowSteps([]);

            // Render result based on result_type
            let autoContent = '';
            let papersResult = null;
            if (fullResult.result_type === 'papers' && fullResult.papers?.length > 0) {
              autoContent = `I found **${fullResult.papers.length} papers** on *${fullResult.topic}*. Select papers to analyze further.`;
              papersResult = fullResult.papers;
              setMessages([
                ...pendingMessages,
                {
                  role: 'assistant',
                  content: autoContent,
                  papers: papersResult,
                }
              ]);
            } else {
              autoContent = fullResult.final_text || 'Research complete.';
              setMessages([
                ...pendingMessages,
                { role: 'assistant', content: autoContent }
              ]);
            }
            if (currentSessionId) {
              await chatApi.createMessage(currentSessionId, 'assistant', autoContent, 'auto');
            }
          } catch (err) {
            setAutoTask(null);
            setMessages([...pendingMessages, { role: 'assistant', content: `❌ Failed to retrieve auto result: ${err.message}` }]);
          }
        } else if (data.status === 'failed') {
          clearInterval(autoPollerRef.current);
          setAutoTask(null);
          setMessages([...pendingMessages, { role: 'assistant', content: `❌ Auto pipeline failed: ${data.error || 'Unknown error'}` }]);
        }
      } catch (_) {}
    };

    poll();
    autoPollerRef.current = setInterval(poll, 2000);
    return () => clearInterval(autoPollerRef.current);
  }, [autoTask]);

  return (
    <div className="flex flex-col h-full relative">
      <TopBar />

      <div className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth">
        <div className="max-w-4xl mx-auto flex flex-col gap-6">
          {messages.length === 0 && !activeTask && !autoTask ? (
            <WelcomeSection onSuggestionClick={handleSendMessage} />
          ) : (
            <div className="space-y-6 pb-24">
              {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} />
              ))}

              {/* ─ Auto Mode Workflow Progress ─ */}
              {autoTask && (
                <div className="flex w-full gap-4 items-start">
                  <div className="w-8 h-8 shrink-0 rounded-full agent-gradient-bg flex items-center justify-center shadow-sm mt-1">
                    <span className="text-white text-xs font-bold">AI</span>
                  </div>
                  <div className="flex-1 bg-[var(--bg-card)] border border-[var(--border-color)] px-5 py-5 rounded-2xl rounded-tl-sm shadow-sm">
                    <AutoWorkflowProgress
                      workflow={autoTask.workflow}
                      intent={autoTask.intent}
                      topic={autoTask.topic}
                      steps={autoWorkflowSteps.length > 0 ? autoWorkflowSteps : (
                        // Render skeleton steps while waiting for first poll
                        Array.from({ length: autoTask.estimatedSteps }, (_, i) => ({
                          step_number: i + 1,
                          agent_name: ['Search Agent', 'Summary Agent', 'Comparison Agent'][i] || `Step ${i+1}`,
                          description: 'Waiting to start…',
                          status: i === 0 ? 'running' : 'pending',
                        }))
                      )}
                      taskProgress={null}
                    />
                  </div>
                </div>
              )}

              {/* ─ Regular agent task progress ─ */}
              {activeTask && (
                <div className="flex w-full gap-4 items-start">
                  <div className="w-8 h-8 shrink-0 rounded-full agent-gradient-bg flex items-center justify-center shadow-sm mt-1">
                    <span className="text-white text-xs font-bold">AI</span>
                  </div>
                  <div className="flex-1 bg-[var(--bg-card)] border border-[var(--border-color)] px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm">
                    <TaskProgress
                      taskId={activeTask.taskId}
                      taskType={activeTask.taskType}
                      onComplete={handleTaskComplete}
                      onError={handleTaskError}
                    />
                  </div>
                </div>
              )}

              {/* Simple spinner for search/citation */}
              {isLoading && !isStreaming && !activeTask && !autoTask && (
                <div className="flex w-full gap-4 items-start">
                  <div className="w-8 h-8 shrink-0 rounded-full agent-gradient-bg flex items-center justify-center shadow-sm mt-1">
                    <span className="text-white text-xs font-bold">AI</span>
                  </div>
                  <div className="bg-[var(--bg-card)] border border-[var(--border-color)] px-4 py-2 rounded-3xl rounded-tl-sm shadow-sm">
                    <AIThinking message={loadingMessage} />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[var(--bg-page)] via-[var(--bg-page)] to-transparent">
        <div className="max-w-3xl mx-auto">
          <ChatInput
            onSend={handleSendMessage}
            onStop={handleStop}
            isStreaming={isStreaming || !!activeTask || !!autoTask}
            onUpload={(data) => {
              // data expected: { paper_id, file_path, message }
              const rawPath = data.file_path || '';
              const filename = (rawPath.replace(/\\/g, '/').split('/').pop()) || `paper-${data.paper_id}`;
              const paper = { id: data.paper_id, title: filename, file_path: data.file_path };
              try { addSelectedPaper(paper); } catch (e) {}
              setUploadedFiles(prev => [...prev, paper]);
            }}
          />
          {uploadedFiles.length > 0 && (
            <div className="mt-3 flex justify-center">
              <div className="bg-[var(--bg-card)] border border-[var(--border-color)] px-3 py-2 rounded-full flex items-center gap-3 shadow-sm">
                {uploadedFiles.map((f) => (
                  <div key={f.id} className="flex items-center gap-2 bg-[var(--bg-sidebar)] text-[var(--text-primary)] px-3 py-1 rounded-full">
                    <div className="w-5 h-5 shrink-0 flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-file-text"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><path d="M14 2v6h6"></path><path d="M8 13h8"></path><path d="M8 17h8"></path></svg>
                    </div>
                    <div className="text-xs font-medium">{f.title}</div>
                    <button
                      onClick={() => {
                        setUploadedFiles(prev => prev.filter(p => p.id !== f.id));
                        try { removeSelectedPaper(f.id); } catch (e) {}
                      }}
                      className="ml-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                      title="Remove uploaded file"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="text-center text-xs text-[var(--text-secondary)] mt-3">
            Smart Research Assistant can make mistakes. Consider verifying important information. Type <b>/cite</b> to generate citations.
          </div>
        </div>
      </div>
    </div>
  );
}
