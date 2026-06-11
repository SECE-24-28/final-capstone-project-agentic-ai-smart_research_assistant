import api from './api';

export const comparisonApi = {
  comparePapers: async (paperIds) => {
    const response = await api.post('/agent/compare', { paper_ids: paperIds });
    return response.data;
  },
};

