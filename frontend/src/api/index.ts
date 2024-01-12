import Chat from './apis/Chat';
import Auth from './apis/Auth';
import { IApi } from './types';

const api: IApi = {
  chat: Chat(),
  auth: Auth(),
};

export default api;
