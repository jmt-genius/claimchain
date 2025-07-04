"use client";
import React from "react";
import { motion } from "framer-motion";

interface ShinyTextProps {
  text: string;
  className?: string;
  shimmerWidth?: number;
}

export function ShinyText({ 
  text, 
  className = "", 
  shimmerWidth = 100 
}: ShinyTextProps) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <span className="relative z-10">{text}</span>
      <motion.div
        className="absolute inset-0 -top-0 -bottom-0 w-full"
        style={{
          background: `linear-gradient(110deg, transparent 25%, rgba(255,255,255,0.5) 50%, transparent 75%)`,
          width: `${shimmerWidth}%`,
        }}
        animate={{
          x: ["-100%", "100%"],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "linear",
        }}
      />
    </div>
  );
}