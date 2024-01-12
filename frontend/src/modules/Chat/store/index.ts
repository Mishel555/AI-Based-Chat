import { create } from 'zustand';
import { produce } from 'immer';

interface IInputStore {
  value: string;
  change: (value: string) => void;
  concat: (value: string | string[]) => void;
  isCanWrite: boolean;
  setCanWrite: (status: boolean) => void;
}

export const useInputStore = create<IInputStore>()((set) => ({
  value: '',
  isCanWrite: true,
  setCanWrite: (status: boolean) =>
    set(
      produce((state: IInputStore) => {
        state.isCanWrite = status;
      })
    ),
  change: (value) => set(() => ({ value })),
  concat: (value) =>
    set((state) => ({
      value: Array.isArray(value) ? state.value + value.join(' ') : state.value + value,
    })),
}));
