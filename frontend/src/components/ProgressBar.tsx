interface ProgressBarProps {
  value: number;
  max: number;
  label?: string;
  color?: string;
}

export function ProgressBar({ value, max, label, color = 'var(--success)' }: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100);

  return (
    <div className="w-full">
      <div className="h-2 w-full overflow-hidden rounded bg-surface">
        <div
          className="h-full rounded transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
          style={{
            width: `${percentage}%`,
            background: color,
          }}
        />
      </div>
      {label && (
        <p className="mt-1 text-xs text-secondary">{label}</p>
      )}
    </div>
  );
}
