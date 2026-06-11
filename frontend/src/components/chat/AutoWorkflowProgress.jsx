import { motion, AnimatePresence } from 'framer-motion';
import { Check, Loader2, Clock, AlertCircle, Sparkles } from 'lucide-react';

const STEP_ICONS = {
  'Search Agent':            '🔍',
  'Summary Agent':           '📄',
  'Comparison Agent':        '⚖️',
  'Gap Agent':               '🎯',
  'Literature Review Agent': '📚',
  'Chat Agent':              '💬',
};

const WORKFLOW_DESCRIPTIONS = {
  'Paper Discovery':              'Searching for relevant papers on your topic.',
  'Paper Summarization':          'Searching and summarizing key findings.',
  'Comparative Analysis':         'Comparing methodologies across papers.',
  'Research Gap Analysis':        'Identifying unexplored research areas.',
  'Literature Review Generation': 'Creating a comprehensive academic review.',
  'Research Q&A':                 'Answering from your paper context.',
};

function StepItem({ step, index }) {
  const icon = STEP_ICONS[step.agent_name] || '🤖';
  const isDone    = step.status === 'done';
  const isRunning = step.status === 'running';
  const isFailed  = step.status === 'failed';
  const isSkipped = step.status === 'skipped';
  const isPending = step.status === 'pending';

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08, duration: 0.3 }}
      className={`flex items-center gap-3 py-2 px-3 rounded-lg transition-colors duration-300
        ${isRunning ? 'bg-[color-mix(in_srgb,var(--agent-primary)_8%,transparent)]' : 'bg-transparent'}`}
    >
      {/* Status icon */}
      <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-sm transition-all duration-300
        ${isDone    ? 'bg-[color-mix(in_srgb,var(--agent-primary)_15%,transparent)] text-[var(--agent-primary)]'
        : isRunning ? 'bg-[color-mix(in_srgb,var(--agent-primary)_10%,transparent)]'
        : isFailed  ? 'bg-red-100 dark:bg-red-900/30 text-red-500'
        : isSkipped ? 'bg-[var(--bg-sidebar)] text-[var(--text-secondary)]'
        : 'bg-[var(--bg-sidebar)] text-[var(--text-secondary)]'}`}
      >
        {isDone    && <Check className="w-3.5 h-3.5 text-[var(--agent-primary)]" />}
        {isRunning && (
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
            <Loader2 className="w-3.5 h-3.5 text-[var(--agent-primary)]" />
          </motion.div>
        )}
        {isFailed  && <AlertCircle className="w-3.5 h-3.5 text-red-500" />}
        {isSkipped && <span className="text-xs">–</span>}
        {isPending && <Clock className="w-3 h-3 text-[var(--text-secondary)]" />}
      </div>

      {/* Step info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm">{icon}</span>
          <span className={`text-sm font-medium transition-colors duration-300
            ${isDone    ? 'text-[var(--agent-primary)]'
            : isRunning ? 'text-[var(--text-primary)]'
            : isFailed  ? 'text-red-500'
            : 'text-[var(--text-secondary)]'}`}>
            {step.agent_name}
          </span>
        </div>
        <p className="text-xs text-[var(--text-secondary)] truncate mt-0.5 leading-tight">
          {step.description}
        </p>
      </div>

      {/* Running badge */}
      {isRunning && (
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.2, repeat: Infinity }}
          className="text-xs font-medium text-[var(--agent-primary)] flex-shrink-0"
        >
          Running…
        </motion.span>
      )}
      {isDone && (
        <span className="text-xs text-[var(--text-secondary)] flex-shrink-0">Done</span>
      )}
    </motion.div>
  );
}

export default function AutoWorkflowProgress({ workflow, intent, topic, steps = [], taskProgress = null }) {
  const description = WORKFLOW_DESCRIPTIONS[workflow] || '';
  const doneCount = steps.filter(s => s.status === 'done').length;
  const totalCount = steps.length;

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className="w-8 h-8 rounded-full agent-gradient-bg flex items-center justify-center flex-shrink-0">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-semibold text-sm text-[var(--text-primary)]">{workflow}</h4>
            <span className="text-xs px-2 py-0.5 rounded-full bg-[color-mix(in_srgb,var(--agent-primary)_10%,transparent)] text-[var(--agent-primary)] font-medium">
              Auto Mode
            </span>
          </div>
          <p className="text-xs text-[var(--text-secondary)] mt-0.5">
            Topic: <span className="font-medium text-[var(--text-primary)]">{topic}</span>
          </p>
          {description && (
            <p className="text-xs text-[var(--text-secondary)] mt-0.5">{description}</p>
          )}
        </div>
      </div>

      {/* Overall progress bar */}
      {taskProgress !== null && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-[var(--text-secondary)]">
              Step {doneCount} of {totalCount}
            </span>
            <span className="text-xs font-semibold text-[var(--agent-primary)]">
              {taskProgress}%
            </span>
          </div>
          <div className="h-1.5 bg-[var(--border-color)] rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full agent-gradient-bg"
              initial={{ width: '0%' }}
              animate={{ width: `${taskProgress}%` }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            />
          </div>
        </div>
      )}

      {/* Workflow steps */}
      {steps.length > 0 && (
        <div className="border border-[var(--border-color)] rounded-xl overflow-hidden">
          <div className="divide-y divide-[var(--border-color)]">
            {steps.map((step, i) => (
              <StepItem key={step.step_number} step={step} index={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
