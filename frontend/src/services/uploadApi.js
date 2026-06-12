import api from './api';

export const uploadApi = {
  uploadPdf: (file, onUploadProgress) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/upload/pdf', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    });
  },
};

export default uploadApi;
