import api from './api';

/**
 * Start an autonomous research pipeline.
 * Returns { task_id, workflow, intent, topic, estimated_steps, estimated_duration }
 */
export async function startAutoResearch(query, paperIds = null) {
  const payload = { query };
  if (paperIds && paperIds.length > 0) payload.paper_ids = paperIds;
  const { data } = await api.post('/agent/auto', payload);
  return data;
}

/**
 * Retrieve the complete result of a finished Auto Mode task.
 */
export async function getAutoResult(taskId) {
  const { data } = await api.get(`/agent/auto/result/${taskId}`);
  return data;
}
