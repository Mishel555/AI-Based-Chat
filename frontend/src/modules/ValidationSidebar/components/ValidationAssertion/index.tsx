import React, { useState } from 'react';
import { useInputStore } from '~/modules/Chat';
import { Assertion } from '../../store/SidebarVisabilityStore';
import AssertionOperationButtons from '../AssertionOperationButtons';
import EvidenceList from '../EvidenceList';
import styles from './style.module.css';
import { ACTIONS } from '~/modules/Chat/constants';
import { useAssertionInputStore } from '~/modules/ValidationSidebar/store';

enum Statuses {
  VIEW,
}

const ValidationAssertion = ({
  assertion,
  statementId,
}: {
  assertion: Assertion;
  statementId: string;
}) => {
  const changeAssertionInput = useAssertionInputStore((state) => state.setValue);
  const changeInputValue = useInputStore((state) => state.change);

  const [status] = useState(Statuses.VIEW);
  const [isEvidenceVisible, setAssertionVisibility] = useState(false);

  const isView = status === Statuses.VIEW;

  const sendAssertionToForm = () => {
    changeInputValue(`${ACTIONS.EXPLORE} ${assertion.value}`);
  };

  const editAssertion = () => {
    changeAssertionInput(assertion.value);
  };

  const handleCheckAssertion = () => {
    setAssertionVisibility(!isEvidenceVisible);
  };

  return (
    <li className={styles.root}>
      <div className={styles.assertion}>
        {isView && <span>{assertion.value}</span>}

        {isView && (
          <AssertionOperationButtons
            opened={isEvidenceVisible}
            onSend={sendAssertionToForm}
            onEdit={editAssertion}
            onCheck={handleCheckAssertion}
          />
        )}
      </div>
      {isEvidenceVisible && (
        <div className={styles.evidence_container}>
          <EvidenceList
            assertionId={assertion.id}
            statementId={statementId}
            assertionValue={assertion.value}
          />
        </div>
      )}
    </li>
  );
};

export default ValidationAssertion;
