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
  { id: 'Nouvelle tâche', title: 'À faire', icon: 'list_alt', color: 'text-slate-400', bg: 'bg-slate-100/50' },
  { id: 'En cours', title: 'En cours', icon: 'bolt', color: 'text-amber-500', bg: 'bg-amber-50/50' },
  { id: 'Terminée', title: 'Terminée', icon: 'check_circle', color: 'text-emerald-500', bg: 'bg-emerald-50/50' }
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
      className="group bg-white p-5 rounded-2xl border border-slate-200/60 shadow-[0_4px_12px_rgba(0,0,0,0.02)] mb-4 hover:shadow-[0_12px_24px_rgba(0,0,0,0.06)] hover:border-emerald-500/20 transition-all duration-300 relative cursor-default"
    >
      <div className="flex justify-between items-start gap-3 mb-3">
        <h4 className="text-[13px] font-bold text-slate-800 leading-snug pr-6 tracking-tight">{task.title}</h4>
        <div {...attributes} {...listeners} className="cursor-grab active:cursor-grabbing text-slate-200 hover:text-slate-400 p-1 transition-colors">
          <span className="material-symbols-outlined text-lg">drag_indicator</span>
        </div>
      </div>
      
      {task.description && (
        <p className="text-[11px] text-slate-400 leading-relaxed font-medium line-clamp-2 mb-4">
          {task.description}
        </p>
      )}
      
      <div className="flex items-center justify-between pt-4 border-t border-slate-50">
        <div className="flex items-center gap-2">
          {task.date ? (
            <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-50 rounded-lg">
              <span className="material-symbols-outlined text-[12px] text-slate-400">calendar_today</span>
              <span className="text-[9px] font-black text-slate-400 uppercase tracking-tighter">{task.date}</span>
            </div>
          ) : <div />}
        </div>
        
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300">
          <button onClick={() => onEdit(task)} className="w-7 h-7 flex items-center justify-center hover:bg-slate-50 rounded-full text-slate-300 hover:text-emerald-600 transition-colors">
            <span className="material-symbols-outlined text-base">edit_square</span>
          </button>
          <button onClick={() => onDelete(task.id)} className="w-7 h-7 flex items-center justify-center hover:bg-slate-50 rounded-full text-slate-300 hover:text-rose-600 transition-colors">
            <span className="material-symbols-outlined text-base">delete</span>
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
      console.error("Fetch tasks error:", error);
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

    const overColumn = COLUMNS.find(c => c.id === overId);
    
    if (overColumn) {
      const newStatus = overColumn.id;
      setTasks(prev => prev.map(t => t.id === activeId ? { ...t, status: newStatus } : t));
      handleUpdateTaskStatus(activeId, newStatus);
      return;
    }

    const overTask = tasks.find(t => t.id === overId);
    if (overTask && activeId !== overId) {
      const oldIndex = tasks.findIndex(t => t.id === activeId);
      const newIndex = tasks.findIndex(t => t.id === overId);
      
      const nextTasks = arrayMove(tasks, oldIndex, newIndex);
      if (nextTasks[newIndex].status !== overTask.status) {
        nextTasks[newIndex].status = overTask.status;
        handleUpdateTaskStatus(activeId, overTask.status);
      }
      setTasks(nextTasks);
    }
  }

  return (
    <div className="space-y-10">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-black text-slate-900 tracking-tight mb-2">Workspace</h2>
          <p className="text-slate-500 font-medium">Gérez le flux de travail et les micro-tâches techniques.</p>
        </div>
        <button 
          onClick={() => { setEditingTask(null); setNewTask({ title: '', description: '', date: '', status: 'Nouvelle tâche' }); setShowTaskModal(true); }}
          className="bg-slate-900 hover:bg-slate-800 text-white min-h-[52px] px-8 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center gap-3 shadow-[0_12px_24px_rgba(0,0,0,0.15)] transition-all duration-300 hover:scale-[1.03] active:scale-[0.97]"
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
          {COLUMNS.map(column => (
            <div key={column.id} className="bg-slate-50/40 rounded-[40px] p-3 border border-slate-200/40 min-h-[600px] flex flex-col">
              <div className="p-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-xl ${column.bg} flex items-center justify-center`}>
                    <span className={`material-symbols-outlined text-lg ${column.color}`}>{column.icon}</span>
                  </div>
                  <h3 className="font-black text-[10px] uppercase tracking-[0.2em] text-slate-500">{column.title}</h3>
                </div>
                <span className="bg-white/80 px-2.5 py-1 rounded-lg text-[9px] font-black text-slate-400 border border-slate-100 shadow-sm">
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
              </div>
            </div>
          ))}
        </div>

        <DragOverlay>
          {activeTask ? (
            <div className="bg-white p-5 rounded-2xl border-2 border-emerald-500 shadow-2xl w-[320px] scale-105 pointer-events-none">
              <h4 className="text-[13px] font-bold text-slate-900">{activeTask.title}</h4>
              <p className="text-[10px] text-slate-400 font-medium mt-2">Déplacement en cours...</p>
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Modal Task */}
      <AnimatePresence>
        {showTaskModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setShowTaskModal(false)} className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" />
            <motion.div 
              initial={{ scale: 0.9, opacity: 0, y: 20 }} 
              animate={{ scale: 1, opacity: 1, y: 0 }} 
              exit={{ scale: 0.9, opacity: 0, y: 20 }} 
              className="relative bg-white rounded-[40px] w-full max-w-lg p-10 shadow-[0_40px_80px_rgba(0,0,0,0.25)]"
            >
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h3 className="text-3xl font-black tracking-tight">{editingTask ? 'Détails de la tâche' : 'Nouvelle Tâche'}</h3>
                  <p className="text-slate-400 text-sm font-medium">Définissez une micro-tâche pour le workspace.</p>
                </div>
                <button onClick={() => setShowTaskModal(false)} className="w-10 h-10 flex items-center justify-center hover:bg-slate-100 rounded-full text-slate-400 transition-colors">
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">Intitulé de la tâche</label>
                  <input type="text" value={newTask.title} onChange={(e) => setNewTask({...newTask, title: e.target.value})} placeholder="ex: Bug fix CSS Kanban" className="w-full bg-slate-50 border-2 border-transparent focus:border-slate-900/10 focus:bg-white rounded-2xl px-6 py-4 text-sm font-bold placeholder:text-slate-300 outline-none transition-all duration-300" />
                </div>
                <div>
                  <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">Notes ou contexte</label>
                  <textarea value={newTask.description} onChange={(e) => setNewTask({...newTask, description: e.target.value})} placeholder="Détails optionnels..." rows={3} className="w-full bg-slate-50 border-2 border-transparent focus:border-slate-900/10 focus:bg-white rounded-2xl px-6 py-4 text-sm font-bold placeholder:text-slate-300 outline-none resize-none transition-all duration-300" />
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">Échéance</label>
                    <input type="date" value={newTask.date || ''} onChange={(e) => setNewTask({...newTask, date: e.target.value})} className="w-full bg-slate-50 border-2 border-transparent focus:border-slate-900/10 focus:bg-white rounded-2xl px-6 py-4 text-sm font-black outline-none transition-all duration-300" />
                  </div>
                  <div>
                    <label className="block text-[10px] font-black uppercase text-slate-400 tracking-[0.2em] mb-2 ml-1">Colonne</label>
                    <select value={newTask.status} onChange={(e) => setNewTask({...newTask, status: e.target.value})} className="w-full bg-slate-50 border-2 border-transparent focus:border-slate-900/10 focus:bg-white rounded-2xl px-6 py-4 text-sm font-black outline-none appearance-none cursor-pointer transition-all duration-300">
                      {COLUMNS.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                    </select>
                  </div>
                </div>
                <div className="flex gap-4 pt-8">
                  <button onClick={() => setShowTaskModal(false)} className="flex-1 py-4 rounded-2xl font-black text-xs uppercase tracking-widest text-slate-400 hover:bg-slate-50 transition-colors">Annuler</button>
                  <button onClick={handleSaveTask} disabled={!newTask.title.trim()} className="flex-[2] py-4 rounded-2xl font-black text-xs uppercase tracking-widest bg-slate-900 text-white hover:bg-slate-800 shadow-[0_12px_24px_rgba(0,0,0,0.15)] transition-all duration-300 active:scale-95 disabled:opacity-40">{editingTask ? 'Mettre à jour' : 'Ajouter au board'}</button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
