import { BiUser } from 'react-icons/all';
import styles from './style.module.css';

const SignIn = () => (
  <a href={`${import.meta.env.VITE_REST_URL}auth/login`} className={styles.root}>
    <BiUser />
    <span>Login with Okta</span>
  </a>
);

export default SignIn;
