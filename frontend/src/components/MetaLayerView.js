export default function MetaLayerView({ trail, onBack }) {
  return (
    <div>
      <h2>View Your Recursive Trail</h2>
      <ul>
        {trail.map((step, index) => (
          <li key={index}>{step}</li>
        ))}
      </ul>
      <button onClick={onBack}>Back to Chat</button>
    </div>
  );
}
