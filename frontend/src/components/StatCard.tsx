import type { ReactNode } from 'react';

interface StatCardProps {
  icon?: ReactNode;
  value: string;
  label: string;
  trend?: {
    value: string;
    positive: boolean;
  };
  color?: string;
}

export function StatCard({ icon, value, label, trend, color }: StatCardProps) {
  const accent = color || 'var(--blood)';

  return (
    <div className="rounded-2xl border border-border bg-card p-6">
      {icon && (
        <div
          className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ backgroundColor: 'var(--bg-surface)', color: accent }}
        >
          {icon}
        </div>
      )}
      <p className="text-2xl font-bold font-display text-primary">{value}</p>
      <p className="mt-1 text-sm text-secondary">{label}</p>
      {trend && (
        <p
          className="mt-2 text-xs font-semibold"
          style={{ color: trend.positive ? 'var(--green)' : 'var(--blood)' }}
        >
          {trend.value}
        </p>
      )}
    </div>
  );
}
