"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useState, useEffect } from "react";
import { Link2, Cpu, MessageSquare } from "lucide-react";
import BentoCard from "@/components/ui/BentoCard";
import AITypewriter from "@/components/ui/AITypewriter";
import {
  RADAR_AXES,
  RADAR_VALUES,
  RADAR_IDEAL,
  LEARNING_PATH_NODES,
} from "@/lib/constants";

/* ─── Helpers ─── */

function CardLabel({ text }: { text: string }) {
  return (
    <span className="mb-2 inline-block text-xs font-medium uppercase tracking-[0.08em] text-accent">
      {text}
    </span>
  );
}

function CardTitle({ text }: { text: string }) {
  return (
    <h3 className="mb-2 text-[22px] font-semibold leading-snug tracking-[-0.02em] text-text-heading">
      {text}
    </h3>
  );
}

function CardDesc({ text }: { text: string }) {
  return (
    <p className="text-[15px] leading-relaxed text-text-secondary">{text}</p>
  );
}

/* ─── CARD 1: Weakness Diagnosis — Radar Chart + AI Typewriter ─── */

function RadarChart() {
  const ref = useRef<SVGSVGElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    const start = performance.now();
    function animate(now: number) {
      const t = Math.min((now - start) / 1500, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setProgress(eased);
      if (t < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  }, [isInView]);

  const cx = 140,
    cy = 130,
    r = 90;
  const angleStep = (2 * Math.PI) / 6;

  function getPoint(index: number, value: number) {
    const angle = angleStep * index - Math.PI / 2;
    return {
      x: cx + r * value * Math.cos(angle),
      y: cy + r * value * Math.sin(angle),
    };
  }

  function polygonPoints(values: number[], scale: number = 1) {
    return values
      .map((v, i) => {
        const pt = getPoint(i, v * scale);
        return `${pt.x},${pt.y}`;
      })
      .join(" ");
  }

  const rings = [0.25, 0.5, 0.75, 1];

  return (
    <svg
      ref={ref}
      viewBox="0 0 280 270"
      className="mx-auto w-full max-w-[320px]"
    >
      {/* Grid rings */}
      {rings.map((ring) => (
        <polygon
          key={ring}
          points={Array.from({ length: 6 })
            .map((_, i) => {
              const pt = getPoint(i, ring);
              return `${pt.x},${pt.y}`;
            })
            .join(" ")}
          fill="none"
          stroke="#1F1F1F"
          strokeOpacity={0.5}
          strokeWidth={1}
        />
      ))}

      {/* Axis lines */}
      {Array.from({ length: 6 }).map((_, i) => {
        const pt = getPoint(i, 1);
        return (
          <line
            key={i}
            x1={cx}
            y1={cy}
            x2={pt.x}
            y2={pt.y}
            stroke="#1F1F1F"
            strokeOpacity={0.5}
            strokeWidth={1}
          />
        );
      })}

      {/* Ideal polygon */}
      <polygon
        points={polygonPoints(RADAR_IDEAL)}
        fill="rgba(255,68,0,0.08)"
        stroke="none"
      />

      {/* User polygon */}
      <motion.polygon
        points={polygonPoints(RADAR_VALUES, progress)}
        fill="rgba(255,68,0,0.15)"
        stroke="#FF4400"
        strokeWidth={2}
        className="transition-all duration-100"
      />

      {/* Vertex dots */}
      {RADAR_VALUES.map((v, i) => {
        const pt = getPoint(i, v * progress);
        return (
          <circle
            key={i}
            cx={pt.x}
            cy={pt.y}
            r={3}
            fill="#FF4400"
            opacity={progress}
          />
        );
      })}

      {/* Labels */}
      {RADAR_AXES.map((label, i) => {
        const pt = getPoint(i, 1.22);
        return (
          <text
            key={label}
            x={pt.x}
            y={pt.y}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="#71717A"
            fontSize={11}
            style={{ fontFamily: "var(--font-geist-sans), sans-serif" }}
          >
            {label}
          </text>
        );
      })}
    </svg>
  );
}

function WeaknessDiagnosisCard() {
  return (
    <BentoCard className="md:col-span-2" delay={0}>
      <div className="mb-4">
        <CardLabel text="Diagnosis" />
        <CardTitle text="Know exactly where you break." />
        <CardDesc text="We analyze your mistake patterns across hundreds of submissions. Not just what topics — but why you fail, how often, and whether you're improving." />
      </div>
      <RadarChart />
      <div className="mt-4 flex flex-wrap gap-2">
        <span className="rounded-full bg-[#1F1F1F] px-3 py-1 text-xs text-text-primary">
          Weakest: <span className="text-red-400">DP (23%)</span>
        </span>
        <span className="rounded-full bg-[#1F1F1F] px-3 py-1 text-xs text-text-primary">
          Strongest: <span className="text-green-400">Arrays (89%)</span>
        </span>
        <span className="rounded-full bg-[#1F1F1F] px-3 py-1 text-xs text-text-primary">
          Improving: Trees <span className="text-accent">&uarr;</span>
        </span>
      </div>
      {/* AI Typewriter */}
      <AITypewriter
        prefix="Analyzing 708 submissions..."
        lines={[
          { text: "Pattern: Repeated O(n²) in DP problems", color: "#FF4400" },
          {
            text: "Root cause: Missing memoization recognition",
            color: "#71717A",
          },
          { text: "Suggestion: Focus on top-down DP patterns", color: "#22c55e" },
        ]}
      />
    </BentoCard>
  );
}

/* ─── CARD 2: Solution Comparison — Split Code + Diff + AI Bubble ─── */

const userCode = [
  "def twoSum(nums, t):",
  "    for i in range(len(nums)):",
  "        for j in range(i+1, len(nums)):",
  "            if nums[i] + nums[j] == t:",
  "                return [i, j]",
];

const optimalCode = [
  "def twoSum(nums, t):",
  "    seen = {}",
  "    for i, n in enumerate(nums):",
  "        if t - n in seen:",
  "            return [seen[t-n], i]",
  "        seen[n] = i",
];

function CodePane({
  title,
  code,
  titleColor,
  highlightLines,
  highlightColor,
  delay,
}: {
  title: string;
  code: string[];
  titleColor: string;
  highlightLines: number[];
  highlightColor: string;
  delay: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  return (
    <div ref={ref} className="flex-1 overflow-hidden rounded-lg bg-[#0A0A0A] p-3">
      <span
        className="mb-2 block text-[10px] uppercase tracking-wider"
        style={{ color: titleColor }}
      >
        {title}
      </span>
      <div className="font-mono text-xs leading-relaxed">
        {code.map((line, i) => (
          <motion.div
            key={i}
            className="flex"
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.15, delay: delay + i * 0.08 }}
          >
            {highlightLines.includes(i) && (
              <span
                className="mr-2 w-0.5 shrink-0 rounded-full"
                style={{ backgroundColor: highlightColor }}
              />
            )}
            <span className="whitespace-pre text-text-secondary/60">
              {line}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function SolutionComparisonCard() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  return (
    <BentoCard delay={0.15}>
      <div className="mb-4">
        <CardLabel text="Comparison" />
        <CardTitle text="Your code vs. the best approach." />
        <CardDesc text="Side-by-side analysis with optimal solutions. See what you missed and why it matters." />
      </div>
      <div ref={ref} className="flex flex-col gap-2 sm:flex-col">
        <CodePane
          title="Your Code"
          code={userCode}
          titleColor="#71717A"
          highlightLines={[1, 2]}
          highlightColor="#ef4444"
          delay={0}
        />
        {/* Diff indicator */}
        <motion.div
          className="flex items-center justify-center"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={isInView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <span className="flex h-7 w-7 items-center justify-center rounded-full border border-border bg-[#141414] text-sm font-bold text-accent">
            &ne;
          </span>
        </motion.div>
        <CodePane
          title="Optimal"
          code={optimalCode}
          titleColor="#FF4400"
          highlightLines={[1, 2, 3, 4, 5]}
          highlightColor="#22c55e"
          delay={0.5}
        />
      </div>
      <motion.div
        className="mt-3 flex items-center justify-center"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={isInView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 0.4, delay: 1.2 }}
      >
        <span className="rounded-md bg-[#1F1F1F] px-3 py-1 text-xs font-medium text-accent">
          O(n&sup2;) &rarr; O(n)
        </span>
      </motion.div>

      {/* AI Chat Bubble */}
      <motion.div
        className="mt-3 flex items-start gap-2.5"
        initial={{ opacity: 0, y: 10 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.4, delay: 1.5 }}
      >
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-text-heading">
          A
        </div>
        <div className="rounded-lg bg-[#141414] px-3 py-2 text-xs leading-relaxed text-text-secondary">
          Your nested loop approach is correct but scales poorly. Using a hash
          map reduces lookups from O(n) to O(1).
        </div>
      </motion.div>

      {/* Pulsing complexity badge */}
      <motion.div
        className="mt-2 flex justify-center"
        initial={{ opacity: 0 }}
        animate={isInView ? { opacity: 1 } : {}}
        transition={{ duration: 0.3, delay: 1.8 }}
      >
        <motion.span
          className="rounded-full border border-accent/20 bg-accent/5 px-3 py-0.5 text-[11px] font-medium text-accent"
          animate={{ opacity: [0.7, 1, 0.7] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          Complexity: O(n&sup2;) → O(n)
        </motion.span>
      </motion.div>
    </BentoCard>
  );
}

/* ─── CARD 3: Code Analysis — Line Numbers, Annotations, Score, Tags ─── */

const analysisCode = [
  "def search(nums, target):",
  "    lo, hi = 0, len(nums) - 1",
  "    while lo <= hi:",
  "        mid = (lo + hi) // 2",
  "        if nums[mid] == target:",
  "            return mid",
];

const annotations = [
  { line: 0, text: "Binary Search · O(log n)", color: "#FF4400" },
  { line: 3, text: "Correct midpoint calc", color: "#22c55e" },
  { line: 4, text: "Edge case: empty array?", color: "#eab308" },
];

function CodeAnalysisCard() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });
  const [scoreProgress, setScoreProgress] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    const timeout = setTimeout(() => {
      const start = performance.now();
      function animate(now: number) {
        const t = Math.min((now - start) / 1000, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        setScoreProgress(eased);
        if (t < 1) requestAnimationFrame(animate);
      }
      requestAnimationFrame(animate);
    }, 1200);
    return () => clearTimeout(timeout);
  }, [isInView]);

  const scoreValue = 8.5;
  const circumference = 2 * Math.PI * 18;
  const strokeDash = (scoreValue / 10) * circumference * scoreProgress;

  // Which lines have annotations
  const annotationLineMap = new Map(annotations.map((a) => [a.line, a]));

  return (
    <BentoCard delay={0.3}>
      <div className="mb-4">
        <CardLabel text="Analysis" />
        <CardTitle text="Every line understood." />
        <CardDesc text="Line-by-line code review with complexity verification, approach classification, and interview scoring." />
      </div>
      <div ref={ref} className="relative rounded-lg bg-[#0A0A0A] p-3">
        <div className="font-mono text-xs leading-relaxed">
          {analysisCode.map((line, i) => {
            const ann = annotationLineMap.get(i);
            return (
              <div key={i} className="flex items-start">
                {/* Line number */}
                <motion.span
                  className="mr-3 w-5 shrink-0 select-none text-right text-text-secondary/30"
                  initial={{ opacity: 0 }}
                  animate={isInView ? { opacity: 1 } : {}}
                  transition={{ duration: 0.3, delay: i * 0.08 }}
                >
                  {i + 1}
                </motion.span>
                {/* Annotation bar */}
                {ann && (
                  <span
                    className="mr-2 mt-0.5 w-0.5 shrink-0 self-stretch rounded-full"
                    style={{ backgroundColor: ann.color }}
                  />
                )}
                <motion.span
                  className="whitespace-pre text-text-secondary/60"
                  initial={{ opacity: 0 }}
                  animate={isInView ? { opacity: 1 } : {}}
                  transition={{ duration: 0.3, delay: i * 0.08 }}
                >
                  {line}
                </motion.span>
              </div>
            );
          })}
        </div>

        {/* Annotations */}
        <div className="mt-3 flex flex-col gap-2">
          {annotations.map((ann, i) => (
            <motion.div
              key={i}
              className="flex items-center gap-2 rounded-md bg-surface px-2.5 py-1.5"
              style={{ borderLeft: `2px solid ${ann.color}` }}
              initial={{ opacity: 0, x: 20 }}
              animate={isInView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.3, delay: 0.6 + i * 0.2 }}
            >
              <span className="text-[11px] text-text-primary">{ann.text}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Score + Tags */}
      <div className="mt-4 flex items-center gap-3">
        <motion.div
          className="flex items-center gap-3"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.4, delay: 1.2 }}
        >
          <svg width={44} height={44} viewBox="0 0 44 44">
            <circle
              cx={22}
              cy={22}
              r={18}
              fill="none"
              stroke="#1F1F1F"
              strokeWidth={3}
            />
            <circle
              cx={22}
              cy={22}
              r={18}
              fill="none"
              stroke="#FF4400"
              strokeWidth={3}
              strokeDasharray={circumference}
              strokeDashoffset={circumference - strokeDash}
              strokeLinecap="round"
              transform="rotate(-90 22 22)"
              className="transition-all duration-100"
            />
          </svg>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-text-heading">
              {(scoreValue * scoreProgress).toFixed(1)}/10
            </span>
            <span className="text-[11px] text-green-400">
              Ready for interviews
            </span>
          </div>
        </motion.div>

        {/* Classification tags */}
        <motion.div
          className="ml-auto flex flex-wrap gap-1.5"
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.3, delay: 1.5 }}
        >
          <span className="rounded-full bg-[#1F1F1F] px-2 py-0.5 text-[10px] text-text-secondary">
            Binary Search
          </span>
          <span className="rounded-full bg-[#1F1F1F] px-2 py-0.5 text-[10px] text-text-secondary">
            Divide &amp; Conquer
          </span>
        </motion.div>
      </div>
    </BentoCard>
  );
}

