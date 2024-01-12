import { ReactNode } from 'react';

export type ContextActionType = {
  label: string;
  icon: ReactNode;
  onClick: () => void;
}
