import { useEffect, useState } from 'react';
import classNames from 'classnames';
import { useInputStore } from '../../../store';
import styles from './style.module.css';
import api from '~/api';

const AssertionList = ({ statementId }: { statementId: string }) => {
  const [assertionsValue, setAssertions] = useState<string[]>([]);
  useEffect(() => {
    const fetchAssertion = async (statementId: string) => {
      const response = await api.chat.getAssertions(statementId);
      if (!response) return;
      const { assertions } = 'error' in response ? { assertions: [] } : response;
      setAssertions(assertions);
    };

    if (statementId) fetchAssertion(statementId);
  }, [statementId]);

  const concat = useInputStore((state) => state.concat);

  const [focusedAssertion, setFocusedAssertion] = useState<number>(0);

  const handleClickAssertion = (assertion: string) => concat(['', assertion]);

  const nextAssertion = () =>
    setFocusedAssertion((prevState) =>
      prevState === assertionsValue.length - 1 ? 0 : prevState + 1
    );

  const prevAssertion = () =>
    setFocusedAssertion((prevState) =>
      prevState === 0 ? assertionsValue.length - 1 : prevState - 1
    );

  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      const { key } = e;

      if (key === 'ArrowDown') {
        nextAssertion();
        e.preventDefault();
      }

      if (key === 'ArrowUp') {
        prevAssertion();
        e.preventDefault();
      }

      if (key === 'Enter') {
        handleClickAssertion(assertionsValue[focusedAssertion]);

        e.preventDefault();
      }
    };

    document.addEventListener('keydown', listener);

    return () => document.removeEventListener('keydown', listener);
  }, [assertionsValue]);

  return (
    <ul autoFocus className={styles.root}>
      {assertionsValue?.length > 0 ? (
        assertionsValue.map((assertion, index) => (
          <li
            key={assertion}
            onClick={() => handleClickAssertion(assertion)}
            className={classNames(
              styles.root__button,
              focusedAssertion === index && styles.focused
            )}
          >
            {assertion}
          </li>
        ))
      ) : (
        <div>No assertion for the last message</div>
      )}
    </ul>
  );
};

export default AssertionList;
