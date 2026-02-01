import { motion } from "framer-motion";

interface HealthWarningPillProps {
  name: string;
  reason: string;
  severity: "High Risk" | "Caution";
}

export function HealthWarningPill({ name, reason, severity }: HealthWarningPillProps) {
  const isHighRisk = severity === "High Risk";
  
  const bgColor = isHighRisk ? "bg-red-500/20" : "bg-yellow-500/20";
  const textColor = isHighRisk ? "text-red-400" : "text-yellow-400";
  const dotColor = isHighRisk ? "#f87171" : "#facc15";

  return (
    <motion.div 
      className={`${bgColor} rounded-[10px] p-3 border border-white/10`}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          {/* Pulsing dot indicator */}
          <motion.div
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: dotColor }}
            animate={{ scale: [1, 1.3, 1], opacity: [1, 0.6, 1] }}
            transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          />
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">
            {name}
          </p>
        </div>
        <span className={`font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[10px] px-2 py-0.5 rounded-full ${bgColor} ${textColor}`}>
          {severity}
        </span>
      </div>
      <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-white/80 tracking-[-0.5px] ml-4">
        {reason}
      </p>
    </motion.div>
  );
}
