import api from './api';

export const reviewApi = {
  generateReview: async (paperIds, topic = 'Research Analysis') => {
    const response = await api.post('/agent/review', { topic, paper_ids: paperIds });
    return response.data;
  },
};

