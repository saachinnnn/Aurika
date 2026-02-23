"use client";

import { Github, Twitter, MessageCircle } from "lucide-react";
import { SOCIAL_LINKS } from "@/lib/constants";

const iconMap: Record<string, React.ElementType> = {
  GitHub: Github,
  Twitter: Twitter,
  Discord: MessageCircle,
};

export default function Footer() {
  return (
    <footer className="border-t border-border bg-background px-5 py-16 md:px-12">
      <div className="mx-auto max-w-6xl">
        {/* Row 1 */}
        <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
          {/* Logo */}
          <a href="#" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
              <span className="text-sm font-bold text-text-heading">A</span>
            </div>
            <span className="text-xl font-bold text-text-heading">Aurika</span>
          </a>

          {/* Social links */}
          <div className="flex items-center gap-5">
            {SOCIAL_LINKS.map((link) => {
              const Icon = iconMap[link.label];
              return (
                <a
                  key={link.label}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-text-secondary transition-colors duration-300 hover:text-text-primary"
                  aria-label={link.label}
                >
                  <Icon size={20} />
                </a>
              );
            })}
          </div>
        </div>

        {/* Divider */}
        <div className="my-8 h-px bg-border" />

        {/* Row 2 */}
        <div className="flex flex-col items-center justify-between gap-4 text-[13px] text-text-secondary md:flex-row">
          <span>&copy; 2025 Aurika. All rights reserved.</span>
          <div className="flex items-center gap-4">
            <a href="#" className="transition-colors hover:text-text-primary">
              Privacy
            </a>
            <a href="#" className="transition-colors hover:text-text-primary">
              Terms
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
