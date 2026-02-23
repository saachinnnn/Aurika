"use client";

import { motion } from "framer-motion";

interface GlowEffectProps {
  width?: number;
  height?: number;
  intensity?: "subtle" | "medium" | "strong";
  className?: string;
}

export default function GlowEffect({
  width = 600,
  height = 400,
  intensity = "medium",
  className = "",
}: GlowEffectProps) {
  const opacityRange = {
    subtle: [0.06, 0.1],
    medium: [0.08, 0.15],
    strong: [0.1, 0.18],
  };

  const [minOpacity, maxOpacity] = opacityRange[intensity];

  return (
    <motion.div
      className={`pointer-events-none absolute ${className}`}
      style={{
        width,
        height,
        background: `radial-gradient(ellipse ${width}px ${height}px at center, rgba(255, 68, 0, ${maxOpacity}), transparent)`,
      }}
      animate={{
        opacity: [minOpacity / maxOpacity, 1, minOpacity / maxOpacity],
      }}
      transition={{
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
  );
}
