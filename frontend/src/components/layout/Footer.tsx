import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border bg-[var(--bg-surface)]">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex flex-col items-center gap-4 md:flex-row md:justify-between">
          <div className="flex items-center gap-2">
            <span className="text-blood">&#9829;</span>
            <span className="text-sm font-semibold text-[var(--text-primary)]">
              PRAAN AI
            </span>
            <span className="text-[var(--text-muted)]">&times;</span>
            <span className="text-sm text-[var(--orange)]">Blood Warriors</span>
          </div>

          <p className="text-xs text-[var(--text-muted)]">
            AI for Good 2.0 Hackathon &middot; Built with AWS &middot; Every
            Drop Counts
          </p>

          <div className="flex gap-4 text-xs text-[var(--text-muted)]">
            <Link href="/" className="hover:text-[var(--text-secondary)]">
              Problem Statement
            </Link>
            <Link href="/" className="hover:text-[var(--text-secondary)]">
              Architecture
            </Link>
            <Link href="/" className="hover:text-[var(--text-secondary)]">
              Dataset
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
