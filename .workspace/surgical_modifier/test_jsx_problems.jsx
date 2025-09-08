const Component = () => {
  return (
    <div>
      {condition && 
      <span>Incomplete conditional</span>
      <div>
        <p>Unclosed fragment
      </div>
      {items.map(item => 
        <li>Item without closing
      )}
    </div>
  );
};
