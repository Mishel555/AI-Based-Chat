import React, { ReactNode } from 'react';
import styles from './ChatMessage.module.css';
import { FaRegEye, FiEdit, ImLoop2 } from 'react-icons/all';

export { ValidationOpenButton } from './action-buttons/ValidationOpenButton';
export { CopyButton as CopyComponent } from './action-buttons/CopyButton';
export { BookUrl } from './action-buttons/BookUrl';

export function getDefaultAction(component: ReactNode) {
  return function Component({ action }: { action: () => void }) {
    return (
      <button type="button" onClick={action} className={styles.root__button}>
        {component}
      </button>
    );
  };
}

export const EditComponent = getDefaultAction(<FiEdit />);
export const RegenerateComponent = getDefaultAction(<ImLoop2 />);
export const EyeComponent = getDefaultAction(<FaRegEye />);
