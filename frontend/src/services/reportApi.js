import api from './api';

// ── Report generation ────────────────────────────────────────────────────────

export const generateReport = (topic, paperIds, comparisonId = null) =>
  api.post('/report/generate', {
    topic,
    paper_ids: paperIds,
    comparison_id: comparisonId,
    template_type: 'Research Report',
  });

// ── Report retrieval ─────────────────────────────────────────────────────────

export const listReports = () => api.get('/reports');

export const getReport = (reportId) => api.get(`/report/${reportId}`);

// ── Regenerate / Delete ───────────────────────────────────────────────────────

export const regenerateReport = (reportId) =>
  api.post(`/report/${reportId}/regenerate`);

export const deleteReport = (reportId) =>
  api.delete(`/report/${reportId}`);

// ── Export helpers ────────────────────────────────────────────────────────────

export const downloadPdf = (reportId, title = 'Research_Report') => {
  const link = document.createElement('a');
  link.href = `http://localhost:8000/report/${reportId}/pdf`;
  link.setAttribute('download', `${title}.pdf`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const downloadDocx = (reportId, title = 'Research_Report') => {
  const link = document.createElement('a');
  link.href = `http://localhost:8000/report/${reportId}/docx`;
  link.setAttribute('download', `${title}.docx`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
