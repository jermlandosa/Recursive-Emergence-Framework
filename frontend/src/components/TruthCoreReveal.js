export default function TruthCoreReveal({ truthCore, onAccept, onRefine, onExplore }) {
  return (
    <div className="centered">
      <h2>Your Truth Core has emerged:</h2>
      <blockquote>{truthCore}</blockquote>
      <button onClick={onAccept}>Accept</button>
      <button onClick={onRefine}>Refine</button>
      <button onClick={onExplore}>Explore More</button>
    </div>
  );
}
