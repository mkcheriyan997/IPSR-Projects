import React, { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(setData);
  }, []);

  return (
    <div>
      <h1>Multi-Service App</h1>
      {data ? <p>{data.message} - Time: {data.time}</p> : <p>Loading...</p>}
    </div>
  );
}

export default App;
