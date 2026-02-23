"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, ChevronDown } from "lucide-react";
import Button from "@/components/ui/Button";
import { NAV_LINKS, RESOURCES_LINKS } from "@/lib/constants";

function ResourcesDropdown() {
  const [open, setOpen] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  function enter() {
    clearTimeout(timeoutRef.current);
    setOpen(true);
  }
  function leave() {
    timeoutRef.current = setTimeout(() => setOpen(false), 150);
  }

  return (
    <div className="relative" onMouseEnter={enter} onMouseLeave={leave}>
      <button className="group/link relative flex items-center gap-1 py-1 text-sm text-text-secondary transition-colors duration-300 hover:text-text-heading">
        Resources
        <ChevronDown
          size={14}
          className={`transition-transform duration-200 ${open ? "rotate-180" : ""}`}
        />
        <span className="absolute bottom-0 left-0 h-px w-0 bg-text-heading transition-all duration-300 group-hover/link:w-full" />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="absolute left-1/2 top-full pt-2"
            style={{ transform: "translateX(-50%)" }}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
          >
            <div className="w-52 overflow-hidden rounded-xl border border-border bg-[#141414] py-1.5 shadow-xl">
              {RESOURCES_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="block px-4 py-2 text-sm text-text-secondary transition-colors duration-200 hover:bg-[#1F1F1F] hover:text-text-heading"
                >
                  {link.label}
                </a>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <motion.nav
      className="fixed top-0 left-0 right-0 z-50 h-16"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <div
        className="absolute inset-0 transition-all duration-300"
        style={{
          backgroundColor: scrolled ? "rgba(10, 10, 10, 0.95)" : "transparent",
          backdropFilter: scrolled ? "blur(12px)" : "none",
        }}
      />
      {/* Separator line — always visible */}
      <div
        className="absolute bottom-0 left-0 right-0 h-px transition-colors duration-300"
        style={{
          backgroundColor: scrolled ? "#1F1F1F" : "rgba(255,255,255,0.06)",
        }}
      />

      <div className="relative mx-auto flex h-full max-w-7xl items-center justify-between px-5 md:px-12">
        {/* Logo */}
        <a href="#" className="group flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent transition-shadow duration-300 group-hover:shadow-[0_0_16px_rgba(255,68,0,0.3)]">
            <span className="text-sm font-bold text-text-heading">A</span>
          </div>
          <span className="text-xl font-bold text-text-heading transition-[text-shadow] duration-300 group-hover:[text-shadow:0_0_20px_rgba(255,68,0,0.2)]">
            Aurika
          </span>
        </a>

        {/* Desktop nav */}
        <div className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="group/link relative py-1 text-sm text-text-secondary transition-colors duration-300 hover:text-text-heading"
            >
              {link.label}
              <span className="absolute bottom-0 left-0 h-px w-0 bg-text-heading transition-all duration-300 group-hover/link:w-full" />
            </a>
          ))}
          <ResourcesDropdown />
          <Button href="#" size="sm">
            Get Started Free <span aria-hidden="true">&rarr;</span>
          </Button>
        </div>

        {/* Mobile toggle */}
        <button
          className="text-text-secondary transition-colors hover:text-text-heading md:hidden"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="absolute top-16 left-0 right-0 border-b border-border bg-background/95 backdrop-blur-xl md:hidden"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex flex-col gap-4 px-5 py-6">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-base text-text-secondary transition-colors hover:text-text-heading"
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              {/* Resources links flattened on mobile */}
              <span className="text-xs font-medium uppercase tracking-wider text-text-secondary/50">
                Resources
              </span>
              {RESOURCES_LINKS.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="text-base text-text-secondary transition-colors hover:text-text-heading"
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              <Button href="#" size="sm">
                Get Started Free <span aria-hidden="true">&rarr;</span>
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
