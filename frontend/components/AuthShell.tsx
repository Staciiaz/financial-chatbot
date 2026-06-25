import React from "react";

export default function AuthShell({
  eyebrow,
  title,
  subtitle,
  children,
  footer,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#0f0f14] flex items-center justify-center px-4 py-10">
      {/* Ambient glow background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-40 h-96 w-96 rounded-full bg-brand-600/20 blur-3xl" />
        <div className="absolute -bottom-40 -right-20 h-96 w-96 rounded-full bg-amber-500/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="mb-8 text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-brand-300">
            {eyebrow}
          </span>
          <h1 className="mt-5 font-serif text-3xl text-white sm:text-4xl">
            {title}
          </h1>
          <p className="mt-2 text-sm text-slate-400">{subtitle}</p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-[0_0_60px_-15px_rgba(139,92,246,0.35)] backdrop-blur-sm sm:p-8">
          {children}
        </div>

        <div className="mt-6 text-center text-sm text-slate-400">
          {footer}
        </div>
      </div>
    </div>
  );
}
