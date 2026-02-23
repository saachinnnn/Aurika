"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";

interface AITypewriterProps {
  prefix?: string;
  lines: { text: string; color?: string }[];
  speed?: number;
}

export default function AITypewriter({
  prefix = "Analyzing 708 submissions...",
  lines,
  speed = 30,
}: AITypewriterProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const [displayed, setDisplayed] = useState("");
  const [typing, setTyping] = useState(false);
  const [cursorVisible, setCursorVisible] = useState(true);
  const [done, setDone] = useState(false);

  const fullText = lines.map((l) => l.text).join("\n");

  useEffect(() => {
    if (!isInView || done) return;
    setTyping(true);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(fullText.slice(0, i));
      if (i >= fullText.length) {
        clearInterval(interval);
        setTyping(false);
        // Blink cursor 2 more seconds then fade
        setTimeout(() => setCursorVisible(false), 2000);
        setDone(true);
      }
    }, 1000 / speed);
    return () => clearInterval(interval);
  }, [isInView, fullText, speed, done]);

  // Cursor blink
  const [cursorOn, setCursorOn] = useState(true);
  useEffect(() => {
    if (!typing && !cursorVisible) return;
    const blink = setInterval(() => setCursorOn((v) => !v), 530);
    return () => clearInterval(blink);
  }, [typing, cursorVisible]);

  // Map displayed text back to lines with colors
  let charIndex = 0;
  const renderedLines = lines.map((line) => {
    const start = charIndex;
    charIndex += line.text.length + 1; // +1 for \n
    const visiblePart = displayed.slice(start, start + line.text.length);
    return { ...line, visibleText: visiblePart };
  });

  return (
    <div
      ref={ref}
      className="mt-4 rounded-xl border border-border bg-[#0A0A0A] p-4 font-mono text-xs leading-relaxed"
    >
      <div className="mb-2 text-accent">
        <span className="mr-1">&#9889;</span>
        {prefix}
      </div>
      <div>
        {renderedLines.map((line, i) => (
          <span key={i} style={{ color: line.color || "#D4D4D8" }}>
            {line.visibleText}
            {i < renderedLines.length - 1 && line.visibleText.length >= line.text.length && (
              <br />
            )}
          </span>
        ))}
        {cursorVisible && (
          <span
            className="ml-px inline-block w-[6px] align-middle"
            style={{
              height: "14px",
              backgroundColor: cursorOn ? "#FF4400" : "transparent",
              transition: "background-color 0.1s",
            }}
          />
        )}
      </div>
    </div>
  );
}
