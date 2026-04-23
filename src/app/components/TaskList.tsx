import { Check, Trash2, Edit, X } from 'lucide-react';
import { Button } from './ui/button';
import { Checkbox } from './ui/checkbox';
import { Task } from './TaskForm';
import { useState } from 'react';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (id: string) => void;
  onDeleteTask: (id: string) => void;
  onUpdateTask: (id: string, updates: Partial<Task>) => void;
}

export function TaskList({ tasks, onToggleComplete, onDeleteTask, onUpdateTask }: TaskListProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');

  const startEditing = (task: Task) => {
    setEditingId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description);
  };

  const cancelEditing = () => {
    setEditingId(null);
    setEditTitle('');
    setEditDescription('');
  };

  const saveEditing = (id: string) => {
    if (!editTitle.trim()) return;
    
    onUpdateTask(id, {
      title: editTitle.trim(),
      description: editDescription.trim()
    });
    
    setEditingId(null);
    setEditTitle('');
    setEditDescription('');
  };

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">Nenhuma tarefa encontrada</p>
        <p className="text-sm mt-2">Adicione uma nova tarefa para começar!</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map(task => (
        <div
          key={task.id}
          className="bg-white p-4 rounded-lg shadow-sm border hover:shadow-md transition-shadow"
        >
          {editingId === task.id ? (
            <div className="space-y-3">
              <Input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                placeholder="Título"
                className="font-medium"
              />
              <Textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                placeholder="Descrição"
                rows={2}
              />
              <div className="flex gap-2 justify-end">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={cancelEditing}
                >
                  <X className="h-4 w-4 mr-1" />
                  Cancelar
                </Button>
                <Button
                  size="sm"
                  onClick={() => saveEditing(task.id)}
                >
                  <Check className="h-4 w-4 mr-1" />
                  Salvar
                </Button>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-start gap-3">
                <Checkbox
                  id={`task-${task.id}`}
                  checked={task.completed}
                  onCheckedChange={() => onToggleComplete(task.id)}
                  className="mt-1"
                />
                <div className="flex-1 min-w-0">
                  <label
                    htmlFor={`task-${task.id}`}
                    className={`block font-medium cursor-pointer ${
                      task.completed ? 'line-through text-gray-400' : 'text-gray-900'
                    }`}
                  >
                    {task.title}
                  </label>
                  {task.description && (
                    <p className={`text-sm mt-1 ${
                      task.completed ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {task.description}
                    </p>
                  )}
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span>
                      📅 {format(new Date(task.date), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
                    </span>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => startEditing(task)}
                    title="Editar tarefa"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => onDeleteTask(task.id)}
                    title="Excluir tarefa"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
