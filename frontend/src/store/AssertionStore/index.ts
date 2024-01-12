import { create } from 'zustand';
import { produce } from 'immer';

export interface IAssertionStore {
  assertions: string[];
  assertionIds: string[];
  setAssertions: (assertions: string[], ids: string[]) => void;
}

const useAssertionStore = create<IAssertionStore>()((set) => ({
  assertions: [],
  assertionIds: [],
  setAssertions: (assertions, ids) =>
    set(
      produce((state: IAssertionStore) => {
        state.assertions = assertions;
        state.assertionIds = ids;
      })
    ),
}));

export default useAssertionStore;
