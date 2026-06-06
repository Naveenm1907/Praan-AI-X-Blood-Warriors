"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/patient", label: "Patient" },
  { href: "/blood-bank", label: "Blood Bank" },
  { href: "/donor-outreach", label: "Voice Calls" },
  { href: "/coordinator", label: "Command Center" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-[var(--bg-primary)]/95 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-blood text-xl">&#9829;</span>
          <span className="text-lg font-bold text-[var(--text-primary)]">
            PRAAN AI
          </span>
          <span className="text-[var(--text-muted)] mx-1">&times;</span>
          <span className="text-sm font-medium text-[var(--orange)]">
            Blood Warriors
          </span>
        </Link>

        <div className="flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-[var(--bg-card)] text-blood"
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
