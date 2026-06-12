import api from './api';

/**
 * Poll task status from GET /agent/task/{task_id}
 */
export async function getTaskStatus(taskId) {
  const { data } = await api.get(`/agent/task/${taskId}`);
  return data;
}

/**
 * Get the result of a completed summary task
 */
export async function getSummaryResult(taskId) {
  const { data } = await api.get(`/agent/summary/result/${taskId}`);
  return data;
}

/**
 * Get the result of a completed comparison task
 */
export async function getCompareResult(taskId) {
  const { data } = await api.get(`/agent/compare/result/${taskId}`);
  return data;
}


/**
 * Poll a task until it completes, calling onProgress on each update.
 * Returns the final status record.
 *
 * @param {string} taskId
 * @param {function} onProgress  - called with TaskStatusResponse on each tick
 * @param {number}  intervalMs  - polling interval (default 2000ms)
 * @param {number}  timeoutMs   - max wait time (default 5 minutes)
 */
export async function pollTask(taskId, onProgress, intervalMs = 2000, timeoutMs = 300000) {
  const start = Date.now();

  return new Promise((resolve, reject) => {
    const check = async () => {
      try {
        if (Date.now() - start > timeoutMs) {
          reject(new Error(`Task ${taskId} timed out after ${timeoutMs / 1000}s`));
          return;
        }

        const status = await getTaskStatus(taskId);
        onProgress(status);

        if (status.status === 'done') {
          resolve(status);
        } else if (status.status === 'failed') {
          reject(new Error(status.error || 'Task failed'));
        } else {
          setTimeout(check, intervalMs);
        }
      } catch (err) {
        reject(err);
      }
    };

    setTimeout(check, intervalMs);
  });
}
