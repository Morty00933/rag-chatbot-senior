import axios from 'axios';

// приоритет: .env → Vite env → дефолт
const baseURL =
  (typeof window !== 'undefined' && (window as any).__API_BASE_URL__) ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8010';

export const api = axios.create({
  baseURL,
  withCredentials: false,
  headers: { 'Content-Type': 'application/json' },
});
