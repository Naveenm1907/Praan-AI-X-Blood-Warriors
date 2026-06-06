import { Clock } from '@phosphor-icons/react';

interface CountdownTimerProps {
  days: number;
  label?: string;
}

export function CountdownTimer({ days, label = 'Transfusion Urgency' }: CountdownTimerProps) {
  const getColor = () => {
    if (days > 7) return 'var(--positive)';
    if (days > 3) return 'var(--warning)';
    return 'var(--blood)';
  };

  const color = getColor();
  const isUrgent = days <= 3;

  return (
    <div
      className={`rounded-2xl border-t-4 border-border bg-card p-6 ${
        isUrgent ? 'animate-pulse-border-red' : ''
      }`}
      style={{ borderTopColor: color }}
    >
      <div className="flex items-center gap-2 text-sm text-secondary">
        <Clock weight="regular" size={18} />
        <span>{label}</span>
      </div>
      <p
        className="mt-2 text-2xl font-bold font-mono"
        style={{ color }}
      >
        {days} DAYS
      </p>
    </div>
  );
}
