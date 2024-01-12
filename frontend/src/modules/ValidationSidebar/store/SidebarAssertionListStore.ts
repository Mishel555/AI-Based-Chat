import { create } from 'zustand';
import { produce } from 'immer';
import { Assertion } from '~/modules/ValidationSidebar/store/SidebarVisabilityStore';

interface IValidationSidebarAssertions {
  assertions: Assertion[];
  setAssertions: (assertions: Assertion[]) => void;
  addAssertions: (assertion: Assertion) => void;
}

export const useValidationSidebarAssertions = create<IValidationSidebarAssertions>()((set) => ({
  assertions: [],
  setAssertions: (assertions) => {
    return set(
      produce((state: IValidationSidebarAssertions) => {
        state.assertions = assertions;
      })
    );
  },
  addAssertions: (assertion) => {
    return set(
      produce((state: IValidationSidebarAssertions) => {
        state.assertions.push(assertion);
      })
    );
  },
}));
