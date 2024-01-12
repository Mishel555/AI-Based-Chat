import React, { useEffect, useRef } from "react";
import styles from "./style.module.css";

type TextAreaPropsType = {
    assertion: string;
    onChange: Function;
};

const AssertionTextArea = ({ assertion, onChange }: TextAreaPropsType) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const inputHandler = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = "auto";
            textarea.style.height = `${textarea.scrollHeight}px`;
        }
    };

    useEffect(() => {
        inputHandler();
        textareaRef.current?.focus();
    }, []);

    return (
        <textarea
            className={styles.assertion_textarea}
            value={assertion}
            ref={textareaRef}
            rows={1}
            onChange={(e) => onChange(e.target.value)}
            onInput={inputHandler}
        />
    );
};

export default AssertionTextArea;
