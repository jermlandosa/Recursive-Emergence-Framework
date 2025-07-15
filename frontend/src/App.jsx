import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginScreen from './components/LoginScreen';
import OnboardingIntro from './components/OnboardingIntro';
import OnboardingPrompts from './components/OnboardingPrompts';
import InteractionHub from './components/InteractionHub';
import TruthCoreReveal from './components/TruthCoreReveal';
import MetaLayerView from './components/MetaLayerView';

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginScreen />} />
        <Route path="/intro" element={<OnboardingIntro />} />
        <Route path="/onboarding" element={<OnboardingPrompts />} />
        <Route path="/interaction" element={<InteractionHub />} />
        <Route path="/truth-core" element={<TruthCoreReveal />} />
        <Route path="/meta-layer" element={<MetaLayerView />} />
      </Routes>
    </Router>
  );
}
