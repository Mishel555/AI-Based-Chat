import { TopicType } from '~/types';
import { BsChatLeft } from 'react-icons/bs';
import { KeyboardEvent, Ref, useEffect, useState } from 'react';
import { CommonPropsType, ConfirmChatOperations } from '../common';
import styles from '../style.module.css';

type PropsType = CommonPropsType & {
  chatLink: TopicType;
  isActive: boolean;
  inputRef: Ref<HTMLInputElement>;
};

const ChatLinkEdit = ({ inputRef, chatLink, isActive, onCancel, onConfirm }: PropsType) => {
  const [value, setValue] = useState<string>(chatLink.title);

  useEffect(() => {
    const listener = (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        onConfirm(chatLink.id, e.currentTarget.value);
      }
    };

    // @ts-ignore
    inputRef.current?.addEventListener('keypress', listener);

    return () => {
      // @ts-ignore
      inputRef.current?.removeEventListener('keypress', listener);
    };
  }, []);

  return (
    <>
      <BsChatLeft />

      <div className={styles.edit_input}>
        <input
          autoFocus
          type="text"
          ref={inputRef}
          value={value}
          maxLength={50}
          onChange={(e) => setValue(e.target.value)}
        />
      </div>

      {isActive && (
        <ConfirmChatOperations onConfirm={() => onConfirm(chatLink.id, value)} onCancel={() => onCancel()} />
      )}
    </>
  );
};

export default ChatLinkEdit;
