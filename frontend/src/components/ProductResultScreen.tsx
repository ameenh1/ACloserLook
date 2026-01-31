import img12 from "figma:asset/3e71b2e76e3163500ce459fc35ad01faa42108fa.png";
import img3 from "figma:asset/d4d40c58bbd603e907bcf97d939af54f73bf95c2.png";
import { ArrowLeft, CheckCircle, AlertTriangle, XCircle } from "lucide-react";

interface ProductResultScreenProps {
  barcode: string;
  onBack: () => void;
  onScanAnother: () => void;
}

export default function ProductResultScreen({ barcode, onBack, onScanAnother }: ProductResultScreenProps) {
  // Mock product data based on barcode
  const mockProduct = {
    name: "Organic Cotton Tampons",
    brand: "Pure Care",
    barcode: barcode,
    safetyRating: "Safe",
    ratingColor: "#4ade80",
    ingredients: [
      { name: "100% Organic Cotton", status: "safe" },
      { name: "No Fragrances", status: "safe" },
      { name: "No Dyes", status: "safe" },
      { name: "No Chlorine Bleach", status: "safe" },
    ],
    warnings: [],
    recommendations: "This product is made with safe, natural materials and is recommended for sensitive skin."
  };

  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
      {/* Top flower decoration */}
      <div className="absolute flex h-[280px] items-center justify-center left-[-90px] top-[-80px] w-[350px] pointer-events-none">
        <div className="flex-none rotate-[135deg]">
          <div className="h-[180px] relative w-[300px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-30" src={img12} />
          </div>
        </div>
      </div>

      {/* Bottom right flower decoration */}
      <div className="absolute flex h-[260px] items-center justify-center left-[150px] top-[640px] w-[320px] pointer-events-none">
        <div className="flex-none rotate-[-45deg]">
          <div className="h-[160px] relative w-[280px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-30" src={img3} />
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="absolute top-[60px] left-[24px] right-[24px] z-10">
        <button 
          onClick={onBack}
          className="text-white flex items-center gap-2 hover:text-[#a380a8] transition-colors mb-6"
        >
          <ArrowLeft size={24} />
          <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] tracking-[-0.65px]">Back to Home</span>
        </button>

        <h1 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[28px] text-white tracking-[-1.5px] mb-2">Product Analysis</h1>
        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/60 tracking-[-0.6px]">Barcode: {barcode}</p>
      </div>

      {/* Content */}
      <div className="absolute top-[180px] left-[24px] right-[24px] bottom-[100px] overflow-y-auto z-10">
        {/* Product Info */}
        <div className="bg-white/5 border border-white/10 rounded-[16px] p-5 mb-4">
          <h2 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[20px] text-white tracking-[-0.8px] mb-1">{mockProduct.name}</h2>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white/70 tracking-[-0.65px]">{mockProduct.brand}</p>
        </div>

        {/* Safety Rating */}
        <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 rounded-[16px] p-5 mb-4">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle size={28} className="text-green-400" />
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[18px] text-white tracking-[-0.8px]">Safe to Use</h3>
          </div>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/80 tracking-[-0.65px]">{mockProduct.recommendations}</p>
        </div>

        {/* Ingredients */}
        <div className="bg-white/5 border border-white/10 rounded-[16px] p-5 mb-4">
          <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">Ingredients</h3>
          <div className="space-y-3">
            {mockProduct.ingredients.map((ingredient, index) => (
              <div key={index} className="flex items-center justify-between">
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px]">{ingredient.name}</p>
                <CheckCircle size={18} className="text-green-400" />
              </div>
            ))}
          </div>
        </div>

        {/* Learn More */}
        <div className="bg-[#a380a8]/10 border border-[#a380a8]/20 rounded-[16px] p-5">
          <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-2">Why This Matters</h3>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/80 tracking-[-0.6px]">
            Many feminine care products contain harsh chemicals and fragrances that can disrupt your body's natural pH balance. This product uses safe, natural materials.
          </p>
        </div>
      </div>

      {/* Bottom Action */}
      <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm p-6 z-20">
        <button
          onClick={onScanAnother}
          className="w-full h-[50px] bg-[#a380a8] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.25)] hover:bg-[#8d6d91] transition-colors active:scale-95"
        >
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">Scan Another Product</p>
        </button>
      </div>
    </div>
  );
}
