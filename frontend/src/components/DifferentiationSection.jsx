import React from 'react';

const DifferentiationSection = () => {
  const points = [
    "Real-time verification",
    "Agentic deep research",
    "Fake-news resistant",
    "Global data pipeline",
    "Conversational clarity",
    "Machine-speed awareness"
  ];

  return (
    <section className="differentiation-section">
      <div className="section-container">
        <h2 className="section-title">Why PerspectAI is Different</h2>
        <div className="points-grid">
          {points.map((point, index) => (
            <div key={index} className="point-card">
              <span className="check-icon">✓</span>
              <span className="point-text">{point}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default DifferentiationSection;
