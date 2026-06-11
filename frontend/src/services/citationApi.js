import api from './api';

export const citationApi = {
  generateCitation: async (paperId, citationType = 'apa') => {
    const response = await api.post('/agent/citation', { paper_id: paperId, citation_type: citationType });
    return response.data;
  }
};
