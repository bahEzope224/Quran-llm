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
      setTimeout(() => setSubmitted(false), 6000);
      setEmail('');
    }
  };

  return (
    <div className="landing-container">

      {/* Navigation */}
      <nav className="landing-nav">
        <Link to="/" style={{ textDecoration: 'none' }}>
          <div className="logo-text">ILM AI</div>
        </Link>
        <Link to="/sign-in" className="nav-btn">Commencer</Link>
      </nav>

      {/* Hero */}
      <header className="hero-section">
        <div className="hero-eyebrow">
          <span className="eyebrow-line" />
          Connaissance islamique · Preuve textuelle
          <span className="eyebrow-line" />
        </div>

        <h1 className="hero-title">
          Chaque réponse<br />
          commence par <em>une source.</em>
        </h1>

        <p className="hero-sub">
          ILM AI ne spécule pas. Pour chaque question, une référence : verset, hadith,
          citation de savant — avec le texte arabe original et sa traduction exacte.
        </p>

        <div className="hero-actions">
          <Link to="/sign-up" className="btn-primary" style={{ textDecoration: 'none' }}>
            Essayer gratuitement
          </Link>
          <a href="#features" className="btn-ghost">Voir comment ça fonctionne</a>
        </div>

        <div className="arabic-watermark" aria-hidden="true">علم</div>
      </header>

      {/* Proof Bar */}
      <div className="proof-bar">
        <div className="proof-item">
          <span className="proof-num">6 236</span>
          <span className="proof-label">versets du Coran indexés</span>
        </div>
        <div className="proof-divider" />
        <div className="proof-item">
          <span className="proof-num">7 275</span>
          <span className="proof-label">hadiths Sahih Bukhari &amp; Muslim</span>
        </div>
        <div className="proof-divider" />
        <div className="proof-item">
          <span className="proof-num">0</span>
          <span className="proof-label">réponse sans source vérifiable</span>
        </div>
        <div className="proof-divider" />
        <div className="proof-item">
          <span className="proof-num">4</span>
          <span className="proof-label">madhabs représentés</span>
        </div>
      </div>

      {/* Features */}
      <section className="features-section" id="features">
        <div className="features-header">
          <div>
            <p className="section-label">Ce qui nous différencie</p>
            <h2 className="features-title">
              La rigueur des <em>oulémas,</em><br />
              la rapidité du numérique.
            </h2>
          </div>
          <p className="features-desc">
            Les grandes questions méritent des réponses ancrées dans la tradition.
            Pas des approximations, pas des compromis. ILM AI a été conçu pour ne jamais
            transiger avec l'exactitude doctrinale.
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-num">01</div>
            <h3>La source d'abord, toujours</h3>
            <p>
              Chaque réponse est générée à partir du texte — pas depuis une base de
              probabilités. Si le texte ne parle pas, ILM AI se tait. C'est une règle,
              pas une promesse.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-num">02</div>
            <h3>Arabe original inclus</h3>
            <p>
              Sourate, numéro de verset, nom du savant, date de sa fatwa. Vous recevez
              ce qu'il faut pour vérifier vous-même — sans dépendre d'un intermédiaire.
            </p>
          </div>
          <div className="feature-card">
            <div className="feature-num">03</div>
            <h3>Le protocole prophétique respecté</h3>
            <p>
              Les formules de respect, les noms, les titres — rien n'est abrégé par
              commodité. La tradition muhammadienne ﷺ est honorée dans chaque ligne générée.
            </p>
          </div>
        </div>
      </section>

      {/* Hadith Quote */}
      <section className="quote-section">
        <p className="arabic-quote">طَلَبُ الْعِلْمِ فَرِيضَةٌ عَلَى كُلِّ مُسْلِمٍ</p>
        <p className="quote-translation">
          "La quête de la connaissance est une obligation pour tout musulman."
        </p>
        <p className="quote-source">Hadith — Ibn Mâja, n°224 · Grade : Hassan</p>
      </section>

      {/* Waitlist */}
      <section className="waitlist-section">
        <p className="section-label">Accès anticipé</p>
        <h2 className="waitlist-title">Rejoignez la liste d'attente</h2>
        <p className="waitlist-sub">
          Nous intégrons chaque mois de nouveaux corpus : Tafsir Ibn Kathir complet,
          Fiqh comparé, Sirah. Soyez informé en avant-première.
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
          <button type="submit" className="submit-btn">S'inscrire</button>
        </form>
        <p className="waitlist-note">Sans spam. Désabonnement en un clic.</p>
        {submitted && (
          <p className="success-msg">Bienvenue. Vous serez parmi les premiers informés.</p>
        )}
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-logo">ILM AI</div>
        <div className="footer-links">
          <a href="/privacy">Confidentialité &amp; RGPD</a>
          <a href="#">Conditions d'utilisation</a>
          <a
            href="https://nomad-developer.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            Nomad Developer
          </a>
        </div>
        <span className="footer-copy">© 2026 ILM AI · La science est une lumière.</span>
      </footer>

    </div>
  );
}