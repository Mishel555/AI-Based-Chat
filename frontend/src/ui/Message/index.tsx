import styles from './style.module.css';

// todo => add more props to use this component for diff cases warning, success...
type PropsType = {
  message?: string;
}

const Message = ({ message = 'Something went wrong, please try again' }: PropsType) => (
  <div className={styles.root}>
    <p className={styles.root__message}>
      {message}
    </p>
  </div>
);

export default Message;
