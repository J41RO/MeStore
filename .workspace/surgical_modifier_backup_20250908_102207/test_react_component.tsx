import React from 'react';

interface Props {
  name: string;
  value: number;
}

const MyComponent = React.memo((props: Props) => {
  return <div>{props.name}: {props.value}</div>;
});

export default MyComponent;
