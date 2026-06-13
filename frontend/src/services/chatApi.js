import api from './api';

export const chatApi = {
  chat: async (question, paperIds = null, sessionId = null) => {
    const response = await api.post('/agent/chat', { 
      question, 
      paper_ids: paperIds,
      session_id: sessionId
    });
    return response.data;
  },

  createSession: async (title = 'New Research') => {
    const response = await api.post('/chat/session', { title });
    return response.data;
  },

  getSessions: async () => {
    const response = await api.get('/chat/sessions');
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/chat/session/${sessionId}`);
    return response.data;
  },

  deleteSession: async (sessionId) => {
    const response = await api.delete(`/chat/session/${sessionId}`);
    return response.data;
  },

  createMessage: async (sessionId, role, content, agentType = null) => {
    const response = await api.post('/chat/message', {
      session_id: sessionId,
      role,
      content,
      agent_type: agentType
    });
    return response.data;
  }
};
