import { InputActionType } from '../../../types';
import styles from './style.module.css';

type PropsType = {
  actions: InputActionType[];
}

const InputActions = ({ actions }: PropsType) => (
  <ul className={styles.root}>
    {actions.map(({ label, action }, index) => (
      <li key={index} onClick={action} className={styles.root__button}>{label}</li>
    ))}
  </ul>
);

export default InputActions;
