import { create } from 'zustand';
import { produce } from 'immer';

interface AssertionInputStore {
  value: string;
  setValue: (value: string) => void;
}

export const useAssertionInputStore = create<AssertionInputStore>()((set) => ({
  value: '',
  setValue: (value) =>
    set(
      produce((state: AssertionInputStore) => {
        state.value = value;
      })
    ),
}));