/* ─── CARD 4: How It Works — Orange Icons + Traveling Dots ─── */

const steps = [
  {
    num: "1",
    title: "Connect",
    desc: "Connect your LeetCode account with one click.",
    icon: Link2,
  },
  {
    num: "2",
    title: "Analyze",
    desc: "We process every submission through our cognition engine.",
    icon: Cpu,
  },
  {
    num: "3",
    title: "Ask",
    desc: "Ask anything about your coding patterns and get instant insight.",
    icon: MessageSquare,
  },
];

function FlowingDots({ vertical = false }: { vertical?: boolean }) {
  return (
    <div
      className={`relative ${vertical ? "mx-auto h-12 w-px" : "h-px w-full"}`}
    >
      <div
        className={`absolute ${
          vertical ? "inset-x-0 inset-y-0" : "inset-x-0 inset-y-0"
        } ${vertical ? "border-l" : "border-t"} border-dashed border-border`}
      />
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="absolute h-[3px] w-[3px] rounded-full bg-accent"
          style={
            vertical
              ? { left: "50%", marginLeft: -1.5 }
              : { top: "50%", marginTop: -1.5 }
          }
          animate={
            vertical
              ? { y: [0, 48], opacity: [0, 1, 0] }
              : { x: ["0%", "100%"], opacity: [0, 1, 0] }
          }
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.6,
            ease: "linear",
          }}
        />
      ))}
    </div>
  );
}

