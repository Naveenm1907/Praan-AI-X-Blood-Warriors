import type { BloodGroup } from '@/lib/types';
import { BLOOD_GROUP_COLORS } from '@/lib/types';

interface BadgeProps {
  type: 'blood' | 'status';
  value: BloodGroup | string;
  className?: string;
}

export function Badge({ type, value, className = '' }: BadgeProps) {
  if (type === 'blood') {
    const color = BLOOD_GROUP_COLORS[value as BloodGroup] || '#9a7a82';
    return (
      <span
        className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-mono font-semibold ${className}`}
        style={{
          backgroundColor: `${color}18`,
          color: color,
        }}
      >
        {value}
      </span>
    );
  }

  const statusConfig: Record<string, { bg: string; color: string; label: string }> = {
    active:    { bg: 'var(--bg-surface)', color: 'var(--green)',  label: 'Active' },
    pending:   { bg: 'var(--bg-surface)', color: 'var(--orange)', label: 'Pending' },
    urgent:    { bg: 'var(--bg-surface)', color: 'var(--blood)',  label: 'Urgent' },
    confirmed: { bg: 'var(--bg-surface)', color: 'var(--teal)',   label: 'Confirmed' },
    declined:  { bg: 'var(--bg-surface)', color: 'var(--muted)',  label: 'Declined' },
    calling:   { bg: 'var(--bg-surface)', color: 'var(--blue)',   label: 'Calling' },
    connected: { bg: 'var(--bg-surface)', color: 'var(--green)',  label: 'Connected' },
    no_answer: { bg: 'var(--bg-surface)', color: 'var(--orange)', label: 'No Answer' },
    waiting:   { bg: 'var(--bg-surface)', color: 'var(--muted)',  label: 'Waiting' },
  };

  const config = statusConfig[value] || { bg: 'var(--bg-surface)', color: 'var(--muted)', label: value };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold ${className}`}
      style={{ backgroundColor: config.bg, color: config.color }}
    >
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: config.color }}
      />
      {config.label}
    </span>
  );
}
