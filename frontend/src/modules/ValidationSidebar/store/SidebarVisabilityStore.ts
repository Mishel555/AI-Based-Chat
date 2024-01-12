import { create } from 'zustand';
import { produce } from 'immer';

export type Assertion = {
  id: string;
  value: string;
};

interface IActiveChatStore {
  visible: boolean;
  open: () => void;
  close: () => void;
  selectedStatementId: string | null;
  setStatementId: (statementId: string) => void;
}

export const useValidationSidebarStore = create<IActiveChatStore>()((set) => ({
  visible: false,
  open: () => set((state) => ({ ...state, visible: true })),
  close: () => set((state) => ({ ...state, visible: false })),
  selectedStatementId: null,
  setStatementId: (statementId) =>
    set(
      produce((state: IActiveChatStore) => {
        state.selectedStatementId = statementId;
      })
    ),
}));
