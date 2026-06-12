import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAgent } from '../../contexts/AgentContext';

const TASK_LABELS = {
  summary: ['Loading paper data…', 'Retrieving document chunks…', 'Analyzing content…', 'Generating summary…', 'Finalizing…'],
  comparison: ['Loading selected papers…', 'Extracting paper metadata…', 'Identifying key dimensions…', 'Comparing methodologies…', 'Finalizing comparison…'],
};

function formatElapsed(ms) {
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
}

export default function TaskProgress({ taskId, taskType, onComplete, onError }) {
  const { selectedAgentId } = useAgent();
  const [taskStatus, setTaskStatus] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef(Date.now());
  const pollRef = useRef(null);
  const timerRef = useRef(null);

  const agentType = taskType || selectedAgentId;
  const steps = TASK_LABELS[agentType] || TASK_LABELS.summary;

  // ── Elapsed timer ────────────────────────────────────────────
  useEffect(() => {
    startRef.current = Date.now();
    timerRef.current = setInterval(() => {
      setElapsed(Date.now() - startRef.current);
    }, 500);
    return () => clearInterval(timerRef.current);
  }, [taskId]);

  // ── Polling ──────────────────────────────────────────────────
  useEffect(() => {
    if (!taskId) return;

    const poll = async () => {
      try {
        const res = await fetch(`http://localhost:8000/agent/task/${taskId}`);
        if (!res.ok) return;
        const data = await res.json();
        setTaskStatus(data);

        if (data.status === 'done') {
          clearInterval(pollRef.current);
          clearInterval(timerRef.current);
          onComplete?.(data);
        } else if (data.status === 'failed') {
          clearInterval(pollRef.current);
          clearInterval(timerRef.current);
          onError?.(data.error || 'Task failed');
        }
      } catch (_) {
        // Network error — keep polling
      }
    };

    poll(); // immediate first call
    pollRef.current = setInterval(poll, 2000);
    return () => clearInterval(pollRef.current);
  }, [taskId]);

  const progress = taskStatus?.progress ?? 0;
  const currentStep = taskStatus?.current_step ?? steps[0];
  const status = taskStatus?.status ?? 'pending';

  // Pick a step label based on progress brackets
  const stepIdx = Math.min(Math.floor((progress / 100) * steps.length), steps.length - 1);
  const displayStep = status === 'pending' ? 'Initializing…' : (currentStep || steps[stepIdx]);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-lg mx-auto"
      >
        {/* Header row */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            {/* Pulsing dots */}
            <div className="flex items-center gap-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 rounded-full bg-[var(--agent-primary)]"
                  animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15 }}
                />
              ))}
            </div>
            <span className="text-sm font-semibold agent-gradient-text capitalize">
              {`${agentType} Agent`}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)]">
            <span className="font-mono tabular-nums">{formatElapsed(elapsed)}</span>
            <span className="font-semibold tabular-nums text-[var(--agent-primary)]">{progress}%</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="relative h-2 bg-[var(--border-color)] rounded-full overflow-hidden mb-3">
          {/* Animated background shimmer */}
          <motion.div
            className="absolute inset-0 agent-gradient-animate opacity-20 rounded-full"
          />
          {/* Actual progress fill */}
          <motion.div
            className="absolute top-0 left-0 h-full rounded-full agent-gradient-bg"
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>

        {/* Current step label */}
        <AnimatePresence mode="wait">
          <motion.p
            key={displayStep}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 6 }}
            transition={{ duration: 0.25 }}
            className="text-xs text-[var(--text-secondary)] tracking-wide"
          >
            {displayStep}
          </motion.p>
        </AnimatePresence>
      </motion.div>
    </AnimatePresence>
  );
}
