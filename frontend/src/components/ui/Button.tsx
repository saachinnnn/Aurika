"use client";

import { motion } from "framer-motion";
import { ReactNode, useState } from "react";

interface ButtonProps {
  children: ReactNode;
  href?: string;
  onClick?: () => void;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export default function Button({
  children,
  href,
  onClick,
  size = "md",
  className = "",
}: ButtonProps) {
  const [isHovered, setIsHovered] = useState(false);

  const sizeClasses = {
    sm: "px-5 py-2.5 text-sm",
    md: "px-8 py-3.5 text-base",
    lg: "px-9 py-4 text-base",
  };

  const content = (
    <motion.span
      className={`relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-[10px] bg-accent font-medium text-text-heading ${sizeClasses[size]} ${className}`}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{
        backgroundColor: "#FF5500",
        boxShadow: "0 0 30px rgba(255, 68, 0, 0.4)",
      }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      style={{ cursor: "pointer" }}
    >
      {/* Shimmer sweep */}
      <motion.span
        className="pointer-events-none absolute inset-0"
        initial={{ x: "-100%" }}
        animate={isHovered ? { x: "100%" } : { x: "-100%" }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        style={{
          background:
            "linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%)",
        }}
      />
      <span className="relative z-10">{children}</span>
    </motion.span>
  );

  if (href) {
    return (
      <a href={href} onClick={onClick}>
        {content}
      </a>
    );
  }

  return (
    <button onClick={onClick} type="button">
      {content}
    </button>
  );
}
