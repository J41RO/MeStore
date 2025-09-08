import React from 'react';

interface TestProps {
    title: string;
    count: number;
}

const TestComponent: React.FC<TestProps> = ({ title, count }) => {
    return (
        <div>
            <h1>{title}</h1>
            <p>Count: {count}</p>
        </div>
    );
};

export default TestComponent;