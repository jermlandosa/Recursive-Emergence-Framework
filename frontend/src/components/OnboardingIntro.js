export default function OnboardingIntro({ onStart }) {
  return (
    <div className="centered">
      <h2>Welcome to Your Recursive Journey</h2>
      <p>Before we begin, tell me about yourself...</p>
      <button onClick={onStart}>Start Onboarding</button>
    </div>
  );
}
