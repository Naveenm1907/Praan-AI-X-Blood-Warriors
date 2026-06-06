'use client';

import { ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'editorial';

interface ButtonProps {
  children: ReactNode;
  variant?: ButtonVariant;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

export function Button({
  children,
  variant = 'primary',
  onClick,
  className = '',
  disabled = false
}: ButtonProps) {
  const baseStyles = 'relative inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus:outline-none disabled:opacity-40 disabled:cursor-not-allowed';

  const variants = {
    primary: `
      px-8 py-3
      bg-[var(--blood-pink)] text-white
      hover:translate-y-[-2px] hover:shadow-[0_8px_20px_rgba(241,65,99,0.3)]
      active:translate-y-0
      rounded-none
      text-sm uppercase tracking-wider
    `,
    secondary: `
      px-8 py-3
      bg-transparent text-[var(--text-primary)]
      border-2 border-[var(--blood-pink)]
      hover:bg-[var(--blood-pink)] hover:text-white
      rounded-none
      text-sm uppercase tracking-wider
    `,
    ghost: `
      px-6 py-2
      text-[var(--text-secondary)]
      hover:text-[var(--blood-pink)]
      text-sm uppercase tracking-wider
    `,
    editorial: `
      px-0 py-0
      text-[var(--blood-pink)]
      border-b-2 border-[var(--blood-pink)]
      hover:border-[var(--text-primary)]
      text-base font-normal normal-case tracking-normal
      group
    `,
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${className}`}
    >
      {children}
      {variant === 'editorial' && (
        <span className="ml-1 transition-transform group-hover:translate-x-1">→</span>
      )}
    </button>
  );
}
