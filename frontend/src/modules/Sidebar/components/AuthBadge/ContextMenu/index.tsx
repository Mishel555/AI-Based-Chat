import classNames from 'classnames';
import { ContextActionType } from '../../../types';
import styles from './style.module.css';

type PropsType = {
  actions: ContextActionType[];
  visible: boolean;
}

const ContextMenu = ({ actions, visible }: PropsType) => (
  <ul className={classNames(styles.root, visible && styles.opened)}>
    {actions.map(({ label, onClick, icon }) => (
      <button key={label} onClick={onClick} className={styles.root__action}>
        {icon}{label}
      </button>
    ))}
  </ul>
);

export default ContextMenu;
