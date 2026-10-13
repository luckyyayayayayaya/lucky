const API = {
  async submitThought(content) {
    const res = await fetch('/api/thoughts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '出错了');
    return data;
  },

  async getThoughts(page = 1, limit = 20) {
    const res = await fetch(`/api/thoughts?page=${page}&limit=${limit}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '出错了');
    return data;
  },

  async getThought(id) {
    const res = await fetch(`/api/thoughts/${id}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '出错了');
    return data;
  },

  async getGarden() {
    const res = await fetch('/api/garden');
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '出错了');
    return data;
  },

  async getGardenStats() {
    const res = await fetch('/api/garden/stats');
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '出错了');
    return data;
  },

  async getDailyMessage(type) {
    const res = await fetch(`/api/daily/message?type=${type}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '出错了');
    return data;
  },

  async getStats() {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '出错了');
    return data;
  },
};
