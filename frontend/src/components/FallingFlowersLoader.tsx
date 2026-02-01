import { useState, useEffect } from "react";

// Import all flower assets
import flower1 from "figma:asset/02505e701d70c92bf6d6dc21dc3e5e3036acc42d.png";
import flower2 from "figma:asset/15822d0d5d333944328a5265ff0f4b30240d07a8.png";
import flower3 from "figma:asset/3e71b2e76e3163500ce459fc35ad01faa42108fa.png";
import flower4 from "figma:asset/52881dd04b184a3ea94b5eb479b6c16709b2a515.png";
import flower5 from "figma:asset/59fcaadf037f47085e2010b0e6a876b4307d5d84.png";
import flower6 from "figma:asset/6e4a41e6bc8c632007a3be70ab1f910b722fc541.png";
import flower7 from "figma:asset/751545583700d5578b852ae7b0f5871e0723ff44.png";
import flower8 from "figma:asset/8331fbee660e6ce05a6f827bee5684e2c298681b.png";
import flower9 from "figma:asset/92e777b5af772d28e9ce487aa4ff2ce69208100c.png";
import flower10 from "figma:asset/cffb2f56518ee28837d39e5cbdba5ce95a23d7a0.png";
import flower11 from "figma:asset/d4d40c58bbd603e907bcf97d939af54f73bf95c2.png";
import flower12 from "figma:asset/d571e3dce4defe6c21b77ea653882f35e55dba90.png";
import flower13 from "figma:asset/e153f9d3e6a9dfd2dd435434c4341330f8e8ab0c.png";
import "./FallingFlowersLoader.css";

interface FloatingFlower {
  id: number;
  src: string;
  left: number;
  delay: number;
  duration: number;
  scale: number;
}

export default function FallingFlowersLoader() {
  const flowers = [flower1, flower2, flower3, flower4, flower5, flower6, flower7, flower8, flower9, flower10, flower11, flower12, flower13];
  const [fallingFlowers, setFallingFlowers] = useState<FloatingFlower[]>([]);

  useEffect(() => {
    // Generate random falling flowers
    const generateFlowers = () => {
      const newFlowers: FloatingFlower[] = [];
      for (let i = 0; i < 20; i++) {
        newFlowers.push({
          id: i,
          src: flowers[Math.floor(Math.random() * flowers.length)],
          left: Math.random() * 100,
          delay: Math.random() * 3,
          duration: 5 + Math.random() * 3,
          scale: 0.4 + Math.random() * 0.6,
        });
      }
      setFallingFlowers(newFlowers);
    };

    generateFlowers();
  }, []);

  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden flex items-center justify-center">
      {/* Animated falling flowers background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {fallingFlowers.map((flower) => (
          <div
            key={flower.id}
            className="falling-flower"
            style={{
              left: `${flower.left}%`,
              top: "-100px",
              width: `${120 * flower.scale}px`,
              height: `${120 * flower.scale}px`,
              animationDuration: `${flower.duration}s`,
              animationDelay: `${flower.delay}s`,
            }}
          >
            <img
              src={flower.src}
              alt="falling flower"
              className="w-full h-full object-contain"
              style={{
                filter: "drop-shadow(0 0 15px rgba(163, 128, 168, 0.7))",
              }}
            />
          </div>
        ))}
      </div>

      {/* Loading message center */}
      <div className="relative z-10 text-center pointer-events-none">
        <div className="mb-6">
          <div className="inline-flex items-center justify-center">
            <div className="w-12 h-12 rounded-full border-3 border-[#a380a8] border-t-white animate-spin"></div>
          </div>
        </div>
        <h2 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[22px] text-white tracking-[-1px] mb-2">
          Analyzing Product
        </h2>
        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white/60 tracking-[-0.65px]">
          Finding ingredients and health info...
        </p>
      </div>
    </div>
  );
}
