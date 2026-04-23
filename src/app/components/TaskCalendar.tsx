import { useState } from 'react';
import { Calendar } from './ui/calendar';
import { Task } from './TaskForm';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { format, isSameDay } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface TaskCalendarProps {
  tasks: Task[];
  onSelectDate: (date: Date) => void;
}

export function TaskCalendar({ tasks, onSelectDate }: TaskCalendarProps) {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());

  const handleDateSelect = (date: Date | undefined) => {
    if (date) {
      setSelectedDate(date);
      onSelectDate(date);
    }
  };

  // Conta tarefas por data
  const getTasksForDate = (date: Date) => {
    return tasks.filter(task => 
      isSameDay(new Date(task.date), date)
    );
  };

  // Customiza os dias com tarefas
  const modifiers = {
    hasTasks: (date: Date) => {
      const tasksForDay = getTasksForDate(date);
      return tasksForDay.length > 0;
    },
    hasCompletedTasks: (date: Date) => {
      const tasksForDay = getTasksForDate(date);
      return tasksForDay.some(task => task.completed);
    }
  };

  const selectedDateTasks = selectedDate ? getTasksForDate(selectedDate) : [];

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <Calendar
          mode="single"
          selected={selectedDate}
          onSelect={handleDateSelect}
          locale={ptBR}
          className="rounded-md"
          modifiers={modifiers}
          modifiersClassNames={{
            hasTasks: 'bg-blue-100 font-bold',
            hasCompletedTasks: 'bg-green-100'
          }}
        />
      </Card>

      {selectedDate && (
        <Card className="p-4">
          <h3 className="font-semibold mb-3">
            Tarefas para {format(selectedDate, "dd 'de' MMMM", { locale: ptBR })}
          </h3>
          {selectedDateTasks.length === 0 ? (
            <p className="text-sm text-gray-500">Nenhuma tarefa para este dia</p>
          ) : (
            <div className="space-y-2">
              {selectedDateTasks.map(task => (
                <div
                  key={task.id}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded-md"
                >
                  <div className="flex-1">
                    <p className={`text-sm font-medium ${
                      task.completed ? 'line-through text-gray-400' : 'text-gray-900'
                    }`}>
                      {task.title}
                    </p>
                    {task.description && (
                      <p className="text-xs text-gray-500 mt-1">{task.description}</p>
                    )}
                  </div>
                  <Badge variant={task.completed ? "secondary" : "default"}>
                    {task.completed ? 'Concluída' : 'Pendente'}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      <Card className="p-4 bg-blue-50 border-blue-200">
        <h4 className="text-sm font-semibold mb-2">Legenda:</h4>
        <div className="space-y-1 text-xs text-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-blue-100 border rounded"></div>
            <span>Dias com tarefas</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-100 border rounded"></div>
            <span>Dias com tarefas concluídas</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
