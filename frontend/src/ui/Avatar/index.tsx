import classNames from 'classnames';
import styles from './style.module.css';

type PropsType = {
  src: string;
  size?: number;
  className?: string;
}

const Avatar = ({ src, className, size = 30 }: PropsType) => (
  <img
    src={src}
    alt="avatar"
    style={{ width: size, height: size }}
    className={classNames(styles.root, className)}
  />
);

export default Avatar;
