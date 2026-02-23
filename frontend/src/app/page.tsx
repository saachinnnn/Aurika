"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Navbar from "@/components/home/Navbar";
import Hero from "@/components/home/Hero";
import FeaturesGrid from "@/components/home/FeaturesGrid";
import StatsSection from "@/components/home/StatsSection";
import FinalCTA from "@/components/home/FinalCTA";
import Footer from "@/components/home/Footer";

function ScrollProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const total = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(total > 0 ? window.scrollY / total : 0);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="fixed top-0 left-0 right-0 z-[60] h-[2px]">
      <div
        className="h-full bg-accent"
        style={{ width: `${progress * 100}%`, transition: "width 0.05s linear" }}
      />
    </div>
  );
}

export default function Home() {
  return (
    <motion.main
      className="min-h-screen bg-background"
      initial={{ backgroundColor: "#000000" }}
      animate={{ backgroundColor: "#0A0A0A" }}
      transition={{ duration: 0.3 }}
    >
      <div className="noise-overlay" />
      <ScrollProgress />
      <Navbar />
      <Hero />
      <FeaturesGrid />
      <StatsSection />
      <FinalCTA />
      <Footer />
    </motion.main>
  );
}
