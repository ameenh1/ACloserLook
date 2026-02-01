import img2 from "figma:asset/d571e3dce4defe6c21b77ea653882f35e55dba90.png";
import img10 from "figma:asset/8331fbee660e6ce05a6f827bee5684e2c298681b.png";
import { Scan, User, LogOut } from "lucide-react";
import RecentScansDropdown from "./RecentScansDropdown";

interface HomePageScreenProps {
  onScanProduct: (barcode?: string) => void;
  onLogout: () => void;
  onProfile: () => void;
}

export default function HomePageScreen({ onScanProduct, onLogout, onProfile }: HomePageScreenProps) {
  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
      {/* Top right flower decoration */}
      <div className="absolute flex h-[350px] items-center justify-center left-[120px] top-[-100px] w-[400px] pointer-events-none">
        <div className="flex-none rotate-[145deg]">
          <div className="h-[220px] relative w-[350px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-40" src={img10} />
          </div>
        </div>
      </div>

      {/* Bottom left flower decoration */}
      <div className="absolute flex h-[320px] items-center justify-center left-[-130px] top-[580px] w-[420px] pointer-events-none">
        <div className="-scale-y-100 flex-none rotate-[-175deg]">
          <div className="h-[260px] relative w-[380px]">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <img alt="" className="absolute h-full left-[-7%] max-w-none top-0 w-[120%] opacity-40" src={img2} />
            </div>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="absolute top-[60px] left-[24px] right-[24px] flex items-center justify-end z-10">
        <button
          onClick={onLogout}
          className="text-white hover:text-[#a380a8] transition-colors"
        >
          <LogOut size={24} />
        </button>
      </div>

      {/* Main Content */}
      <div className="absolute top-[200px] left-[40px] right-[40px] z-10">
        <div className="text-center mb-12">
          <h2 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] font-bold text-[32px] text-white tracking-[-1.5px] leading-[0.9]">
            Know What You're<br />Using
          </h2>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/80 tracking-[-0.65px] mt-3">Scan any feminine care product to learn about its ingredients and safety</p>
        </div>

        {/* Scan Button */}
        <button
          onClick={() => onScanProduct()}
          className="w-full h-[140px] bg-gradient-to-br from-[#a380a8] to-[#8d6d91] rounded-[20px] shadow-[0px_8px_16px_0px_rgba(163,128,168,0.3)] hover:shadow-[0px_12px_24px_0px_rgba(163,128,168,0.4)] transition-all active:scale-95 flex flex-col items-center justify-center gap-3"
        >
          <div className="bg-white/20 rounded-full p-4">
            <Scan size={48} className="text-white" strokeWidth={1.5} />
          </div>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[20px] text-white tracking-[-0.8px]">Scan Product</p>
        </button>

        {/* Info Cards */}
        <div className="mt-8 space-y-3">
          <RecentScansDropdown onScanClick={(barcode) => onScanProduct(barcode)} />

          <div className="bg-white/5 border border-white/10 rounded-[12px] p-4">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px] mb-2">Safety Tips</h3>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/60 tracking-[-0.6px]">Look for products free of fragrances and harsh chemicals</p>
          </div>
        </div>
      </div>

      {/* Profile Button */}
      <button className="absolute bottom-[40px] right-[40px] bg-[#a380a8] rounded-full p-4 shadow-[0px_4px_12px_0px_rgba(0,0,0,0.3)] hover:bg-[#8d6d91] transition-colors z-10" onClick={onProfile}>
        <User size={24} className="text-white" />
      </button>
    </div>
  );
}