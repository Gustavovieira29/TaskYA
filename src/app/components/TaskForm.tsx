import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { AudioRecorder } from './AudioRecorder';
import { toast } from 'sonner';

export interface Task {
  id: string;
  title: string;
  description: string;
  date: string;
  completed: boolean;
  createdAt: string;
}

interface TaskFormProps {
  onAddTask: (task: Omit<Task, 'id' | 'createdAt'>) => void;
  selectedDate?: Date;
}

export function TaskForm({ onAddTask, selectedDate }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [date, setDate] = useState(
    selectedDate ? selectedDate.toISOString().split('T')[0] : new Date().toISOString().split('T')[0]
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim()) {
      toast.error('Digite um título para a tarefa');
      return;
    }

    onAddTask({
      title: title.trim(),
      description: description.trim(),
      date,
      completed: false
    });

    setTitle('');
    setDescription('');
    setDate(new Date().toISOString().split('T')[0]);
    
    toast.success('Tarefa adicionada com sucesso!');
  };

  const handleAudioTranscript = (transcript: string) => {
    // Se o título estiver vazio, usa o transcript como título
    // Caso contrário, adiciona à descrição
    if (!title.trim()) {
      setTitle(transcript);
    } else {
      setDescription(prev => prev ? `${prev} ${transcript}` : transcript);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow-sm border">
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-2">
          Título da Tarefa
        </label>
        <div className="flex gap-2">
          <Input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ex: Reunião com cliente"
            className="flex-1"
          />
          <AudioRecorder onTranscript={handleAudioTranscript} />
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-2">
          Descrição (opcional)
        </label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Adicione detalhes sobre a tarefa..."
          rows={3}
        />
      </div>

      <div>
        <label htmlFor="date" className="block text-sm font-medium mb-2">
          Data
        </label>
        <Input
          id="date"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-full"
        />
      </div>

      <Button type="submit" className="w-full">
        <Plus className="h-4 w-4 mr-2" />
        Adicionar Tarefa
      </Button>
    </form>
  );
}
