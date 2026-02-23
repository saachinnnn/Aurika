"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface BentoCardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  id?: string;
}

export default function BentoCard({
  children,
  className = "",
  delay = 0,
  id,
}: BentoCardProps) {
  return (
    <motion.div
      id={id}
      className={`group relative overflow-hidden rounded-2xl border border-border bg-surface p-8 transition-all duration-400 ease-out hover:border-border-hover ${className}`}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.7, delay, ease: "easeOut" }}
      whileHover={{
        y: -6,
        boxShadow:
          "0 8px 30px rgba(0, 0, 0, 0.3), 0 0 60px rgba(255, 68, 0, 0.06)",
      }}
      style={{ willChange: "transform" }}
    >
      {/* Gradient border pseudo-element on hover */}
      <div
        className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-400 group-hover:opacity-100"
        style={{
          background:
            "linear-gradient(180deg, rgba(255,68,0,0.2) 0%, rgba(255,68,0,0.05) 50%, transparent 100%)",
          mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          maskComposite: "exclude",
          WebkitMaskComposite: "xor",
          padding: "1px",
        }}
      />
      {/* Warm gradient overlay */}
      <div
        className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-400 group-hover:opacity-100"
        style={{
          background:
            "linear-gradient(180deg, transparent 0%, rgba(255, 68, 0, 0.02) 100%)",
        }}
      />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}
