import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface AnimatedScoreRingProps {
  score: number; // 0-100
  size?: number;
}

export function AnimatedScoreRing({ score, size = 60 }: AnimatedScoreRingProps) {
  const [animatedScore, setAnimatedScore] = useState(0);
  
  // Determine color based on score
  const getColor = (value: number) => {
    if (value >= 71) return "#4ade80"; // green
    if (value >= 41) return "#facc15"; // yellow
    return "#f87171"; // red
  };

  const color = getColor(score);
  const radius = 25;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (circumference * score) / 100;

  useEffect(() => {
    // Animate score number counting up
    const duration = 1000; // 1 second
    const steps = 30;
    const increment = score / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score]);

  return (
    <div className="relative" style={{ width: size, height: size }}>
      {/* SVG Circular Progress */}
      <svg 
        className="w-full h-full -rotate-90" 
        viewBox="0 0 60 60"
        style={{ filter: `drop-shadow(0 0 8px ${color})` }}
      >
        {/* Define gradient */}
        <defs>
          <linearGradient id={`scoreGradient-${score}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#f87171" />
            <stop offset="50%" stopColor="#facc15" />
            <stop offset="100%" stopColor="#4ade80" />
          </linearGradient>
        </defs>
        
        {/* Background circle */}
        <circle
          cx="30"
          cy="30"
          r={radius}
          fill="none"
          stroke="rgba(80, 80, 80, 0.5)"
          strokeWidth="5"
        />
        
        {/* Animated progress circle */}
        <motion.circle
          cx="30"
          cy="30"
          r={radius}
          fill="none"
          strokeWidth="5"
          strokeLinecap="round"
          stroke={color}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </svg>
      
      {/* Score Number in Center */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.span 
          className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] font-bold"
          style={{ color }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.3 }}
        >
          {animatedScore}/100
        </motion.span>
      </div>
    </div>
  );
}
