import { BsSendFill } from 'react-icons/bs';
import styles from './style.module.css';
import { KeyboardEvent } from 'react';
import { useValidationSidebarAssertions } from '~/modules/ValidationSidebar/store';
import { v4 as uuid } from 'uuid';
import { cacheService } from '~/api/cache';
import { useChatStore } from '~/store';
import { useAssertionInputStore } from '~/modules/ValidationSidebar/store/AssertionInputStore';

const ValidationSidebarInput = ({ statementId }: { statementId: string }) => {
  const chatId = useChatStore((state) => state.currentChat);
  const addAssertion = useValidationSidebarAssertions((state) => state.addAssertions);

  const value = useAssertionInputStore((state) => state.value);
  const setValue = useAssertionInputStore((state) => state.setValue);

  const handleAddAssertion = () => {
    if (!chatId) return;
    addAssertion({ value, id: uuid() });
    cacheService.addAssertion(chatId, statementId, { assertion: value, id: uuid() });
    setValue('');
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleAddAssertion();
    }
  };

  return (
    <div className={styles.root}>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        type="text"
        onKeyDown={handleKeyDown}
        placeholder="Add an assertion..."
      />
      <button onClick={handleAddAssertion}>
        <BsSendFill />
      </button>
    </div>
  );
};

export default ValidationSidebarInput;
