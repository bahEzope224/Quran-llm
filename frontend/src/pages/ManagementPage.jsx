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
      console.error("Erreur features:", error);
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
      console.error("Save feature error:", error);
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
      console.error("Delete feature error:", error);
    }
  }

  if (!isLoaded) return <div className="flex items-center justify-center min-vh-100 text-slate-400 font-medium">Initialisation...</div>;
  if (!isSignedIn) return <Navigate to="/sign-in" replace />;

  const priorityStyles = {
    'Haute': 'bg-rose-50 text-rose-600 border-rose-100',
    'Moyenne': 'bg-amber-50 text-amber-600 border-amber-100',
    'Basse': 'bg-emerald-50 text-emerald-600 border-emerald-100'
  };

  return (
    <div className="min-h-screen bg-[#fcfdfc] text-slate-900 selection:bg-emerald-100">
      {/* Background Decor */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-50/50 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-50/50 rounded-full blur-[120px]" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/70 backdrop-blur-xl border-b border-slate-200/50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-5">
            <Link to="/" className="group flex items-center justify-center w-10 h-10 rounded-full hover:bg-slate-100/80 transition-all duration-300">
              <span className="material-symbols-outlined text-slate-500 group-hover:text-emerald-600 transition-colors">arrow_back</span>
            </Link>
            <div>
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xl font-black tracking-tight text-slate-800">Gestion</span>
                <span className="px-2 py-0.5 bg-emerald-600 text-[10px] font-black text-white rounded-md tracking-tighter uppercase">Admin</span>
              </div>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest leading-none">ILM AI Infrastructure</p>
            </div>
          </div>
          
          <nav className="flex items-center bg-slate-100/50 p-1 rounded-2xl border border-slate-200/40">
            <button 
              onClick={() => setActiveTab('features')}
              className={`px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300 ${activeTab === 'features' ? 'bg-white text-emerald-700 shadow-[0_4px_12px_rgba(0,0,0,0.05)]' : 'text-slate-400 hover:text-slate-600'}`}
            >
              Roadmap
            </button>
            <button 
              onClick={() => setActiveTab('kanban')}
              className={`px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300 ${activeTab === 'kanban' ? 'bg-white text-emerald-700 shadow-[0_4px_12px_rgba(0,0,0,0.05)]' : 'text-slate-400 hover:text-slate-600'}`}
            >
              Kanban
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <AnimatePresence mode="wait">
          {activeTab === 'features' ? (
            <motion.div 
              key="features-tab"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.02 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-10"
            >
              <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="max-w-xl">
                  <h2 className="text-4xl font-black text-slate-900 tracking-tight mb-3">Roadmap Évolutive</h2>
                  <p className="text-slate-500 font-medium leading-relaxed">
                    Priorisez et planifiez les prochaines capacités du modèle ILM AI. 
                    Chaque feature assure l&apos;alignement avec les valeurs éthiques et religieuses.
                  </p>
                </div>
                <button 
                  onClick={() => { setEditingFeature(null); setShowFeatureModal(true); }}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white min-h-[52px] px-8 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center gap-3 shadow-[0_12px_24px_rgba(5,150,105,0.2)] transition-all duration-300 hover:scale-[1.03] active:scale-[0.97]"
                >
                  <span className="material-symbols-outlined text-lg">add_circle</span>
                  Nouveau Projet
                </button>
              </div>

              {isLoading ? (
                <div className="py-32 flex flex-col items-center justify-center text-slate-300">
                  <div className="w-12 h-12 border-4 border-slate-100 border-t-emerald-500 rounded-full animate-spin mb-4" />
                  <p className="font-bold uppercase tracking-widest text-[10px]">Synchronisation...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {features.map((feature) => (
                    <motion.article 
                      key={feature.id}
                      layout
                      className="group bg-white border border-slate-200/60 rounded-[32px] p-8 shadow-[0_8px_30px_rgb(0,0,0,0.02)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] transition-all duration-500 relative flex flex-col"
                    >
                      <div className="flex items-center justify-between mb-6">
                        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider border ${priorityStyles[feature.priority]}`}>
                          {feature.priority}
                        </span>
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0">
                          <button 
                            onClick={() => {
                              setEditingFeature(feature);
                              setNewFeature(feature);
                              setShowFeatureModal(true);
                            }}
                            className="w-9 h-9 flex items-center justify-center hover:bg-slate-50 rounded-full text-slate-400 hover:text-emerald-600 transition-colors"
                          >
                            <span className="material-symbols-outlined text-xl">edit_note</span>
                          </button>
                          <button 
                            onClick={() => handleDeleteFeature(feature.id)}
                            className="w-9 h-9 flex items-center justify-center hover:bg-rose-50 rounded-full text-slate-400 hover:text-rose-600 transition-colors"
                          >
                            <span className="material-symbols-outlined text-xl">delete</span>
                          </button>
                        </div>
                      </div>
                      
                      <h3 className="text-xl font-black text-slate-900 mb-3 leading-tight tracking-tight">{feature.title}</h3>
                      <p className="text-sm text-slate-500 font-medium leading-relaxed line-clamp-4 flex-grow mb-8">{feature.description || 'Aucune documentation disponible.'}</p>
                      
                      <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.1)] ${
                            feature.status === 'Déployée' ? 'bg-emerald-500 shadow-emerald-500/40' : 
                            feature.status === 'En cours' ? 'bg-amber-500 shadow-amber-500/40' : 'bg-slate-300'
                          }`} />
                          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{feature.status}</span>
                        </div>
                        <span className="text-[10px] font-bold text-slate-300">ID: {feature.id.slice(0, 8)}</span>
                      </div>
                    </motion.article>
                  ))}
                  
                  {features.length === 0 && (
                    <div className="col-span-full py-24 text-center bg-slate-50/50 border-2 border-dashed border-slate-200/60 rounded-[40px]">
                      <span className="material-symbols-outlined text-4xl text-slate-300 mb-4 block">inventory_2</span>
                      <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Le carnet est vide pour le moment</p>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div 
              key="kanban-tab"
              initial={{ opacity: 0, filter: 'blur(10px)' }}
              animate={{ opacity: 1, filter: 'blur(0px)' }}
              exit={{ opacity: 0, filter: 'blur(10px)' }}
              transition={{ duration: 0.4 }}
            >
              <KanbanBoard />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Modal Feature */}
      <AnimatePresence>
        {showFeatureModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowFeatureModal(false)}
              className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="relative bg-white rounded-[40px] w-full max-w-xl p-10 shadow-[0_40px_80px_rgba(0,0,0,0.25)]"
            >
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h3 className="text-3xl font-black tracking-tight">{editingFeature ? 'Modifier l&apos;entrée' : 'Nouveau Projet'}</h3>
                  <p className="text-slate-400 text-sm font-medium">Définissez les détails et les priorités.</p>
                </div>
                <button onClick={() => setShowFeatureModal(false)} className="w-10 h-10 flex items-center justify-center hover:bg-slate-100 rounded-full text-slate-400 transition-colors">
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">Titre du projet</label>
                  <input 
                    type="text" 
                    value={newFeature.title}
                    onChange={(e) => setNewFeature({...newFeature, title: e.target.value})}
                    placeholder="ex: Reranking Cross-Encoder"
                    className="w-full bg-slate-50 border-2 border-transparent focus:border-emerald-500/20 focus:bg-white rounded-2xl px-6 py-4 text-sm font-bold placeholder:text-slate-300 outline-none transition-all duration-300"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">Documentation technique</label>
                  <textarea 
                    value={newFeature.description}
                    onChange={(e) => setNewFeature({...newFeature, description: e.target.value})}
                    placeholder="Quels sont les enjeux et les outils utilisés ?"
                    rows={4}
                    className="w-full bg-slate-50 border-2 border-transparent focus:border-emerald-500/20 focus:bg-white rounded-2xl px-6 py-4 text-sm font-bold placeholder:text-slate-300 outline-none resize-none transition-all duration-300"
                  />
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">Niveau de priorité</label>
                    <select 
                      value={newFeature.priority}
                      onChange={(e) => setNewFeature({...newFeature, priority: e.target.value})}
                      className="w-full bg-slate-50 border-2 border-transparent focus:border-emerald-500/20 focus:bg-white rounded-2xl px-6 py-4 text-sm font-black outline-none appearance-none cursor-pointer transition-all duration-300"
                    >
                      <option value="Haute">🔴 Haute</option>
                      <option value="Moyenne">🟡 Moyenne</option>
                      <option value="Basse">🟢 Basse</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">État actuel</label>
                    <select 
                      value={newFeature.status}
                      onChange={(e) => setNewFeature({...newFeature, status: e.target.value})}
                      className="w-full bg-slate-50 border-2 border-transparent focus:border-emerald-500/20 focus:bg-white rounded-2xl px-6 py-4 text-sm font-black outline-none appearance-none cursor-pointer transition-all duration-300"
                    >
                      <option value="À implémenter">⏳ À implémenter</option>
                      <option value="En cours">⚡ En cours</option>
                      <option value="Déployée">🚀 Déployée</option>
                    </select>
                  </div>
                </div>
                
                <div className="flex gap-4 pt-8">
                  <button 
                    onClick={() => setShowFeatureModal(false)}
                    className="flex-1 py-4 rounded-2xl font-black text-xs uppercase tracking-widest text-slate-400 hover:bg-slate-50 transition-colors"
                  >
                    Annuler
                  </button>
                  <button 
                    onClick={handleSaveFeature}
                    disabled={!newFeature.title.trim()}
                    className="flex-[2] py-4 rounded-2xl font-black text-xs uppercase tracking-widest bg-emerald-600 text-white hover:bg-emerald-700 shadow-[0_12px_24px_rgba(5,150,105,0.2)] disabled:opacity-40 disabled:scale-100 transition-all duration-300"
                  >
                    {editingFeature ? 'Sauvegarder les modifications' : 'Lancer le projet'}
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
