export default function LoginScreen({ onLogin }) {
  return (
    <div className="centered">
      <h1>REF: Enter Your Depth</h1>
      <button onClick={() => onLogin('login')}>Login</button>
      <button onClick={() => onLogin('create')}>Create Account</button>
    </div>
  );
}
