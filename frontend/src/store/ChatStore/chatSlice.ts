import { StateCreator } from 'zustand';
import chatStore from '~/store/ChatStore/index';
import { useValidationSidebarStore } from '~/modules/ValidationSidebar/ValidationSidebar';

export interface IChatSlice {
  currentChat: string | null;
  isChatActive: (id: string) => boolean;
  changeCurrentChat: (id: string | null) => void;
  setCurrentChat: (id: string | null) => void;
}

export const createChatSlice: StateCreator<IChatSlice> = (set, get) => ({
  currentChat: null,
  isChatActive: (id: string) => {
    const { currentChat } = get();
    return id === currentChat;
  },
  setCurrentChat: (id) => set((state) => ({ ...state, currentChat: id })),
  changeCurrentChat: (id) => {
    if (id === get().currentChat) return;
    chatStore.getState().setCurrentChat(id);
    useValidationSidebarStore.getState().close();
  },
});
