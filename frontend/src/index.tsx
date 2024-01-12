import { Fragment } from 'react';
import { createRoot } from 'react-dom/client';
import { ToastContainer } from 'react-toastify';
import { init } from '~/utils/initializeApplication';
import App from './App';

import 'react-tooltip/dist/react-tooltip.css';
import 'react-toastify/dist/ReactToastify.css';
import './styles/main.css';

const container = document.getElementById('root');
const root = createRoot(container as Element);

init();

root.render(
  <Fragment>
    <App />
    <ToastContainer
      pauseOnHover={false}
      hideProgressBar
      pauseOnFocusLoss={false}
      draggable={false}
      autoClose={500}
      limit={1}
      position="top-center"
      theme="dark"
    />
  </Fragment>
);
