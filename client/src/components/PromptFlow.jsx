import { useState } from "react";

export default function PromptFlow({ step, onNext }) {
  const prompts = [
    "Tell me your story.",
    "What traits define you today?",
    "What repeating patterns do you see?"
  ];

  const [input, setInput] = useState("");

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h2 className="text-xl font-semibold">{prompts[step]}</h2>
      <textarea
        className="w-full mt-4 border p-2"
        rows={5}
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded"
        onClick={() => { onNext(input); setInput(""); }}
      >
        Next
      </button>
    </div>
  );
}
