/**
 * api.js - REST API Client for CodeSnap Backend
 */

const API = {
  baseUrl: (window.location.protocol === 'http:' || window.location.protocol === 'https:')
    ? '' 
    : 'http://localhost:5050',

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    try {
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  async checkHealth() {
    return this.request('/api/health');
  },

  async getExamples() {
    return this.request('/api/examples');
  },

  async getExample(id) {
    return this.request(`/api/examples/${id}`);
  },

  async getGrammar() {
    return this.request('/api/grammar');
  },

  async getAutomata() {
    return this.request('/api/automata');
  },

  async testAutomata(dfaId, inputString) {
    return this.request('/api/automata/test', {
      method: 'POST',
      body: JSON.stringify({ dfa_id: dfaId, input_string: inputString })
    });
  },

  async compile(sourceCode) {
    return this.request('/api/compile', {
      method: 'POST',
      body: JSON.stringify({ source_code: sourceCode })
    });
  },

  async run(sourceCode) {
    return this.request('/api/run', {
      method: 'POST',
      body: JSON.stringify({ source_code: sourceCode })
    });
  },

  async lex(sourceCode) {
    return this.request('/api/lex', {
      method: 'POST',
      body: JSON.stringify({ source_code: sourceCode })
    });
  },

  async parse(sourceCode) {
    return this.request('/api/parse', {
      method: 'POST',
      body: JSON.stringify({ source_code: sourceCode })
    });
  },

  async semantic(sourceCode) {
    return this.request('/api/semantic', {
      method: 'POST',
      body: JSON.stringify({ source_code: sourceCode })
    });
  }
};
