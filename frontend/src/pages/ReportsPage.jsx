import { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  FileText, Plus, Download, RefreshCw, Trash2,
  ChevronRight, Clock, Loader2, AlertCircle, FileDown,
} from 'lucide-react';
import {
  listReports, getReport, generateReport,
  regenerateReport, deleteReport,
  downloadPdf, downloadDocx,
} from '../services/reportApi';
import { listReports as _lr } from '../services/reportApi';

// ─── Task polling helper ───────────────────────────────────────────────────
const POLL_MS = 1500;

function usePollTask(taskId, onDone, onFail) {
  useEffect(() => {
    if (!taskId) return;
    const id = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/agent/task/${taskId}`);
        const data = await res.json();
        if (data.status === 'done') {
          clearInterval(id);
          onDone(data.result);
        } else if (data.status === 'failed') {
          clearInterval(id);
          onFail(data.error || 'Task failed');
        }
      } catch (e) {
        clearInterval(id);
        onFail(String(e));
      }
    }, POLL_MS);
    return () => clearInterval(id);
  }, [taskId]);
}

// ─── Progress bar ──────────────────────────────────────────────────────────
function ProgressBar({ value, label }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-[var(--text-secondary)]">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-[var(--border-color)] overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[#6366F1] to-[#A855F7] transition-all duration-500"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

// ─── Generate Report Modal ─────────────────────────────────────────────────
function GenerateModal({ onClose, onGenerated }) {
  const [topic, setTopic] = useState('');
  const [paperIdsStr, setPaperIdsStr] = useState('');
  const [loading, setLoading] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState('');
  const [error, setError] = useState('');

  // Poll while generation runs
  usePollTask(
    taskId,
    (result) => {
      setLoading(false);
      onGenerated(result?.report_id);
      onClose();
    },
    (err) => {
      setLoading(false);
      setError(err);
    },
  );

  // Live progress polling
  useEffect(() => {
    if (!taskId || !loading) return;
    const id = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/agent/task/${taskId}`);
        const data = await res.json();
        setProgress(data.progress || 0);
        setStep(data.current_step || '');
      } catch (_) {}
    }, 800);
    return () => clearInterval(id);
  }, [taskId, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const ids = paperIdsStr
      .split(',')
      .map((s) => parseInt(s.trim(), 10))
      .filter((n) => !isNaN(n));
    if (!topic.trim() || ids.length === 0) {
      setError('Please enter a topic and at least one paper ID.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const { data } = await generateReport(topic.trim(), ids);
      setTaskId(data.task_id);
    } catch (err) {
      setLoading(false);
      setError(err?.response?.data?.detail || 'Failed to start generation.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl shadow-2xl p-6 space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2">
            <Plus className="w-5 h-5 text-[#6366F1]" />
            Generate Research Report
          </h2>
          <button onClick={onClose} className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">✕</button>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded-lg p-3">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {loading ? (
          <div className="space-y-4 py-4">
            <div className="flex items-center gap-3 text-[var(--text-secondary)]">
              <Loader2 className="w-5 h-5 animate-spin text-[#6366F1]" />
              <span className="text-sm">{step || 'Initialising…'}</span>
            </div>
            <ProgressBar value={progress} label={step} />
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                Research Topic
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Federated Learning in Healthcare"
                className="w-full rounded-lg bg-[var(--bg-sidebar)] border border-[var(--border-color)] px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[#6366F1] transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">
                Paper IDs (comma-separated)
              </label>
              <input
                type="text"
                value={paperIdsStr}
                onChange={(e) => setPaperIdsStr(e.target.value)}
                placeholder="e.g. 1, 2, 3"
                className="w-full rounded-lg bg-[var(--bg-sidebar)] border border-[var(--border-color)] px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[#6366F1] transition-colors"
              />
              <p className="text-xs text-[var(--text-secondary)] mt-1">
                Find IDs in your Paper Library.
              </p>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-2 rounded-lg border border-[var(--border-color)] text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-[#6366F1] to-[#A855F7] hover:opacity-90 transition-opacity"
              >
                Generate
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

// ─── Report History Item ───────────────────────────────────────────────────
function HistoryItem({ report, isActive, onClick }) {
  const date = report.created_at
    ? new Date(report.created_at).toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric',
      })
    : '—';

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 rounded-xl border transition-all duration-200 group ${
        isActive
          ? 'bg-[#6366F1]/10 border-[#6366F1]/40 shadow-sm'
          : 'bg-[var(--bg-card)] border-[var(--border-color)] hover:border-[#6366F1]/30 hover:bg-[#6366F1]/5'
      }`}
    >
      <div className="flex items-start gap-2.5">
        <FileText className={`w-4 h-4 mt-0.5 flex-shrink-0 ${isActive ? 'text-[#6366F1]' : 'text-[var(--text-secondary)] group-hover:text-[#6366F1]'}`} />
        <div className="flex-1 min-w-0">
          <p className={`text-sm font-medium truncate ${isActive ? 'text-[#6366F1]' : 'text-[var(--text-primary)]'}`}>
            {report.title || report.topic}
          </p>
          <div className="flex items-center gap-1.5 mt-0.5">
            <Clock className="w-3 h-3 text-[var(--text-secondary)]" />
            <span className="text-xs text-[var(--text-secondary)]">{date}</span>
          </div>
        </div>
        <ChevronRight className={`w-4 h-4 flex-shrink-0 transition-transform ${isActive ? 'text-[#6366F1] translate-x-0.5' : 'text-[var(--text-secondary)]'}`} />
      </div>
    </button>
  );
}

// ─── Main ReportsPage ──────────────────────────────────────────────────────
export default function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [activeReport, setActiveReport] = useState(null);
  const [loadingReports, setLoadingReports] = useState(true);
  const [loadingView, setLoadingView] = useState(false);
  const [showGenModal, setShowGenModal] = useState(false);
  const [actionTaskId, setActionTaskId] = useState(null);
  const [actionProgress, setActionProgress] = useState(0);
  const [actionStep, setActionStep] = useState('');
  const [actionError, setActionError] = useState('');

  // fetch history
  const fetchReports = useCallback(async () => {
    setLoadingReports(true);
    try {
      const { data } = await listReports();
      setReports(Array.isArray(data) ? data : []);
    } catch (_) {
      setReports([]);
    } finally {
      setLoadingReports(false);
    }
  }, []);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  // view single report
  const handleSelect = async (reportId) => {
    setLoadingView(true);
    setActiveReport(null);
    try {
      const { data } = await getReport(reportId);
      setActiveReport(data);
    } catch (_) {
    } finally {
      setLoadingView(false);
    }
  };

  // task polling for regenerate
  usePollTask(
    actionTaskId,
    (result) => {
      setActionTaskId(null);
      fetchReports();
      if (result?.report_id) handleSelect(result.report_id);
    },
    (err) => {
      setActionTaskId(null);
      setActionError(err);
    },
  );

  // live progress for in-viewer actions
  useEffect(() => {
    if (!actionTaskId) return;
    const id = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/agent/task/${actionTaskId}`);
        const data = await res.json();
        setActionProgress(data.progress || 0);
        setActionStep(data.current_step || '');
      } catch (_) {}
    }, 800);
    return () => clearInterval(id);
  }, [actionTaskId]);

  const handleDelete = async () => {
    if (!activeReport) return;
    if (!window.confirm(`Delete report "${activeReport.title}"?`)) return;
    try {
      await deleteReport(activeReport.report_id);
      setActiveReport(null);
      fetchReports();
    } catch (err) {
      setActionError(err?.response?.data?.detail || 'Delete failed');
    }
  };

  const handleRegenerate = async () => {
    if (!activeReport) return;
    setActionError('');
    setActionProgress(0);
    setActionStep('Starting regeneration…');
    try {
      const { data } = await regenerateReport(activeReport.report_id);
      setActionTaskId(data.task_id);
    } catch (err) {
      setActionError(err?.response?.data?.detail || 'Regeneration failed');
    }
  };

  return (
    <div className="flex h-full" data-agent="auto">
      {/* ── LEFT: History Panel ── */}
      <aside className="w-72 flex-shrink-0 border-r border-[var(--border-color)] bg-[var(--bg-sidebar)] flex flex-col">
        <div className="p-4 border-b border-[var(--border-color)]">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-[var(--text-primary)] flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#6366F1]" />
              Reports
            </h2>
            <button
              onClick={() => setShowGenModal(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-[#6366F1] to-[#A855F7] hover:opacity-90 transition-opacity"
            >
              <Plus className="w-3.5 h-3.5" />
              New
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {loadingReports ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-5 h-5 animate-spin text-[#6366F1]" />
            </div>
          ) : reports.length === 0 ? (
            <div className="text-center py-12 text-[var(--text-secondary)] text-sm">
              <FileText className="w-8 h-8 mx-auto mb-2 opacity-30" />
              No reports yet.<br />Click <strong>+ New</strong> to generate one.
            </div>
          ) : (
            reports.map((r) => (
              <HistoryItem
                key={r.report_id}
                report={r}
                isActive={activeReport?.report_id === r.report_id}
                onClick={() => handleSelect(r.report_id)}
              />
            ))
          )}
        </div>
      </aside>

      {/* ── RIGHT: Viewer ── */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {!activeReport && !loadingView ? (
          /* Empty state */
          <div className="flex-1 flex flex-col items-center justify-center text-[var(--text-secondary)] space-y-4">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#6366F1]/20 to-[#A855F7]/20 flex items-center justify-center">
              <FileText className="w-10 h-10 text-[#6366F1]" />
            </div>
            <div className="text-center">
              <p className="font-medium text-[var(--text-primary)]">No report selected</p>
              <p className="text-sm mt-1">Select a report from the left, or generate a new one.</p>
            </div>
            <button
              onClick={() => setShowGenModal(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-[#6366F1] to-[#A855F7] hover:opacity-90 transition-opacity"
            >
              <Plus className="w-4 h-4" />
              Generate Research Report
            </button>
          </div>
        ) : loadingView ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-[#6366F1]" />
          </div>
        ) : (
          <>
            {/* Toolbar */}
            <div className="flex-shrink-0 border-b border-[var(--border-color)] bg-[var(--bg-card)] px-6 py-3 flex items-center justify-between">
              <div>
                <h1 className="font-bold text-[var(--text-primary)] text-base truncate max-w-xl">
                  {activeReport.title || activeReport.topic}
                </h1>
                <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                  {activeReport.template_type} &nbsp;·&nbsp;{' '}
                  {activeReport.created_at
                    ? new Date(activeReport.created_at).toLocaleString()
                    : '—'}
                </p>
              </div>

              <div className="flex items-center gap-2">
                {/* Regenerate */}
                <button
                  onClick={handleRegenerate}
                  disabled={!!actionTaskId}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--border-color)] text-xs font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[#6366F1]/50 transition-all disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${actionTaskId ? 'animate-spin' : ''}`} />
                  Regenerate
                </button>
                {/* Download PDF */}
                <button
                  onClick={() => downloadPdf(activeReport.report_id, activeReport.title || activeReport.topic)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--border-color)] text-xs font-medium text-[var(--text-secondary)] hover:text-red-400 hover:border-red-400/40 transition-all"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  PDF
                </button>
                {/* Download DOCX */}
                <button
                  onClick={() => downloadDocx(activeReport.report_id, activeReport.title || activeReport.topic)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--border-color)] text-xs font-medium text-[var(--text-secondary)] hover:text-blue-400 hover:border-blue-400/40 transition-all"
                >
                  <Download className="w-3.5 h-3.5" />
                  DOCX
                </button>
                {/* Delete */}
                <button
                  onClick={handleDelete}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--border-color)] text-xs font-medium text-[var(--text-secondary)] hover:text-red-400 hover:border-red-400/40 transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete
                </button>
              </div>
            </div>

            {/* Action progress */}
            {actionTaskId && (
              <div className="px-6 py-3 bg-[#6366F1]/5 border-b border-[#6366F1]/20">
                <ProgressBar value={actionProgress} label={actionStep} />
              </div>
            )}

            {/* Error */}
            {actionError && (
              <div className="mx-6 mt-4 flex items-center gap-2 text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded-lg p-3">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {actionError}
              </div>
            )}

            {/* Markdown content */}
            <div className="flex-1 overflow-y-auto px-8 py-6">
              <article className="max-w-4xl mx-auto prose prose-sm dark:prose-invert markdown-body">
                <ReactMarkdown>
                  {activeReport.report_markdown || '*(No content available)*'}
                </ReactMarkdown>
              </article>
            </div>
          </>
        )}
      </main>

      {/* Generate modal */}
      {showGenModal && (
        <GenerateModal
          onClose={() => setShowGenModal(false)}
          onGenerated={(reportId) => {
            fetchReports();
            if (reportId) handleSelect(reportId);
          }}
        />
      )}
    </div>
  );
}
