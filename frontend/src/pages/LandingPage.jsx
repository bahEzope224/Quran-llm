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
      // Simulation d'envoi (à remplacer par un vrai appel API plus tard)
      setTimeout(() => {
        setSubmitted(false);
        setEmail('');
      }, 5000);
    }
  };

  return (
    <div className="landing-container">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="logo">
          <span className="logo-icon">📖</span>
          <span className="logo-text">ILM AI</span>
        </div>
        <div className="nav-links">
          <Link to="/sign-in" className="nav-btn primary">
            Lancer l'App
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero-section">
        <div className="hero-content">
          <div className="badge-hero">
            ✨ Première IA islamique au monde
          </div>
          
          <h1>
            L’intelligence qui ne parle<br />
            <span className="highlight">que par la preuve.</span>
          </h1>
          
          <p className="hero-subtitle">
            La première IA conçue pour répondre <strong>uniquement</strong> avec le Coran, 
            les Hadiths authentiques et le Tafsir des savants. 
            Zéro hallucination. Zéro interprétation personnelle. 
            <span className="elite-tag">La rigueur doctrinale absolue.</span>
          </p>

          <div className="cta-group">
            <Link to="/sign-up" className="submit-btn hero-cta">
              Commencer gratuitement
            </Link>
            <Link to="/sign-in" className="secondary-btn">
              Voir une démo
            </Link>
          </div>

          <div className="trust-bar">
            <div className="trust-item">
              <span>🛡️</span> Sources vérifiables
            </div>
            <div className="trust-item">
              <span>📖</span> Coran • Hadith • Tafsir
            </div>
            <div className="trust-item">
              <span>✅</span> Validé par la méthodologie islamique
            </div>
          </div>
        </div>

        <div className="hero-image-container">
          <img
            src="/assets/landing-hero.png"
            alt="ILM AI - Assistant Coranique Intelligent"
            className="hero-image"
          />
          <div className="image-overlay">
            <div className="floating-badge">
              Réponse en 3 secondes<br />
              <span className="small">avec références exactes</span>
            </div>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className="features-grid">
        <div className="feature-card">
          <span className="feature-icon">🛡️</span>
          <h3>Confiance Totale</h3>
          <p>
            Si la source n’existe pas dans le Coran ou les Hadiths authentiques, 
            <strong>ILM AI ne l’invente jamais.</strong> 
            La vérité avant tout.
          </p>
        </div>

        <div className="feature-card">
          <span className="feature-icon">📖</span>
          <h3>Sources Vérifiables</h3>
          <p>
            Chaque réponse inclut le <strong>texte arabe original</strong>, 
            sa traduction, la sourate, le numéro du verset et la référence complète. 
            Audit personnel instantané.
          </p>
        </div>

        <div className="feature-card">
          <span className="feature-icon">✨</span>
          <h3>Respect Absolu de la Tradition</h3>
          <p>
            Conçu selon les règles de l’adab islamique et la méthodologie des savants. 
            Une IA qui honore la Sunnah du Prophète ﷺ dans chaque réponse.
          </p>
        </div>
      </section>

      {/* Value Proposition / Mini Testimonial Style */}
      <section className="value-section">
        <div className="value-content">
          <h2>Plus qu’une IA.<br />Un compagnon de savoir pieux.</h2>
          <p>
            Que vous cherchiez une explication de verset, un hadith authentique, 
            un tafsir d’Ibn Kathir ou une réponse sur la vie du Prophète ﷺ, 
            ILM AI vous donne la science authentique, sans filtre et sans détour.
          </p>
        </div>
      </section>

      {/* Waitlist Section */}
      <section className="waitlist-section">
        <div className="waitlist-card">
          <h2>Rejoignez les pionniers de l’intelligence islamique</h2>
          <p>
            Soyez parmi les premiers à tester ILM AI et à recevoir les mises à jour 
            des nouveaux corpus (Tafsir complet, Hadiths Sahih, Fiqh, etc.).
          </p>
          
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
              Recevoir l’accès prioritaire
            </button>
          </form>

          {submitted && (
            <div className="success-msg">
              ✨ Bienvenue dans la communauté des pionniers. 
              Vous êtes désormais en première ligne de la révolution du savoir islamique.
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-links">
          <a href="/privacy">Confidentialité &amp; RGPD</a>
          <a href="/terms">Conditions d’utilisation</a>
          <a href="https://github.com/bahEzope224/Quran-llm" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </div>
        
        <p className="copyright">
          &copy; 2026 ILM AI — La science est une lumière.<br />
          Développé avec ❤️ pour la Oummah par{' '}
          <a href="https://nomad-developer.com" target="_blank" rel="noopener noreferrer">
            Nomad Developer
          </a>
        </p>

        <p className="disclaimer">
          ILM AI n’est pas une fatwa. Toutes les réponses sont générées par intelligence artificielle 
          et doivent être vérifiées auprès de savants qualifiés.
        </p>
      </footer>
    </div>
  );
}