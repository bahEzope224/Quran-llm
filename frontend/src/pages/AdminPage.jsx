import { useUser } from '@clerk/react';
import { useEffect, useState } from 'react';
import { Navigate, Link } from 'react-router-dom';
import { 
  LineChart, 
  Line, 
  BarChart,
  Bar,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export default function AdminPage() {
  const { isLoaded, isSignedIn, user } = useUser();
  const [stats, setStats] = useState(null);
  const [feedbacks, setFeedbacks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  // Securite : Seul l'email contact@ibrahima-bah.com peut acceder a cette page
  const isAdmin = user?.primaryEmailAddress?.emailAddress === 'contact@ibrahima-bah.com';

  const [history, setHistory] = useState([]);
  const [selectedResponse, setSelectedResponse] = useState(null);

  useEffect(() => {
    if (!isLoaded || !isSignedIn || !isAdmin) return;

    const fetchData = async () => {
      try {
        const [statsRes, feedbackRes, historyRes] = await Promise.all([
          fetch(`${API_BASE_URL}/admin/stats`),
          fetch(`${API_BASE_URL}/admin/feedbacks`),
          fetch(`${API_BASE_URL}/admin/history`)
        ]);

        if (statsRes.ok) setStats(await statsRes.json());
        if (feedbackRes.ok) setFeedbacks(await feedbackRes.json());
        if (historyRes.ok) setHistory(await historyRes.json());
      } catch (error) {
        console.error('Erreur lors du chargement des donnees admin:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [isLoaded, isSignedIn, isAdmin]);

  const handleDelete = async (timestamp) => {
    if (!window.confirm('Voulez-vous vraiment supprimer ce feedback ?')) return;

    try {
      const res = await fetch(`${API_BASE_URL}/admin/feedback/${timestamp}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        setFeedbacks(prev => prev.filter(f => f.timestamp !== timestamp));
        // Mettre a jour les stats et l'historique localement
        setStats(prev => ({ ...prev, total_feedbacks: prev.total_feedbacks - 1 }));
        setHistory(prev => {
          const date = timestamp.split('T')[0];
          return prev.map(d => d.date === date ? { ...d, up: d.up - 1 } : d);
        });
      }
    } catch (err) {
      console.error('Erreur suppression:', err);
    }
  };

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

      {/* Modal pour voir la reponse complete */}
      {selectedResponse && (
        <div className="admin-modal-overlay" onClick={() => setSelectedResponse(null)}>
          <div className="admin-modal" onClick={e => e.stopPropagation()}>
            <header className="modal-header">
              <h3>Détail de la réponse IA</h3>
              <button onClick={() => setSelectedResponse(null)} className="close-modal">×</button>
            </header>
            <div className="modal-body">
              <p><strong>Question :</strong> {selectedResponse.question}</p>
              <hr />
              <p className="modal-answer-text">{selectedResponse.answer}</p>
            </div>
          </div>
        </div>
      )}

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

          {/* Graphiques d'evolution */}
          <section className="admin-charts-grid">
            <article className="admin-chart-section container-card">
              <h2>Évolution de la Qualité</h2>
              <div className="chart-wrapper" style={{ height: '350px' }}>
                <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                  <LineChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }} 
                      tickFormatter={(val) => new Date(val).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip 
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}
                    />
                    <Legend verticalAlign="top" height={36}/>
                    <Line 
                      type="monotone" 
                      dataKey="up" 
                      name="Preuves Utiles (Up)" 
                      stroke="#3182ce" 
                      strokeWidth={3} 
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="down" 
                      name="Imprécisions (Down)" 
                      stroke="#e53e3e" 
                      strokeWidth={3}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </article>

            <article className="admin-chart-section container-card">
              <h2>Volume des Questions</h2>
              <div className="chart-wrapper" style={{ height: 350 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }} 
                      tickFormatter={(val) => new Date(val).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip 
                      cursor={{fill: '#f9fafb'}}
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}
                    />
                    <Bar 
                      dataKey="total" 
                      name="Nombre de Questions" 
                      fill="#123825" 
                      radius={[6, 6, 0, 0]} 
                      barSize={40}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
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
                    <th>Action</th>
                    <th>Statut</th>
                    <th>Commentaire</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFeedbacks.map((f, idx) => (
                    <tr key={idx}>
                      <td className="col-date">{new Date(f.timestamp).toLocaleDateString()}</td>
                      <td className="col-question">
                        <span title={f.question}>{f.question}</span>
                      </td>
                      <td className="col-view">
                        <button 
                          className="view-answer-btn"
                          onClick={() => setSelectedResponse(f)}
                        >
                          Voir Réponse
                        </button>
                      </td>
                      <td className="col-status">
                        <span className={`status-pill ${f.feedback}`}>
                          {f.feedback === 'up' ? '👍' : '👎'}
                        </span>
                      </td>
                      <td className="col-comment">{f.comment || '-'}</td>
                      <td className="col-delete">
                        <button 
                          className="delete-feedback-btn"
                          onClick={() => handleDelete(f.timestamp)}
                          title="Supprimer ce test"
                        >
                          <span className="material-symbols-outlined">delete</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                  {filteredFeedbacks.length === 0 && (
                    <tr>
                      <td colSpan="6" className="empty-table">Aucun retour trouve.</td>
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