function HowItWorksCard() {
  return (
    <BentoCard className="md:col-span-2" delay={0.45} id="how-it-works">
      <div className="mb-6">
        <CardLabel text="How It Works" />
        <CardTitle text="From connect to insights in minutes." />
      </div>

      {/* Desktop: horizontal */}
      <div className="hidden md:block">
        <div className="flex items-start gap-4">
          {steps.map((step, i) => (
            <div key={step.title} className="flex flex-1 flex-col items-center">
              <motion.div
                className="flex flex-col items-center text-center"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.3 + i * 0.3 }}
              >
                <span className="mb-3 text-5xl font-bold text-accent/80">
                  {step.num}
                </span>
                {/* Orange-tinted icon circle */}
                <div
                  className="mb-3 flex h-16 w-16 items-center justify-center rounded-full transition-transform duration-300 group-hover:scale-110"
                  style={{
                    backgroundColor: "rgba(255, 68, 0, 0.1)",
                    border: "1px solid rgba(255, 68, 0, 0.2)",
                  }}
                >
                  <step.icon size={28} className="text-accent" />
                </div>
                <h4 className="mb-1.5 text-lg font-semibold text-text-heading">
                  {step.title}
                </h4>
                <p className="max-w-[200px] text-sm text-text-secondary">
                  {step.desc}
                </p>
              </motion.div>
              {i < steps.length - 1 && (
                <div className="mt-4 w-full px-8">
                  <FlowingDots />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Mobile: vertical */}
      <div className="flex flex-col gap-2 md:hidden">
        {steps.map((step, i) => (
          <div key={step.title}>
            <motion.div
              className="flex items-center gap-4"
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.2 }}
            >
              <div
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full"
                style={{
                  backgroundColor: "rgba(255, 68, 0, 0.1)",
                  border: "1px solid rgba(255, 68, 0, 0.2)",
                }}
              >
                <step.icon size={22} className="text-accent" />
              </div>
              <div>
                <h4 className="text-base font-semibold text-text-heading">
                  {step.title}
                </h4>
                <p className="text-sm text-text-secondary">{step.desc}</p>
              </div>
            </motion.div>
            {i < steps.length - 1 && <FlowingDots vertical />}
          </div>
        ))}
      </div>
    </BentoCard>
  );
}

