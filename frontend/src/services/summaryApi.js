import api from './api';

export const summaryApi = {
  generateSummary: async (paperId) => {
    // Backend uses query param: POST /agent/summary?paper_id=X
    const response = await api.post(`/agent/summary?paper_id=${paperId}`);
    return response.data;
  },
};

