"use client";
import React, { useId } from "react";
import { useEffect, useState } from "react";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import type { Container } from "@tsparticles/engine";
import { loadSlim } from "@tsparticles/slim";
import { cn } from "@/lib/utils";
import { motion, useAnimation } from "motion/react";

type ParticlesProps = {
  id?: string;
  className?: string;
  background?: string;
  particleSize?: number;
  minSize?: number;
  maxSize?: number;
  speed?: number;
  particleColor?: string;
  particleDensity?: number;
};

interface SparklesProps extends ParticlesProps {
  children?: React.ReactNode;
}

export const SparklesCore = (props: ParticlesProps) => {
  const {
    id,
    className,
    background,
    minSize,
    maxSize,
    speed,
    particleColor,
    particleDensity,
  } = props;
  const [init, setInit] = useState(false);
  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    }).then(() => {
      setInit(true);
    });
  }, []);
  const controls = useAnimation();

  const particlesLoaded = async (container?: Container) => {
    if (container) {
      controls.start({
        opacity: 1,
        transition: {
          duration: 0.8,
        },
      });
    }
  };

  const generatedId = useId();
  return (
    <motion.div animate={controls} className={cn("opacity-0", className)}>
      {init && (
        <Particles
          id={id || generatedId}
          className={cn("h-full w-full")}
          particlesLoaded={particlesLoaded}
          options={{
            background: {
              color: {
                value: background || "transparent",
              },
            },
            fullScreen: {
              enable: false,
              zIndex: 1,
            },
            fpsLimit: 60,
            interactivity: {
              events: {
                onClick: {
                  enable: true,
                  mode: "push",
                },
                onHover: {
                  enable: true,
                  mode: "repulse",
                },
                resize: true as any,
              },
              modes: {
                push: {
                  quantity: 4,
                },
                repulse: {
                  distance: 150,
                  duration: 0.4,
                },
              },
            },
            particles: {
              color: {
                value: particleColor || "#FFFFFF",
              },
              move: {
                direction: "none",
                enable: true,
                outModes: {
                  default: "bounce",
                  bottom: "bounce",
                  left: "bounce",
                  right: "bounce",
                  top: "bounce"
                },
                random: true,
                speed: speed || 1,
                straight: false,
              },
              number: {
                density: {
                  enable: true,
                  width: 1000,
                  height: 1000,
                },
                value: particleDensity || 60,
                limit: {
                  value: particleDensity || 60
                },
              },
              opacity: {
                value: {
                  min: 0.1,
                  max: 0.5,
                },
                animation: {
                  enable: true,
                  speed: 1,
                  startValue: "random",
                  sync: false,
                },
              },
              size: {
                value: {
                  min: minSize || 1,
                  max: maxSize || 2,
                },
                animation: {
                  enable: true,
                  speed: 1,
                  startValue: "random",
                  sync: false,
                },
              },
              shape: {
                type: "circle",
              },
              collisions: {
                enable: true,
                bounce: {
                  horizontal: {
                    value: 1
                  },
                  vertical: {
                    value: 1
                  }
                },
              }
            },
            detectRetina: true,
          }}
        />
      )}
    </motion.div>
  );
};

export const Sparkles: React.FC<SparklesProps> = ({ children, ...props }) => {
  return (
    <div className="relative w-full">
      <SparklesCore
        className="absolute inset-0 h-full w-full"
        {...props}
      />
      {children && (
        <div className="relative z-10">{children}</div>
      )}
    </div>
  );
};

export default Sparkles;
