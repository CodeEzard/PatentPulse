import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

export default {
  getDomains() {
    return client.get('/trends/domains/').then((res) => res.data)
  },
  getTrendSummary(domain = null) {
    return client
      .get('/trends/summary/', { params: domain ? { domain } : {} })
      .then((res) => res.data)
  },
  getPatents(params = {}) {
    return client.get('/patents/', { params }).then((res) => res.data)
  },
}
