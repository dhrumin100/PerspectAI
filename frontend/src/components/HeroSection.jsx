import React from 'react';

const HeroSection = ({ onTryChat }) => {
  return (
    <section className="hero-section">
      <div className="hero-content">
        <h1 className="hero-title">
          The World’s <span className="highlight">Conversational Intelligence</span> Engine.
        </h1>
        <p className="hero-subtitle">
          A superfast AI that researches, verifies truth, predicts crises, and analyzes global signals — all in real-time.
        </p>
        <div className="hero-actions">
          <button className="primary-button" onClick={onTryChat}>
            Try the AI
          </button>
        </div>
        <div className="hero-tagline">
          Powered by Agentic Intelligence + Real-Time Web Awareness
        </div>
      </div>
      <div className="hero-background">
        {/* Abstract animated background elements could go here */}
        <div className="glow-orb orb-1"></div>
        <div className="glow-orb orb-2"></div>
      </div>
    </section>
  );
};

export default HeroSection;
