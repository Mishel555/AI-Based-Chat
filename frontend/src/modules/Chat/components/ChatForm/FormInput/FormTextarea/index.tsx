import React, { ChangeEvent, KeyboardEvent, useEffect, useRef } from 'react';
import styles from './style.module.css';

type TextAreaPropsType = {
  value: string;
  onChange: (e: ChangeEvent<HTMLTextAreaElement>) => void;
  onPressEnter: (e: KeyboardEvent) => void;
  placeholder?: string;
  maxLength?: number;
};

const FormTextarea = ({
  value,
  onChange,
  placeholder,
  maxLength = 4096,
  onPressEnter,
}: TextAreaPropsType) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const inputHandler = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      onPressEnter(event);
      inputHandler();
    }
  }

  useEffect(() => {
    inputHandler();
  }, [value]);

  useEffect(() => {
    inputHandler();
    textareaRef.current?.focus();
  }, []);

  return (
    <textarea
      ref={textareaRef}
      value={value}
      rows={1}
      maxLength={maxLength}
      placeholder={placeholder || 'Send a message'}
      className={styles.textarea}
      onChange={(e) => onChange(e)}
      onInput={inputHandler}
      onKeyDown={handleKeyDown}
    />
  );
};

export default FormTextarea;
