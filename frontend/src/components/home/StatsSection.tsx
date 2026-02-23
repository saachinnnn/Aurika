"use client";

import { motion } from "framer-motion";
import AnimatedCounter from "@/components/ui/AnimatedCounter";
import { STATS } from "@/lib/constants";

export default function StatsSection() {
  return (
    <section className="px-5 pt-[100px] pb-[80px] md:px-12">
      <div className="mx-auto max-w-[900px]">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4 md:gap-0">
          {STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              className="relative flex flex-col items-center text-center"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.5 }}
              transition={{ duration: 0.6, delay: i * 0.15, ease: "easeOut" }}
            >
              {/* Divider (between stats on desktop) */}
              {i > 0 && (
                <div className="absolute left-0 top-1/2 hidden h-10 w-px -translate-y-1/2 bg-border md:block" />
              )}
              <span className="text-5xl font-bold text-text-heading">
                <AnimatedCounter target={stat.value} delay={i * 0.15} />
              </span>
              <span className="mt-2 text-sm text-text-secondary">
                {stat.label}
              </span>
            </motion.div>
          ))}
        </div>
        <motion.p
          className="mt-5 text-center text-sm italic text-text-secondary"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          and counting...
        </motion.p>
      </div>
    </section>
  );
}
