import React from 'react';
import './App.css';
import HeroSection from './components/HeroSection';
import AboutSection from './components/AboutSection';
import FeaturesSection from './components/FeaturesSection';
import ChatSection from './components/ChatSection';
import DifferentiationSection from './components/DifferentiationSection';
import Footer from './components/Footer';

function App() {
  const handleTryChat = () => {
    const chatSection = document.getElementById('chat-interface');
    chatSection?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="app-container">
      <HeroSection onTryChat={handleTryChat} />
      <AboutSection />
      <FeaturesSection />
      <ChatSection />
      <DifferentiationSection />
      <Footer />
    </div>
  );
}

export default App;
