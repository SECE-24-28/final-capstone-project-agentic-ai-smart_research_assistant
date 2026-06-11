import api from './api';

export const chatApi = {
  chat: async (question, paperIds = null, sessionId = null) => {
    const response = await api.post('/agent/chat', { 
      question, 
      paper_ids: paperIds,
      session_id: sessionId
    });
    return response.data;
  }
};
