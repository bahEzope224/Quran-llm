import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/react';
import { Navigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import KanbanBoard from '../components/KanbanBoard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export default function ManagementPage() {
  const { isLoaded, isSignedIn, getToken } = useAuth();
  const [activeTab, setActiveTab] = useState('features');
  const [features, setFeatures] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showFeatureModal, setShowFeatureModal] = useState(false);
  const [editingFeature, setEditingFeature] = useState(null);
  
  const [newFeature, setNewFeature] = useState({
    title: '',
    description: '',
    priority: 'Moyenne',
    status: 'À implémenter'
  });

  useEffect(() => {
    if (isSignedIn) {
      fetchFeatures();
    }
  }, [isSignedIn]);

  async function fetchFeatures() {
    try {
      const token = await getToken();
      const response = await fetch(`${API_BASE_URL}/management/features`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setFeatures(data);
      }
    } catch (error) {
      console.error("Erreur lors du chargement des features:", error);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSaveFeature() {
    try {
      const token = await getToken();
      const method = editingFeature ? 'PATCH' : 'POST';
      const url = editingFeature 
        ? `${API_BASE_URL}/management/features/${editingFeature.id}`
        : `${API_BASE_URL}/management/features`;

      const response = await fetch(url, {
        method,
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newFeature)
      });

      if (response.ok) {
        fetchFeatures();
        setShowFeatureModal(false);
        setNewFeature({ title: '', description: '', priority: 'Moyenne', status: 'À implémenter' });
        setEditingFeature(null);
      }
    } catch (error) {
      console.error("Erreur lors de la sauvegarde:", error);
    }
  }

  async function handleDeleteFeature(id) {
    if (!confirm("Supprimer cette fonctionnalité ?")) return;
    try {
      const token = await getToken();
      await fetch(`${API_BASE_URL}/management/features/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchFeatures();
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
    }
  }

  if (!isLoaded) return <div className="p-8 text-center text-slate-500">Chargement...</div>;
  if (!isSignedIn) return <Navigate to="/sign-in" replace />;

  const priorityColors = {
    'Haute': 'bg-rose-100 text-rose-700 border-rose-200',
    'Moyenne': 'bg-amber-100 text-amber-700 border-amber-200',
    'Basse': 'bg-emerald-100 text-emerald-700 border-emerald-200'
  };

  return (
    <div className="min-h-screen bg-[#f8faf9] text-slate-900 font-sans">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="p-2 hover:bg-slate-100 rounded-xl transition-colors">
              <span className="material-symbols-outlined text-slate-600">arrow_back</span>
            </Link>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900 leading-none mb-1">Centre de Gestion</h1>
              <p className="text-xs font-semibold uppercase tracking-widest text-emerald-600">ILM AI Infrastructure</p>
            </div>
          </div>
          
          <nav className="flex bg-slate-100 p-1 rounded-xl">
            <button 
              onClick={() => setActiveTab('features')}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'features' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Fonctionnalités
            </button>
            <button 
              onClick={() => setActiveTab('kanban')}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'kanban' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Kanban
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        <AnimatePresence mode="wait">
          {activeTab === 'features' ? (
            <motion.div 
              key="features-tab"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-black text-slate-900">Roadmap des Features</h2>
                  <p className="text-slate-500">Planifiez et priorisez les prochaines évolutions du modèle.</p>
                </div>
                <button 
                  onClick={() => { setEditingFeature(null); setShowFeatureModal(true); }}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
                >
                  <span className="material-symbols-outlined text-lg">add</span>
                  Ajouter une Feature
                </button>
              </div>

              {isLoading ? (
                <div className="py-20 text-center text-slate-400 font-medium">Récupération des données...</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {features.map((feature) => (
                    <motion.article 
                      key={feature.id}
                      layoutId={feature.id}
                      className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border ${priorityColors[feature.priority]}`}>
                          {feature.priority}
                        </span>
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button 
                            onClick={() => {
                              setEditingFeature(feature);
                              setNewFeature(feature);
                              setShowFeatureModal(true);
                            }}
                            className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-emerald-600"
                          >
                            <span className="material-symbols-outlined text-lg">edit</span>
                          </button>
                          <button 
                            onClick={() => handleDeleteFeature(feature.id)}
                            className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-rose-600"
                          >
                            <span className="material-symbols-outlined text-lg">delete</span>
                          </button>
                        </div>
                      </div>
                      
                      <h3 className="text-lg font-bold text-slate-900 mb-2 leading-tight">{feature.title}</h3>
                      <p className="text-sm text-slate-500 line-clamp-3 mb-6">{feature.description || 'Aucune description.'}</p>
                      
                      <div className="flex items-center justify-between pt-4 border-top border-slate-50">
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            feature.status === 'Déployée' ? 'bg-emerald-500' : 
                            feature.status === 'En cours' ? 'bg-amber-500' : 'bg-slate-300'
                          }`} />
                          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-tighter">{feature.status}</span>
                        </div>
                      </div>
                    </motion.article>
                  ))}
                  
                  {features.length === 0 && (
                    <div className="col-span-full py-20 text-center bg-white border-2 border-dashed border-slate-200 rounded-3xl">
                      <p className="text-slate-400 font-medium">Aucune fonctionnalité planifiée pour le moment.</p>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div 
              key="kanban-tab"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <KanbanBoard />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Modal Feature */}
      <AnimatePresence>
        {showFeatureModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowFeatureModal(false)}
              className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative bg-white rounded-[32px] w-full max-w-lg p-8 shadow-2xl"
            >
              <h3 className="text-2xl font-black mb-6">{editingFeature ? 'Modifier la Feature' : 'Nouvelle Feature'}</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Titre</label>
                  <input 
                    type="text" 
                    value={newFeature.title}
                    onChange={(e) => setNewFeature({...newFeature, title: e.target.value})}
                    placeholder="ex: Reranking Cross-Encoder"
                    className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Description</label>
                  <textarea 
                    value={newFeature.description}
                    onChange={(e) => setNewFeature({...newFeature, description: e.target.value})}
                    placeholder="Détails de l'implémentation..."
                    rows={4}
                    className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none resize-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Priorité</label>
                    <select 
                      value={newFeature.priority}
                      onChange={(e) => setNewFeature({...newFeature, priority: e.target.value})}
                      className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none appearance-none cursor-pointer"
                    >
                      <option value="Haute">🔴 Haute</option>
                      <option value="Moyenne">🟡 Moyenne</option>
                      <option value="Basse">🟢 Basse</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Statut</label>
                    <select 
                      value={newFeature.status}
                      onChange={(e) => setNewFeature({...newFeature, status: e.target.value})}
                      className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none appearance-none cursor-pointer"
                    >
                      <option value="À implémenter">⏳ À implémenter</option>
                      <option value="En cours">⚡ En cours</option>
                      <option value="Déployée">🚀 Déployée</option>
                    </select>
                  </div>
                </div>
                
                <div className="flex gap-3 pt-6">
                  <button 
                    onClick={() => setShowFeatureModal(false)}
                    className="flex-1 py-3.5 rounded-2xl font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
                  >
                    Annuler
                  </button>
                  <button 
                    onClick={handleSaveFeature}
                    disabled={!newFeature.title.trim()}
                    className="flex-[2] py-3.5 rounded-2xl font-bold bg-emerald-600 text-white hover:bg-emerald-700 shadow-lg shadow-emerald-600/20 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100"
                  >
                    {editingFeature ? 'Mettre à jour' : 'Créer la Feature'}
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
