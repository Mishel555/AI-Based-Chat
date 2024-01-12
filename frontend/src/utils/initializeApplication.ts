import Cookies from 'js-cookie';
import { wsService } from '~/api/ws/WsService';
import { INITIAL_USER } from '~/store/AuthStore';
import { useAuthStore } from '~/store';

export const init = async () => {
  const session = Cookies.get('session');
  if (!session) return useAuthStore.getState().logout();

  useAuthStore.getState().setUser(INITIAL_USER);

  const response = await wsService.connect(session);
  if (response?.email) {
    useAuthStore.getState().setUser({
      id: response.email,
      email: response.email,
      avatar: INITIAL_USER.avatar,
    });
  }
};
