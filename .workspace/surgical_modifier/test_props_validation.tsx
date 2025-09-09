interface ComponentProps {
  title: string;
  count?: number;
  items: string[];
}

const MyComponent: React.FC<ComponentProps> = ({ title, count, items }) => {
  return <div>{title}</div>;
};
