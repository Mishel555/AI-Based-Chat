import { useEffect } from 'react';
import api from '~/api';
import ValidationAssertion from '../ValidationAssertion';
import styles from './style.module.css';
import { useValidationSidebarAssertions } from '~/modules/ValidationSidebar/store/SidebarAssertionListStore';

type PropsType = {
  statementId?: string;
};

const ValidationSidebarAssertionList = ({ statementId }: PropsType) => {
  const assertionsList = useValidationSidebarAssertions((state) => state.assertions);
  const setAssertions = useValidationSidebarAssertions((state) => state.setAssertions);

  useEffect(() => {
    const fetchAssertion = async (statementId: string) => {
      const response = await api.chat.getAssertions(statementId);
      const { assertions, ids } = 'error' in response ? { assertions: [], ids: [] } : response;
      const list = ids.map((id, idx) => ({ id, value: assertions[idx] }));
      setAssertions(list);
    };

    if (statementId) fetchAssertion(statementId);
  }, [statementId]);

  return (
    <ol className={styles.root}>
      {statementId
        ? assertionsList.map((assertion) => (
            <ValidationAssertion
              key={assertion.id}
              statementId={statementId}
              assertion={assertion}
            />
          ))
        : 'No assertions'}
    </ol>
  );
};

export default ValidationSidebarAssertionList;
