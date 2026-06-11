import api from './api';

export const searchApi = {
  searchPapers: async (topic, limit = 5) => {
    const response = await api.post('/search/topic', { topic, limit });
    return response.data;
  },
};
