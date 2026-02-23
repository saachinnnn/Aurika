"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import Button from "@/components/ui/Button";

const headlineWords = ["Understand", "How", "Your", "Mind", "Codes."];

// Pre-computed particle data to avoid hydration mismatch from Math.random()
const PARTICLES = [
  { w: 2.8, h: 3.1, l: 12, t: 72, o: 0.06, dy: -320, dur: 18, del: 2 },
  { w: 3.2, h: 2.4, l: 28, t: 85, o: 0.07, dy: -280, dur: 22, del: 5 },
  { w: 2.1, h: 2.9, l: 41, t: 67, o: 0.05, dy: -350, dur: 25, del: 1 },
  { w: 3.6, h: 3.4, l: 55, t: 91, o: 0.07, dy: -240, dur: 16, del: 8 },
  { w: 2.5, h: 2.2, l: 68, t: 78, o: 0.06, dy: -300, dur: 20, del: 3 },
  { w: 3.0, h: 3.8, l: 82, t: 88, o: 0.05, dy: -260, dur: 28, del: 6 },
  { w: 2.3, h: 2.7, l: 7, t: 95, o: 0.07, dy: -380, dur: 19, del: 0 },
  { w: 3.4, h: 2.1, l: 35, t: 62, o: 0.06, dy: -290, dur: 24, del: 4 },
  { w: 2.7, h: 3.3, l: 50, t: 80, o: 0.05, dy: -310, dur: 17, del: 7 },
  { w: 3.1, h: 2.6, l: 74, t: 70, o: 0.07, dy: -340, dur: 26, del: 9 },
  { w: 2.4, h: 3.0, l: 90, t: 84, o: 0.06, dy: -270, dur: 21, del: 2 },
  { w: 3.5, h: 2.3, l: 18, t: 93, o: 0.05, dy: -360, dur: 23, del: 5 },
  { w: 2.9, h: 3.6, l: 62, t: 75, o: 0.07, dy: -250, dur: 15, del: 8 },
  { w: 2.2, h: 2.8, l: 45, t: 98, o: 0.06, dy: -330, dur: 27, del: 1 },
  { w: 3.3, h: 3.2, l: 80, t: 65, o: 0.05, dy: -370, dur: 20, del: 4 },
];

function FloatingParticles() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {PARTICLES.map((p, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            width: p.w,
            height: p.h,
            left: `${p.l}%`,
            top: `${p.t}%`,
            backgroundColor: "#FF4400",
            opacity: p.o,
          }}
          animate={{
            y: [0, p.dy],
            opacity: [p.o, 0],
          }}
          transition={{
            duration: p.dur,
            repeat: Infinity,
            ease: "linear",
            delay: p.del,
          }}
        />
      ))}
    </div>
  );
}

function DotGrid() {
  return (
    <div
      className="pointer-events-none absolute inset-0"
      style={{
        backgroundImage:
          "radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)",
        backgroundSize: "32px 32px",
      }}
    />
  );
}

export default function Hero() {
  return (
    <section className="relative flex h-screen min-h-[700px] items-center justify-center overflow-hidden">
      {/* Background effects */}
      <DotGrid />
      <FloatingParticles />

      {/* Centered glow with blur(60px) and pulse */}
      <motion.div
        className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
        style={{
          width: 600,
          height: 400,
          background:
            "radial-gradient(ellipse 600px 400px at center, rgba(255, 68, 0, 0.15), transparent)",
          filter: "blur(60px)",
        }}
        animate={{
          opacity: [0.5, 1, 0.5],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center px-5 text-center">
        {/* Label */}
        <motion.span
          className="mb-4 text-[13px] font-medium uppercase tracking-[0.1em] text-accent"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          Programming Cognition Engine
        </motion.span>

        {/* Headline */}
        <h1 className="mb-6 max-w-4xl text-4xl font-[800] leading-tight tracking-[-0.03em] text-text-heading md:text-[64px] md:leading-[1.1]">
          {headlineWords.map((word, i) => (
            <motion.span
              key={i}
              className="mr-[0.3em] inline-block last:mr-0"
              style={
                word === "Codes."
                  ? { textShadow: "0 0 30px rgba(255, 68, 0, 0.3)" }
                  : undefined
              }
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.6,
                delay: 0.5 + i * 0.08,
                ease: [0.22, 1, 0.36, 1],
              }}
            >
              {word}
            </motion.span>
          ))}
        </h1>

        {/* Subtitle */}
        <motion.p
          className="mb-10 max-w-[540px] text-base leading-relaxed text-text-secondary md:text-lg md:leading-[1.7]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.1 }}
        >
          We analyze every solution you&apos;ve ever written on LeetCode — to
          reveal how you think, where you break, and what to conquer next.
        </motion.p>

        {/* CTA */}
        <motion.div
          className="flex flex-col items-center gap-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1.3 }}
        >
          <Button href="#" size="lg">
            Start For Free <span aria-hidden="true">&rarr;</span>
          </Button>
          <span className="text-[13px] text-text-secondary">
            No credit card required
          </span>
          <span className="text-[13px] text-text-secondary">
            Already have an account?{" "}
            <a
              href="/login"
              className="text-text-heading underline decoration-text-heading/30 underline-offset-2 transition-colors hover:text-accent"
            >
              Log in
            </a>
          </span>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.a
        href="#features"
        className="absolute bottom-8 left-1/2 -translate-x-1/2 text-text-secondary/40 transition-colors hover:text-text-primary"
        animate={{ y: [0, 4, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        aria-label="Scroll to features"
      >
        <ChevronDown size={24} />
      </motion.a>
    </section>
  );
}
