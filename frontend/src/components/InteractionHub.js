import { useState } from 'react';

export default function InteractionHub({ messages, onSend }) {
  const [input, setInput] = useState('');

  return (
    <div>
      <h2>REF: What would you like to explore today?</h2>
      <div className="chat-feed">
        {messages.map((msg, i) => <div key={i}>{msg}</div>)}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={() => {
        onSend(input);
        setInput('');
      }}>Send</button>
    </div>
  );
}
