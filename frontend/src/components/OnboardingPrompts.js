import { useState } from 'react';

const questions = [
  'Tell me the story of who you are.',
  'What are the personal traits that define you?',
  'What patterns repeat in your life?'
  // Add all 10 questions from the user guide...
];

export default function OnboardingPrompts({ onComplete }) {
  const [step, setStep] = useState(0);
  const [responses, setResponses] = useState([]);

  function handleNext(answer) {
    const updatedResponses = [...responses, answer];
    if (step < questions.length - 1) {
      setResponses(updatedResponses);
      setStep(step + 1);
    } else {
      onComplete(updatedResponses);
    }
  }

  return (
    <div>
      <h3>Question {step + 1} of {questions.length}</h3>
      <p>{questions[step]}</p>
      <textarea onBlur={(e) => handleNext(e.target.value)} />
    </div>
  );
}
