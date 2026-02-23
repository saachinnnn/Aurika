"use client";

import { ReactNode } from "react";

interface GradientBorderProps {
  children: ReactNode;
  className?: string;
}

export default function GradientBorder({
  children,
  className = "",
}: GradientBorderProps) {
  return (
    <div className={`relative rounded-2xl p-px ${className}`}>
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-border-hover to-border opacity-100 transition-opacity duration-300" />
      <div className="relative rounded-2xl bg-surface">{children}</div>
    </div>
  );
}
