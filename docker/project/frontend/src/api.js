import axios from 'axios'

const url =
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : (import.meta.env.VITE_API_URL || 'http://backend:8000');

export default axios.create({ baseURL: url })
