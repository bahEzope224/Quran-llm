import { useUser } from '@clerk/react';
import { useEffect, useState } from 'react';
import { Navigate, Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export default function AdminPage() {
  const { isLoaded, isSignedIn, user } = useUser();
  const [stats, setStats] = useState(null);
  const [feedbacks, setFeedbacks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  // Securite : Seul l'email contact@ibrahima-bah.com peut acceder a cette page
  const isAdmin = user?.primaryEmailAddress?.emailAddress === 'contact@ibrahima-bah.com';

  useEffect(() => {
    if (!isLoaded || !isSignedIn || !isAdmin) return;

    const fetchData = async () => {
      try {
        const [statsRes, feedbackRes] = await Promise.all([
          fetch(`${API_BASE_URL}/admin/stats`),
          fetch(`${API_BASE_URL}/admin/feedbacks`)
        ]);

        if (statsRes.ok) setStats(await statsRes.json());
        if (feedbackRes.ok) setFeedbacks(await feedbackRes.json());
      } catch (error) {
        console.error('Erreur lors du chargement des donnees admin:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [isLoaded, isSignedIn, isAdmin]);

  if (!isLoaded) return <div className="app-loading">Chargement...</div>;
  if (!isSignedIn || !isAdmin) return <Navigate to="/" replace />;

  const filteredFeedbacks = feedbacks.filter(f => 
    filter === 'all' ? true : f.feedback === filter
  );

  return (
    <main className="admin-container">
      <header className="admin-header">
        <div className="admin-header-content">
          <h1>Tableau de Bord Admin</h1>
          <p className="admin-subtitle">Gestion des feedbacks et performance RAG</p>
        </div>
        <Link to="/" className="back-to-chat">
          <span className="material-symbols-outlined">arrow_back</span>
          Retour au Chat
        </Link>
      </header>

      {isLoading ? (
        <div className="admin-loading-state">Initialisation des donnees...</div>
      ) : (
        <div className="admin-content">
          {/* Stats Cards */}
          <section className="stats-grid">
            <article className="stat-card">
              <span className="stat-label">Total Feedbacks</span>
              <span className="stat-value">{stats?.total_feedbacks || 0}</span>
            </article>
            <article className="stat-card">
              <span className="stat-label">Taux de precision</span>
              <span className="stat-value">{stats?.success_rate?.toFixed(1) || 0}%</span>
            </article>
            <article className="stat-card highlight">
              <span className="stat-label">Utiles (👍)</span>
              <span className="stat-value">{stats?.helpful_count || 0}</span>
            </article>
            <article className="stat-card warning">
              <span className="stat-label">Imprecis (👎)</span>
              <span className="stat-value">{stats?.unclear_count || 0}</span>
            </article>
          </section>

          {/* Feedback List */}
          <section className="feedback-section container-card">
            <header className="section-header">
              <h2>Retours Utilisateurs</h2>
              <div className="filter-tabs">
                <button 
                  className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                  onClick={() => setFilter('all')}
                >
                  Tous
                </button>
                <button 
                  className={`filter-btn ${filter === 'up' ? 'active' : ''}`}
                  onClick={() => setFilter('up')}
                >
                  Utiles
                </button>
                <button 
                  className={`filter-btn ${filter === 'down' ? 'active' : ''}`}
                  onClick={() => setFilter('down')}
                >
                  Imprecis
                </button>
              </div>
            </header>

            <div className="feedback-table-wrapper">
              <table className="feedback-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Question</th>
                    <th>Statut</th>
                    <th>Commentaire</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFeedbacks.map((f, idx) => (
                    <tr key={idx}>
                      <td className="col-date">{new Date(f.timestamp).toLocaleDateString()}</td>
                      <td className="col-question">
                        <span title={f.question}>{f.question}</span>
                      </td>
                      <td className="col-status">
                        <span className={`status-pill ${f.feedback}`}>
                          {f.feedback === 'up' ? '👍' : '👎'}
                        </span>
                      </td>
                      <td className="col-comment">{f.comment || '-'}</td>
                    </tr>
                  ))}
                  {filteredFeedbacks.length === 0 && (
                    <tr>
                      <td colSpan="4" className="empty-table">Aucun retour trouve.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
