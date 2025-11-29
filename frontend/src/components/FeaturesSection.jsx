import React from 'react';

const FeaturesSection = () => {
  const features = [
    {
      title: "Rapid Intelligence",
      tagline: "Instant answers. Real-time facts. Fast clarity.",
      description: "Rapid Intelligence is your fast mode — the AI responds instantly, pulling verified context from your vector database and live web sources. It feels like a normal AI chat, but every answer is rooted in real information, not guesses.",
      icon: "⚡"
    },
    {
      title: "Deep Research",
      tagline: "Multi-agent deep analysis when you need complete understanding.",
      description: "Deep Research activates your 9-agent pipeline. It performs parallel research, finds contradictions, checks credibility, and produces synthesized insights. For complex queries and long-term analysis.",
      icon: "🧠"
    },
    {
      title: "Crisis Prediction",
      tagline: "24/7 monitoring of global signals.",
      description: "PerspectAI continuously scans data from trusted sources, government feeds, and global media. It creates early warning signals and real-time situation awareness. Your global intelligence layer.",
      icon: "🌍"
    },
    {
      title: "Sim2Sim Conversations",
      tagline: "Experience AI-to-AI conversations like never before.",
      description: "Watch two intelligent agents talk to each other — similar to debates — but with real-time data integration. Explore opposing perspectives and understand complex topics clearly.",
      icon: "🤖"
    }
  ];

  return (
    <section className="features-section">
      <div className="section-container">
        <h2 className="section-title">Core Capabilities</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-tagline">{feature.tagline}</p>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