/* ─── CARD 5: Smart Recommendations — Node Glow + Pulse + AI Typewriter ─── */

function LearningPath() {
  const ref = useRef<SVGSVGElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    const start = performance.now();
    function animate(now: number) {
      const t = Math.min((now - start) / 2000, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setProgress(eased);
      if (t < 1) requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  }, [isInView]);

  const nodes = LEARNING_PATH_NODES;
  const nodeSpacing = 80;
  const startX = 40;
  const cy = 40;
  const svgWidth = startX * 2 + (nodes.length - 1) * nodeSpacing;

  return (
    <svg ref={ref} viewBox={`0 0 ${svgWidth} 90`} className="w-full">
      {/* Definitions for glow filters */}
      <defs>
        <filter id="completedGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="4" />
        </filter>
        <filter id="currentPulse" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="8" />
        </filter>
      </defs>

      {/* Connections */}
      {nodes.slice(0, -1).map((node, i) => {
        const x1 = startX + i * nodeSpacing + 20;
        const x2 = startX + (i + 1) * nodeSpacing - 20;
        const isCompleted = node.completed && !node.current;
        const lineProgress = Math.max(
          0,
          Math.min(1, progress * nodes.length - i)
        );

        return (
          <line
            key={i}
            x1={x1}
            y1={cy}
            x2={x2}
            y2={cy}
            stroke={isCompleted ? "#FF4400" : "#1F1F1F"}
            strokeWidth={2}
            strokeOpacity={isCompleted ? 0.3 * lineProgress : 0.5}
            strokeDasharray={isCompleted ? "none" : "4 4"}
          />
        );
      })}

      {/* Nodes */}
      {nodes.map((node, i) => {
        const nodeCx = startX + i * nodeSpacing;
        const nodeProgress = Math.max(
          0,
          Math.min(1, progress * nodes.length - i)
        );
        const isCompleted = node.completed && !node.current;
        const isCurrent = node.current;
        const nodeR = isCurrent ? 18 : 15;

        return (
          <g key={node.label}>
            {/* Glow behind completed nodes */}
            {isCompleted && (
              <circle
                cx={nodeCx}
                cy={cy}
                r={nodeR + 4}
                fill="rgba(255, 68, 0, 0.3)"
                opacity={nodeProgress * 0.5}
                filter="url(#completedGlow)"
              />
            )}

            {/* Dramatic pulse for current node */}
            {isCurrent && (
              <>
                <circle
                  cx={nodeCx}
                  cy={cy}
                  r={26}
                  fill="rgba(255, 68, 0, 0.15)"
                  filter="url(#currentPulse)"
                >
                  <animate
                    attributeName="r"
                    values="20;30;20"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                  <animate
                    attributeName="opacity"
                    values="0.4;0.1;0.4"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>
                <circle
                  cx={nodeCx}
                  cy={cy}
                  r={22}
                  fill="none"
                  stroke="#FF4400"
                  strokeWidth={1}
                  opacity={0.3}
                >
                  <animate
                    attributeName="r"
                    values="18;26;18"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                  <animate
                    attributeName="opacity"
                    values="0.4;0.1;0.4"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>
              </>
            )}

            {/* Node circle */}
            <circle
              cx={nodeCx}
              cy={cy}
              r={nodeR}
              fill={
                isCompleted
                  ? `rgba(255,68,0,${0.8 * nodeProgress})`
                  : "#1F1F1F"
              }
              stroke={
                isCurrent ? "#FF4400" : isCompleted ? "none" : "#71717A"
              }
              strokeWidth={isCurrent ? 2 : 1}
              opacity={0.3 + 0.7 * nodeProgress}
            />

            {/* Checkmark for completed */}
            {isCompleted && (
              <text
                x={nodeCx}
                y={cy + 1}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="#FFFDF1"
                fontSize={12}
                fontWeight={600}
                opacity={nodeProgress}
              >
                &#10003;
              </text>
            )}

            {/* Label */}
            <text
              x={nodeCx}
              y={cy + 32}
              textAnchor="middle"
              fill="#71717A"
              fontSize={11}
              style={{ fontFamily: "var(--font-geist-sans), sans-serif" }}
              opacity={0.3 + 0.7 * nodeProgress}
            >
              {node.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function SmartRecommendationsCard() {
  return (
    <BentoCard
      className="md:col-span-2 lg:col-start-1 lg:col-span-3 xl:col-start-1 xl:col-span-2 xl:mx-auto xl:max-w-2xl"
      delay={0.6}
    >
      <div className="mb-4">
        <CardLabel text="Recommendations" />
        <CardTitle text="Not random practice. Precision growth." />
        <CardDesc text="Our engine maps your weaknesses to the exact problems that will stretch you — in the right order, at the right difficulty." />
      </div>
      <div className="mt-6 overflow-x-auto">
        <LearningPath />
      </div>
      {/* AI Recommendation Typewriter */}
      <AITypewriter
        prefix="Generating personalized path..."
        lines={[
          {
            text: "Next: Sliding Window — 3 problems queued",
            color: "#FF4400",
          },
          {
            text: "Confidence: 72% → target 90% before advancing",
            color: "#71717A",
          },
          { text: "Estimated mastery: 5 focused sessions", color: "#22c55e" },
        ]}
      />
    </BentoCard>
  );
}

/* ─── Cursor Glow Effect (Desktop only) ─── */

function CursorGlow() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Only on desktop (pointer: fine)
    if (!window.matchMedia("(pointer: fine)").matches) return;

    function onMove(e: MouseEvent) {
      const rect = container!.getBoundingClientRect();
      setPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
      setVisible(true);
    }
    function onLeave() {
      setVisible(false);
    }

    container.addEventListener("mousemove", onMove);
    container.addEventListener("mouseleave", onLeave);
    return () => {
      container.removeEventListener("mousemove", onMove);
      container.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  return (
    <>
      <div ref={containerRef} className="absolute inset-0 z-0" />
      {visible && (
        <div
          className="pointer-events-none absolute z-0"
          style={{
            left: pos.x - 200,
            top: pos.y - 200,
            width: 400,
            height: 400,
            background:
              "radial-gradient(circle, rgba(255, 68, 0, 0.04) 0%, transparent 70%)",
            transition: "left 0.05s linear, top 0.05s linear",
          }}
        />
      )}
    </>
  );
}

/* ─── Features Grid (Main Export) ─── */

export default function FeaturesGrid() {
  return (
    <section id="features" className="relative px-5 py-[140px] md:px-12">
      {/* Cursor glow */}
      <CursorGlow />

      <div className="relative z-10 mx-auto max-w-6xl">
        {/* Section header */}
        <motion.div
          className="mb-20 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
        >
          <span className="mb-4 inline-block text-[13px] font-medium uppercase tracking-[0.1em] text-accent">
            Features
          </span>
          <h2 className="mb-4 text-3xl font-semibold tracking-[-0.02em] text-text-heading md:text-[40px] md:leading-tight">
            Everything your LeetCode profile
            <br />
            doesn&apos;t tell you.
          </h2>
          <p className="mx-auto max-w-[600px] text-base leading-relaxed text-text-secondary md:text-lg">
            Four intelligent systems that analyze your code, understand your
            patterns, and accelerate your growth.
          </p>
        </motion.div>

        {/* Bento grid */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <WeaknessDiagnosisCard />
          <SolutionComparisonCard />
          <CodeAnalysisCard />
          <HowItWorksCard />
          <SmartRecommendationsCard />
        </div>
      </div>
    </section>
  );
}
