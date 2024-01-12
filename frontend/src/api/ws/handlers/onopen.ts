import { onOpenLogger } from '../logger';

export const onopen = (logger: onOpenLogger) => () => logger.openConnection();
