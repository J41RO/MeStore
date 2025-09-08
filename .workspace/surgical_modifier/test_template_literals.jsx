const TestComponent = ({ activated }) => {
  return (
    <div className={`container ${active ? 'active' : 'inactive'}`}>
      <span className={`status-${status}`}>Content</span>
    </div>
  );
};