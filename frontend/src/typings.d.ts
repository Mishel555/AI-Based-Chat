declare module '*.scss' {
  interface IClassNames {
    [className: string]: string;
  }
  const classNames: IClassNames;
  export = classNames;
}

declare module '*.css' {
  interface IClassNames {
    [className: string]: string;
  }
  const classNames: IClassNames;
  export = classNames;
}

declare module 'uuid' {
  interface IClassNames {
    v4: () => string;
  }
  const uuid: IClassNames;
  export = uuid;
}

declare module '*.webp';
declare module '*.svg';
