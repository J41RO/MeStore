import React from 'react';

const ValidComponent = React.memo((props) => {
  return <div>{props.message}</div>;
});

export default ValidComponent;
