import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/react';
import {
  DndContext,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay,
  defaultDropAnimationSideEffects,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const COLUMNS = [
  { id: 'Nouvelle tâche', title: 'Nouvelle tâche', color: 'bg-slate-100 text-slate-500' },
  { id: 'En cours', title: 'En cours', color: 'bg-amber-100 text-amber-600' },
  { id: 'Terminée', title: 'Terminée', color: 'bg-emerald-100 text-emerald-600' }
];

function SortableTask({ task, onDelete, onEdit }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.3 : 1,
  };

  return (
    <div 
      ref={setNodeRef} 
      style={style} 
      className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm mb-3 group relative cursor-default"
    >
      <div className="flex justify-between items-start mb-2">
        <h4 className="text-sm font-bold text-slate-900 pr-8">{task.title}</h4>
        <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing text-slate-300 hover:text-slate-400 p-1">
          <span className="material-symbols-outlined text-base">drag_indicator</span>
        </div>
      </div>
      
      {task.description && <p className="text-xs text-slate-500 line-clamp-2 mb-3">{task.description}</p>}
      
      <div className="flex items-center justify-between">
        {task.date ? (
          <span className="text-[10px] font-bold text-slate-400 flex items-center gap-1">
            <span className="material-symbols-outlined text-xs">calendar_today</span>
            {task.date}
          </span>
        ) : <div />}
        
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={() => onEdit(task)} className="p-1 hover:bg-slate-50 rounded text-slate-400 hover:text-emerald-600">
            <span className="material-symbols-outlined text-sm">edit</span>
          </button>
          <button onClick={() => onDelete(task.id)} className="p-1 hover:bg-slate-50 rounded text-slate-400 hover:text-rose-600">
            <span className="material-symbols-outlined text-sm">delete</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default function KanbanBoard() {
  const { getToken } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [activeTask, setActiveTask] = useState(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [newTask, setNewTask] = useState({ title: '', description: '', date: '', status: 'Nouvelle tâche' });

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  useEffect(() => {
    fetchTasks();
  }, []);

  async function fetchTasks() {
    try {
      const token = await getToken();
      const response = await fetch(`${API_BASE_URL}/management/tasks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      }
    } catch (error) {
      console.error("Erreur tasks:", error);
    }
  }

  async function handleSaveTask() {
    try {
      const token = await getToken();
      const method = editingTask ? 'PATCH' : 'POST';
      const url = editingTask 
        ? `${API_BASE_URL}/management/tasks/${editingTask.id}`
        : `${API_BASE_URL}/management/tasks`;

      const response = await fetch(url, {
        method,
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newTask)
      });

      if (response.ok) {
        fetchTasks();
        setShowTaskModal(false);
        setEditingTask(null);
      }
    } catch (error) {
      console.error("Save task error:", error);
    }
  }

  async function handleUpdateTaskStatus(taskId, newStatus) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    try {
      const token = await getToken();
      await fetch(`${API_BASE_URL}/management/tasks/${taskId}`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ ...task, status: newStatus })
      });
    } catch (error) {
      console.error("Status update error:", error);
    }
  }

  async function handleDeleteTask(id) {
    if (!confirm("Supprimer cette tâche ?")) return;
    try {
      const token = await getToken();
      await fetch(`${API_BASE_URL}/management/tasks/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchTasks();
    } catch (error) {
      console.error("Delete task error:", error);
    }
  }

  function onDragStart(event) {
    const { active } = event;
    setActiveTask(tasks.find(t => t.id === active.id));
  }

  async function onDragEnd(event) {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    // Si on lache sur une colonne (id est dans COLUMNS), on change le statut
    const overColumn = COLUMNS.find(c => c.id === overId);
    
    if (overColumn) {
      const newStatus = overColumn.id;
      setTasks(prev => prev.map(t => t.id === activeId ? { ...t, status: newStatus } : t));
      handleUpdateTaskStatus(activeId, newStatus);
      return;
    }

    // Si on lache sur une autre tache, on peut reordonner (si meme colonne)
    const overTask = tasks.find(t => t.id === overId);
    if (overTask && activeId !== overId) {
      const oldIndex = tasks.findIndex(t => t.id === activeId);
      const newIndex = tasks.findIndex(t => t.id === overId);
      
      const nextTasks = arrayMove(tasks, oldIndex, newIndex);
      // On met a jour aussi le statut si besoin
      if (nextTasks[newIndex].status !== overTask.status) {
        nextTasks[newIndex].status = overTask.status;
        handleUpdateTaskStatus(activeId, overTask.status);
      }
      setTasks(nextTasks);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black text-slate-900">Task Board</h2>
          <p className="text-slate-500">Gérez le flux de travail au quotidien.</p>
        </div>
        <button 
          onClick={() => { setEditingTask(null); setNewTask({ title: '', description: '', date: '', status: 'Nouvelle tâche' }); setShowTaskModal(true); }}
          className="bg-slate-900 hover:bg-slate-800 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 shadow-lg transition-all active:scale-95"
        >
          <span className="material-symbols-outlined text-lg">add_task</span>
          Nouvelle Tâche
        </button>
      </div>

      <DndContext 
        sensors={sensors} 
        collisionDetection={closestCorners} 
        onDragStart={onDragStart}
        onDragEnd={onDragEnd}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {COLUMNS.map(column => (
            <div key={column.id} className="bg-slate-50/50 rounded-[32px] p-2 border border-slate-100 min-h-[500px] flex flex-col">
              <div className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${column.color.split(' ')[0]}`} />
                  <h3 className="font-black text-xs uppercase tracking-widest text-slate-500">{column.title}</h3>
                </div>
                <span className="bg-white px-2 py-0.5 rounded-lg text-[10px] font-black text-slate-400 border border-slate-100">
                  {tasks.filter(t => t.status === column.id).length}
                </span>
              </div>
              
              <div className="flex-1 p-2">
                <SortableContext items={tasks.filter(t => t.status === column.id)} strategy={verticalListSortingStrategy}>
                  {tasks.filter(t => t.status === column.id).map(task => (
                    <SortableTask 
                      key={task.id} 
                      task={task} 
                      onDelete={handleDeleteTask}
                      onEdit={(t) => { setEditingTask(t); setNewTask(t); setShowTaskModal(true); }}
                    />
                  ))}
                </SortableContext>
                
                {/* Zone de drop vide au fond */}
                <div className="h-20" />
              </div>
            </div>
          ))}
        </div>

        <DragOverlay>
          {activeTask ? (
            <div className="bg-white p-4 rounded-2xl border-2 border-emerald-500 shadow-xl w-[300px] opacity-90 scale-105">
              <h4 className="text-sm font-bold text-slate-900">{activeTask.title}</h4>
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Modal Task */}
      <AnimatePresence>
        {showTaskModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setShowTaskModal(false)} className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" />
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} className="relative bg-white rounded-[32px] w-full max-w-lg p-8 shadow-2xl">
              <h3 className="text-2xl font-black mb-6">{editingTask ? 'Modifier la Tâche' : 'Nouvelle Tâche'}</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Titre</label>
                  <input type="text" value={newTask.title} onChange={(e) => setNewTask({...newTask, title: e.target.value})} placeholder="ex: Bug fix CSS Kanban" className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-slate-900" />
                </div>
                <div>
                  <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Description</label>
                  <textarea value={newTask.description} onChange={(e) => setNewTask({...newTask, description: e.target.value})} placeholder="Optionnel..." rows={3} className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-slate-900 resize-none" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Échéance</label>
                    <input type="date" value={newTask.date || ''} onChange={(e) => setNewTask({...newTask, date: e.target.value})} className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-slate-900" />
                  </div>
                  <div>
                    <label className="block text-[11px] font-black uppercase text-slate-400 tracking-widest mb-1.5">Statut</label>
                    <select value={newTask.status} onChange={(e) => setNewTask({...newTask, status: e.target.value})} className="w-full bg-slate-50 border-0 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-slate-900 cursor-pointer">
                      {COLUMNS.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                    </select>
                  </div>
                </div>
                <div className="flex gap-3 pt-6">
                  <button onClick={() => setShowTaskModal(false)} className="flex-1 py-3.5 rounded-2xl font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors">Annuler</button>
                  <button onClick={handleSaveTask} disabled={!newTask.title.trim()} className="flex-[2] py-3.5 rounded-2xl font-bold bg-slate-900 text-white hover:bg-slate-800 transition-all active:scale-95 disabled:opacity-50">{editingTask ? 'Enregistrer' : 'Ajouter'}</button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
