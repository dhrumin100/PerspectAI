import React from 'react';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-content">
        <div className="footer-brand">
          <h3>PerspectAI</h3>
          <p>The World’s Conversational Intelligence Engine</p>
        </div>
        <div className="footer-links">
          <div className="link-group">
            <h4>Connect</h4>
            <a href="#">Twitter</a>
            <a href="#">LinkedIn</a>
            <a href="#">Email</a>
          </div>
          <div className="link-group">
            <h4>Legal</h4>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        &copy; {new Date().getFullYear()} PerspectAI. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
