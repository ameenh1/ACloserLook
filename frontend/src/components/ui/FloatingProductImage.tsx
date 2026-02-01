import { motion } from "framer-motion";

interface FloatingProductImageProps {
  src: string;
  alt: string;
  size?: number;
}

export function FloatingProductImage({ src, alt, size = 85 }: FloatingProductImageProps) {
  return (
    <motion.div
      className="absolute -right-2 z-30"
      animate={{ y: [0, -8, 0] }}
      transition={{
        repeat: Infinity,
        duration: 4,
        ease: "easeInOut"
      }}
      style={{
        top: '70px',
        width: size,
        height: size,
        willChange: "transform"
      }}
    >
      <img 
        src={src} 
        alt={alt}
        className="w-full h-full object-contain rounded-[10px] shadow-lg"
        style={{ 
          filter: "drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4))"
        }}
      />
    </motion.div>
  );
}
