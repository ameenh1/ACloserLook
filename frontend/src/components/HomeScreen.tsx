import { useEffect, useState } from "react";
import img2 from "figma:asset/d571e3dce4defe6c21b77ea653882f35e55dba90.png";
import img12 from "figma:asset/3e71b2e76e3163500ce459fc35ad01faa42108fa.png";
import img10 from "figma:asset/8331fbee660e6ce05a6f827bee5684e2c298681b.png";

interface HomeScreenProps {
  onLogin: () => void;
  onCreateAccount: () => void;
}

export default function HomeScreen({ onLogin, onCreateAccount }: HomeScreenProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation after component mounts
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
      {/* Bottom left flower */}
      <div className="absolute flex h-[292.001px] items-center justify-center left-[-118px] top-[591px] w-[402.971px]" style={{ "--transform-inner-width": "1200", "--transform-inner-height": "21.328125" } as React.CSSProperties}>
        <div className="-scale-y-100 flex-none rotate-[-175.33deg]">
          <div className="h-[261.715px] relative w-[382.949px]" data-name="2">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <img alt="" className="absolute h-full left-[-7.1%] max-w-none top-0 w-[121.92%]" src={img2} />
            </div>
          </div>
        </div>
      </div>
      
      {/* Top left flower */}
      <div className="absolute flex h-[445.107px] items-center justify-center left-[-162px] top-[-140px] w-[461.537px]" style={{ "--transform-inner-width": "1200", "--transform-inner-height": "21.328125" } as React.CSSProperties}>
        <div className="flex-none rotate-[139.41deg]">
          <div className="h-[246px] relative w-[397px]" data-name="12">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={img12} />
          </div>
        </div>
      </div>
      
      {/* Right flower */}
      <div className="absolute flex h-[432.819px] items-center justify-center left-[162px] top-[279px] w-[413px]" style={{ "--transform-inner-width": "1200", "--transform-inner-height": "21.328125" } as React.CSSProperties}>
        <div className="flex-none rotate-[-51.03deg]">
          <div className="h-[234.018px] relative w-[367.396px]" data-name="10">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full" src={img10} />
          </div>
        </div>
      </div>
      
      {/* Title */}
      <p 
        className="absolute font-['Konkhmer_Sleokchher:Regular',sans-serif] font-extrabold h-[60px] leading-[normal] left-[59px] not-italic text-[40px] text-white top-[256px] tracking-[-2px] w-[275px] whitespace-pre-wrap text-center"
        style={{
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 1.5s ease-in-out',
        }}
      >A Closer Look</p>
      
      {/* Subtitle */}
      <p 
        className="absolute font-['Konkhmer_Sleokchher:Regular',sans-serif] font-extrabold h-[87px] leading-[normal] not-italic text-[13px] text-white top-[316px] tracking-[-0.65px] w-[236px] whitespace-pre-wrap text-center"
        style={{
          left: '50%', 
          transform: 'translateX(-50%)',
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 1.5s ease-in-out 0.3s',
        }}
      >Know what you're putting down there</p>
      
      {/* Login Button */}
      <button 
        onClick={onLogin}
        className="absolute bg-[#a380a8] h-[40px] rounded-[10px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25),0px_4px_4px_0px_rgba(0,0,0,0.25)] top-[351px] w-[130px] hover:bg-[#8d6d91] active:scale-95"
        style={{
          left: '50%', 
          transform: 'translateX(-50%)',
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 1.2s ease-in-out 0.6s, background-color 0.15s',
        }}
      >
        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] leading-[normal] not-italic text-[13px] text-white tracking-[-0.65px]">Login</p>
      </button>
      
      {/* Create Account Button */}
      <button 
        onClick={onCreateAccount}
        className="absolute bg-[#a380a8] h-[40px] rounded-[10px] top-[403px] w-[130px] hover:bg-[#8d6d91] active:scale-95"
        style={{
          left: '50%', 
          transform: 'translateX(-50%)',
          opacity: isVisible ? 1 : 0,
          transition: 'opacity 1.2s ease-in-out 0.8s, background-color 0.15s',
        }}
      >
        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] leading-[normal] not-italic text-[13px] text-white tracking-[-0.65px]">Create Account</p>
      </button>
    </div>
  );
}