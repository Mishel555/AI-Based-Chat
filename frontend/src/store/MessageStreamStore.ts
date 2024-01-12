import { create } from 'zustand';
import { produce } from 'immer';

export interface IStreamMessageStore {
  isActiveStream: boolean;
  message: string;
  appendMessage: (messagePart: string) => void;
  resetMessage: () => void;
  startStream: () => void;
  stopStream: () => void;
}

const useStreamMessageStore = create<IStreamMessageStore>()((set) => ({
  isActiveStream: false,
  message: '',
  startStream: () =>
    set(
      produce((state: IStreamMessageStore) => {
        state.isActiveStream = true;
      })
    ),
  stopStream: () =>
    set(
      produce((state: IStreamMessageStore) => {
        state.isActiveStream = false;
      })
    ),
  appendMessage: (messagePart) =>
    set(
      produce((state: IStreamMessageStore) => {
        state.message += messagePart;
      })
    ),
  resetMessage: () =>
    set(
      produce((state: IStreamMessageStore) => {
        state.message = '';
      })
    ),
}));

export default useStreamMessageStore;
