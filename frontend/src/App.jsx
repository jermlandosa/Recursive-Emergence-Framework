import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import LoginScreen from './components/LoginScreen';
import OnboardingIntro from './components/OnboardingIntro';
import OnboardingPrompts from './components/OnboardingPrompts';
import InteractionHub from './components/InteractionHub';
import TruthCoreReveal from './components/TruthCoreReveal';
import MetaLayerView from './components/MetaLayerView';
import InfoSidebar from './components/InfoSidebar';

export default function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

function AppRoutes() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);

  const handleLogin = () => navigate('/intro');
  const handleStart = () => navigate('/onboarding');
  const handleComplete = (responses) => {
    // In a real app responses would be saved
    navigate('/interaction');
  };
  const handleSend = (msg) => {
    if (msg) {
      setMessages([...messages, msg]);
    }
  };
  const handleAccept = () => navigate('/meta-layer');
  const handleRefine = () => navigate('/interaction');
  const handleExplore = () => navigate('/interaction');
  const handleBack = () => navigate('/interaction');

  return (
    <Routes>
      <Route path="/" element={<LoginScreen onLogin={handleLogin} />} />
      <Route path="/intro" element={<OnboardingIntro onStart={handleStart} />} />
      <Route path="/onboarding" element={<OnboardingPrompts onComplete={handleComplete} />} />
      <Route path="/interaction" element={<InteractionHub messages={messages} onSend={handleSend} />} />
      <Route path="/truth-core" element={<TruthCoreReveal truthCore="" onAccept={handleAccept} onRefine={handleRefine} onExplore={handleExplore} />} />
      <Route path="/meta-layer" element={<MetaLayerView trail={messages} onBack={handleBack} />} />
      <Route path="/learn" element={<InfoSidebar />} />
    </Routes>
  );
}
