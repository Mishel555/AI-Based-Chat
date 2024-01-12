import React, { useEffect, useState } from 'react';
import styles from '~/modules/Chat/components/ChatMessage/ChatMessage.module.css';
import { BsClipboard, MdDone } from 'react-icons/all';

export const CopyButton = ({ action }: { action: () => void }) => {
  const [showSecondary, setShowSecondary] = useState<boolean>(false);

  const onClick = () => {
    action();

    setShowSecondary(true);
  };

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;

    if (showSecondary) {
      timeout = setTimeout(() => setShowSecondary(false), 1500);
    }

    return () => {
      if (timeout) {
        clearTimeout(timeout);
      }
    };
  }, [showSecondary]);

  return (
    <button
      type="button"
      disabled={showSecondary}
      onClick={onClick}
      className={styles.root__button}
    >
      {showSecondary && <MdDone />}
      {!showSecondary && <BsClipboard />}
    </button>
  );
};
