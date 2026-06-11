import api from './api';

export const gapApi = {
  analyzeGaps: async (paperIds, topic = 'Research Analysis') => {
    const response = await api.post('/agent/gap', { topic, paper_ids: paperIds });
    return response.data;
  },
};

