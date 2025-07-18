// Mock para archivos SVG
import React from 'react';
const SvgMock = React.forwardRef((props, ref) => {
  return React.createElement('svg', {
    ...props,
    ref,
    'data-testid': 'mocked-svg'
  });
});
SvgMock.displayName = 'SvgMock';
export default SvgMock;
