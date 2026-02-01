import { motion } from "framer-motion";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  animated?: boolean;
}

export function GlassCard({ children, className = "", animated = true }: GlassCardProps) {
  const cardClasses = `
    relative rounded-[20px] p-6
    backdrop-blur-xl bg-white/10
    border border-white/30
    ${className}
  `.trim();

  if (animated) {
    return (
      <motion.div
        className={cardClasses}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        {/* Gradient border effect */}
        <div className="absolute inset-0 rounded-[20px] bg-gradient-to-br from-white/30 via-transparent to-transparent pointer-events-none" style={{ padding: '1px', WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)', WebkitMaskComposite: 'xor', maskComposite: 'exclude' }} />
        {children}
      </motion.div>
    );
  }

  return (
    <div className={cardClasses}>
      {/* Gradient border effect */}
      <div className="absolute inset-0 rounded-[20px] bg-gradient-to-br from-white/30 via-transparent to-transparent pointer-events-none" style={{ padding: '1px', WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)', WebkitMaskComposite: 'xor', maskComposite: 'exclude' }} />
      {children}
    </div>
  );
}
