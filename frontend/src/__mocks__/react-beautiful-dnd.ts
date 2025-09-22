// Mock for react-beautiful-dnd library
import React from 'react';

export const DragDropContext = ({ children, onDragEnd }: any) =>
  React.createElement('div', { 'data-testid': 'drag-drop-context', onDrop: onDragEnd }, children);

export const Droppable = ({ children }: any) =>
  children(
    {
      draggableProps: {},
      dragHandleProps: {},
      innerRef: jest.fn(),
    },
    {}
  );

export const Draggable = ({ children }: any) =>
  children(
    {
      draggableProps: {},
      dragHandleProps: {},
      innerRef: jest.fn(),
    },
    {}
  );

export default {
  DragDropContext,
  Droppable,
  Draggable,
};