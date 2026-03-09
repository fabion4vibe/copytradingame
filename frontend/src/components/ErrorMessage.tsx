interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="flex flex-col items-center gap-3 p-6 bg-red-950 border border-red-700 rounded-lg text-center">
      <p className="text-red-300 text-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-1.5 text-xs bg-red-700 hover:bg-red-600 text-white rounded transition-colors"
        >
          Riprova
        </button>
      )}
    </div>
  );
}
