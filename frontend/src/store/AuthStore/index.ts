import { create } from 'zustand';
import { produce } from 'immer';
import Cookies from 'js-cookie';
import { UserType } from '~/types';

export interface IAuthStore {
  user: UserType | null;
  logout: () => void;
  setUser: (user: UserType) => void;
}

export const INITIAL_USER: UserType = {
  id: '1111',
  email: '...',
  avatar: './chatgpt.png',
};

const useAuthStore = create<IAuthStore>()((set) => ({
  user: null,
  setUser: (user) =>
    set(
      produce((state: IAuthStore) => {
        state.user = user;
      })
    ),
  logout: () =>
    set(
      produce((state: IAuthStore) => {
        Cookies.remove('session');

        state.user = null;
      })
    ),
}));

export default useAuthStore;
