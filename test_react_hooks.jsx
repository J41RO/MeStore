import React, { useState, useEffect } from "react";

function MyComponent() {
    const [state, setState] = useState('initial');
    
    useEffect(() => {
        console.log("effect");
    }, [state]);
    
    return <div>{state}</div>;
}
