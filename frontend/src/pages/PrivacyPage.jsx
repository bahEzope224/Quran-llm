import React from 'react';

export default function PrivacyPage() {
  return (
    <main style={{ padding: '4rem 5%', maxWidth: '800px', margin: '0 auto', color: '#f8fafc', backgroundColor: '#0f172a', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '2rem', color: '#10b981' }}>Politique de Confidentialité</h1>
      <p style={{ color: '#94a3b8', marginBottom: '2rem' }}>Dernière mise à jour : 2 avril 2026</p>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ color: '#f59e0b', marginBottom: '1rem' }}>1. Collecte de données</h2>
        <p style={{ lineHeight: '1.6' }}>Nous ne recueillons pas de données personnelles identifiables (PII) lors de vos interactions avec l'IA. Les discussions sont recueillies de façon strictement anonyme pour améliorer la précision du modèle.</p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ color: '#f59e0b', marginBottom: '1rem' }}>2. Utilisation des données</h2>
        <p style={{ lineHeight: '1.6' }}>Les contenus anonymisés servent exclusivement à réduire les erreurs doctrinales et à enrichir la base de connaissances de ILM AI.</p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ color: '#f59e0b', marginBottom: '1rem' }}>3. Vos Droits</h2>
        <p style={{ lineHeight: '1.6' }}>Conformément au RGPD, vous disposez d'un droit d'accès et d'effacement de vos informations de compte. Les logs de chat, étant anonymisés, ne sont plus rattachés à votre identité.</p>
      </section>

      <footer style={{ marginTop: '4rem', paddingTop: '2rem', borderTop: '1px solid #1e293b', textAlign: 'center' }}>
        <a href="/landing" style={{ color: '#10b981', textDecoration: 'none' }}>Retour à l'accueil</a>
      </footer>
    </main>
  );
}
