import axios from 'axios';
import Cookies from 'js-cookie';
import { useAuthStore } from '~/store';

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_REST_URL,
});

axiosInstance.interceptors.request.use(
  (config) => {
    const session = Cookies.get('session');
    config.withCredentials = true;

    if (session) {
      // config.headers['X-Jwt-Token'] = session;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(
  (AxiosResponse) => AxiosResponse,
  (AxiosError) => {
    if (AxiosError.response?.status === 403) {
      // unauthorized
      useAuthStore.getState().logout();
      return Promise.reject(AxiosError);
    }

    return Promise.reject(AxiosError);
  }
);

export default axiosInstance;
