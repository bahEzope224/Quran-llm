import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

export default function LandingPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email) {
      setSubmitted(true);
      // Simulation d'envoi vers un backend
      setTimeout(() => setSubmitted(false), 5000);
      setEmail('');
    }
  };

  return (
    <div className="landing-container">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="logo-text">ILM AI</div>
        <div className="nav-links">
          <Link to="/sign-in" className="nav-btn">Lancer l'App</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero-section">
        <div className="hero-content">
          <h1>L'Élite de l'Intelligence Islamique.</h1>
          <p>
            Découvrez la première IA au monde qui ne répond que par la preuve. 
            Une rigueur doctrinale absolue, sourcée depuis le Coran, le Hadith et le Tafsir.
          </p>
          <div className="cta-group">
            <Link to="/sign-up" className="submit-btn" style={{ textDecoration: 'none', display: 'inline-block' }}>
              Commencer gratuitement
            </Link>
          </div>
        </div>
        <div className="hero-image-container">
          <img 
            src="/assets/landing-hero.png" 
            alt="ILM AI Visualization" 
            className="hero-image"
          />
        </div>
      </header>

      {/* Features Section */}
      <section className="features-grid">
        <div className="feature-card">
          <span className="feature-icon">🛡️</span>
          <h3>Confiance Totale</h3>
          <p>Zéro hallucination. Si la source n'existe pas, ILM AI ne l'invente pas. La vérité avant tout.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">📖</span>
          <h3>Sources Vérifiables</h3>
          <p>Chaque réponse est accompagnée de son texte original et de sa référence exacte pour votre audit personnel.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">✨</span>
          <h3>Respect Absolu</h3>
          <p>Une intelligence conçue pour respecter les sensibilités et les protocoles de la tradition mohammadienne (PBSL).</p>
        </div>
      </section>

      {/* Waitlist Section */}
      <section className="waitlist-section">
        <div className="waitlist-card">
          <h2>Rejoignez la révolution ILM AI</h2>
          <p>Soyez les premiers informés de nos mises à jour majeures et des nouveaux corpus savants intégrés.</p>
          
          <form className="waitlist-form" onSubmit={handleSubmit}>
            <input 
              type="email" 
              className="waitlist-input" 
              placeholder="votre@email.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit" className="submit-btn">
              S'inscrire
            </button>
          </form>

          {submitted && (
            <div className="success-msg">
              ✨ Bienvenue dans la communauté ILM AI. À très bientôt !
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ textAlign: 'center', padding: '3rem', borderTop: '1px solid rgba(255,255,255,0.05)', color: '#64748b' }}>
        © 2024 ILM AI. La science est une lumière.
      </footer>
    </div>
  );
}
