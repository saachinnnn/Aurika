"use client";

import { motion } from "framer-motion";
import Button from "@/components/ui/Button";
import GlowEffect from "@/components/ui/GlowEffect";

export default function FinalCTA() {
  return (
    <section className="relative overflow-hidden px-5 pb-[120px] pt-[180px] md:px-12">
      {/* Orange glow */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <GlowEffect width={800} height={500} intensity="strong" />
      </div>

      <motion.div
        className="relative z-10 mx-auto max-w-2xl text-center"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.3 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
      >
        <h2 className="mb-6 text-3xl font-bold tracking-tight text-text-heading md:text-[44px] md:leading-tight">
          Ready to understand your code?
        </h2>
        <p className="mb-10 text-base text-text-secondary md:text-lg">
          Join hundreds of programmers who&apos;ve unlocked their coding
          patterns.
        </p>
        <Button href="#" size="lg">
          Get Started — It&apos;s Free <span aria-hidden="true">&rarr;</span>
        </Button>
        <p className="mt-4 text-[13px] text-text-secondary">
          No credit card required &middot; Takes 30 seconds
        </p>
      </motion.div>
    </section>
  );
}
