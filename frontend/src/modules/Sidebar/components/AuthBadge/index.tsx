import { useAuthStore } from '~/store';
import UserDetails from './UserDetails';
import SignIn from './SignIn';
import styles from './style.module.css';

const AuthBadge = () => {
  const user = useAuthStore(state => state.user);

  return (
    <div className={styles.root}>
      {user ? <UserDetails data={user} /> : <SignIn />}
    </div>
  );
};

export default AuthBadge;
