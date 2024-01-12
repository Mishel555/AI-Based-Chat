import { ChangeEvent, FormEvent, useState } from 'react';
import styles from './style.module.css';

interface IProps {
  defaultValue: string;
  onSubmit: (value: string) => void;
  onCancel: () => void;
}

const MessageForm = ({ defaultValue, onSubmit, onCancel }: IProps) => {
  const [value, setValue] = useState<string>(defaultValue);

  const onFormSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(value);
  };

  const onChange = (e: ChangeEvent<HTMLTextAreaElement>) => setValue(e.target.value);

  return (
    <form onSubmit={onFormSubmit} autoFocus className={styles.root}>
      <textarea value={value} onChange={onChange} className={styles.root__area} />
      <p className={styles.root__notification}>After edit save your all messages will be deleted !</p>
      <div className={styles.root__wrapper}>
        <button type="button" onClick={onCancel} className={styles.root__cancel}>Cancel</button>
        <button type="submit" className={styles.root__submit}>Save</button>
      </div>
    </form>
  );
};

export default MessageForm;
