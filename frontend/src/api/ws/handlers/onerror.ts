import { onErrorLogger } from '../logger';

export const onerror = (logger: onErrorLogger) => (error: Event) => {
  logger.error(error);
};
