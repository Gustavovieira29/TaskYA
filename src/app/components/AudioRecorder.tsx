import { useState, useEffect } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import { Button } from './ui/button';
import { toast } from 'sonner';

interface AudioRecorderProps {
  onTranscript: (text: string) => void;
}

export function AudioRecorder({ onTranscript }: AudioRecorderProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    // Verifica se o navegador suporta Web Speech API
    const SpeechRecognition = 
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    const recognitionInstance = new SpeechRecognition();
    recognitionInstance.continuous = false;
    recognitionInstance.lang = 'pt-BR';
    recognitionInstance.interimResults = false;
    recognitionInstance.maxAlternatives = 1;

    recognitionInstance.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
      toast.success('Áudio transcrito!', {
        description: `"${transcript}"`
      });
    };

    recognitionInstance.onerror = (event: any) => {
      console.error('Erro no reconhecimento de voz:', event.error);
      setIsListening(false);
      
      if (event.error === 'no-speech') {
        toast.error('Nenhuma fala detectada', {
          description: 'Tente falar mais próximo do microfone'
        });
      } else if (event.error === 'not-allowed') {
        toast.error('Permissão negada', {
          description: 'Por favor, permita o acesso ao microfone'
        });
      } else {
        toast.error('Erro no reconhecimento de voz', {
          description: `Erro: ${event.error}`
        });
      }
    };

    recognitionInstance.onend = () => {
      setIsListening(false);
    };

    setRecognition(recognitionInstance);
  }, [onTranscript]);

  const toggleListening = () => {
    if (!recognition) return;

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      try {
        recognition.start();
        setIsListening(true);
        toast.info('Escutando...', {
          description: 'Fale agora para gravar sua tarefa',
          icon: <Volume2 className="h-4 w-4" />
        });
      } catch (error) {
        console.error('Erro ao iniciar reconhecimento:', error);
        toast.error('Erro ao iniciar gravação');
      }
    }
  };

  if (!isSupported) {
    return (
      <Button
        type="button"
        variant="outline"
        size="icon"
        disabled
        title="Seu navegador não suporta reconhecimento de voz"
      >
        <MicOff className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <Button
      type="button"
      variant={isListening ? "destructive" : "outline"}
      size="icon"
      onClick={toggleListening}
      title={isListening ? "Parar gravação" : "Gravar áudio"}
      className={isListening ? "animate-pulse" : ""}
    >
      {isListening ? (
        <MicOff className="h-4 w-4" />
      ) : (
        <Mic className="h-4 w-4" />
      )}
    </Button>
  );
}
