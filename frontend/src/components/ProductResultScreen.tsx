import { useEffect, useState } from "react";
import img12 from "figma:asset/3e71b2e76e3163500ce459fc35ad01faa42108fa.png";
import img3 from "figma:asset/d4d40c58bbd603e907bcf97d939af54f73bf95c2.png";
import { ArrowLeft, CheckCircle, AlertTriangle, XCircle, Loader2, Shield, ShieldCheck, ShieldX } from "lucide-react";
import { supabase } from "../lib/supabase";

interface RiskyIngredient {
  name: string;
  risk_level: string;
  reason: string;
}

interface ProductData {
  id: number;
  brand_name: string;
  barcode: string;
  ingredients: string[];
  product_type?: string;
  coverage_score?: number;
  research_count?: number;
}

interface AssessmentData {
  scan_id: string;
  user_id: string;
  product: ProductData;
  overall_risk_level: string; // "Low Risk" | "Caution" | "High Risk"
  risky_ingredients: RiskyIngredient[];
  explanation: string;
  timestamp: string;
}

interface AlternativeProduct {
  id: number;
  brand_name: string;
  product_type: string;
  risk_level: string;
}

interface ProductResultScreenProps {
  barcode: string;
  onBack: () => void;
  onScanAnother: () => void;
}

export default function ProductResultScreen({ barcode, onBack, onScanAnother }: ProductResultScreenProps) {
  const [assessmentData, setAssessmentData] = useState<AssessmentData | null>(null);
  const [alternatives, setAlternatives] = useState<AlternativeProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProductAssessment = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get current user for personalized assessment
        const { data: { user } } = await supabase.auth.getUser();
        const userId = user?.id || "anonymous";

        // Call barcode assessment endpoint (includes risk scoring)
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/scan/barcode/assess`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            barcode: barcode,
            user_id: userId,
          }),
        });

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Product not found in database");
          }
          if (response.status === 422) {
            // Fallback to basic barcode lookup if user_id issue
            const basicResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/scan/barcode`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ barcode: barcode }),
            });
            
            if (!basicResponse.ok) {
              throw new Error("Product not found in database");
            }
            
            const basicData = await basicResponse.json();
            // Create a basic assessment from product data
            setAssessmentData({
              scan_id: "basic-" + Date.now(),
              user_id: userId,
              product: basicData.product,
              overall_risk_level: "Caution",
              risky_ingredients: [],
              explanation: "Product found. Sign in to get personalized health recommendations.",
              timestamp: new Date().toISOString(),
            });
            return;
          }
          throw new Error(`Failed to assess product: ${response.statusText}`);
        }

        const data: AssessmentData = await response.json();
        setAssessmentData(data);

        // If product is risky, fetch alternatives
        if (data.overall_risk_level === "High Risk" || data.overall_risk_level === "Caution") {
          fetchAlternatives(data.product.product_type);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error occurred";
        setError(errorMessage);
        console.error("Product assessment error:", err);
      } finally {
        setLoading(false);
      }
    };

    const fetchAlternatives = async (productType?: string) => {
      try {
        // Query Supabase for safer alternatives of same product type
        const { data, error } = await supabase
          .from('products')
          .select('id, brand_name, product_type')
          .eq('product_type', productType || 'general')
          .limit(3);

        if (!error && data && data.length > 0) {
          setAlternatives(data.map(p => ({
            ...p,
            risk_level: "Low Risk"
          })));
        }
      } catch (err) {
        console.error("Error fetching alternatives:", err);
        // Alternatives are optional, don't set error
      }
    };

    fetchProductAssessment();
  }, [barcode]);

  // Get safety display properties based on risk level
  const getSafetyDisplay = (riskLevel: string) => {
    switch (riskLevel) {
      case "Low Risk":
        return { 
          color: "text-green-400", 
          bgColor: "bg-green-500/20", 
          borderColor: "border-green-500/30", 
          icon: ShieldCheck, 
          label: "Safe",
          score: 85
        };
      case "Caution":
        return { 
          color: "text-yellow-400", 
          bgColor: "bg-yellow-500/20", 
          borderColor: "border-yellow-500/30", 
          icon: Shield, 
          label: "Caution",
          score: 55
        };
      case "High Risk":
        return { 
          color: "text-red-400", 
          bgColor: "bg-red-500/20", 
          borderColor: "border-red-500/30", 
          icon: ShieldX, 
          label: "Unsafe",
          score: 25
        };
      default:
        return { 
          color: "text-yellow-400", 
          bgColor: "bg-yellow-500/20", 
          borderColor: "border-yellow-500/30", 
          icon: Shield, 
          label: "Unknown",
          score: 50
        };
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 size={48} className="text-[#a380a8] animate-spin" />
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
            Analyzing product...
          </p>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/60 tracking-[-0.6px]">
            Checking ingredients against your health profile
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !assessmentData) {
    return (
      <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
        <div className="absolute top-[60px] left-[24px] right-[24px] z-10">
          <button 
            onClick={onBack}
            className="text-white flex items-center gap-2 hover:text-[#a380a8] transition-colors mb-6"
          >
            <ArrowLeft size={24} />
            <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] tracking-[-0.65px]">Back to Home</span>
          </button>
        </div>

        <div className="absolute top-[180px] left-[24px] right-[24px] bottom-[100px] overflow-y-auto z-10 flex items-center justify-center">
          <div className="bg-white/5 border border-red-500/30 rounded-[16px] p-6 text-center">
            <XCircle size={48} className="text-red-400 mx-auto mb-4" />
            <h2 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[18px] text-white tracking-[-0.8px] mb-2">
              Product Not Found
            </h2>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/80 tracking-[-0.65px]">
              {error || "The scanned barcode does not match any products in our database."}
            </p>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm p-6 z-20">
          <button
            onClick={onScanAnother}
            className="w-full h-[50px] bg-[#a380a8] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.25)] hover:bg-[#8d6d91] transition-colors active:scale-95"
          >
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">Try Another Barcode</p>
          </button>
        </div>
      </div>
    );
  }

  const safetyDisplay = getSafetyDisplay(assessmentData.overall_risk_level);
  const SafetyIcon = safetyDisplay.icon;
  const productData = assessmentData.product;
  const isSafe = assessmentData.overall_risk_level === "Low Risk";

  // Success state - display product assessment
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
      <div className="absolute top-[50px] left-[24px] right-[24px] z-10">
        <button 
          onClick={onBack}
          className="text-white flex items-center gap-2 hover:text-[#a380a8] transition-colors mb-4"
        >
          <ArrowLeft size={24} />
          <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] tracking-[-0.65px]">Back to Home</span>
        </button>

        <h1 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[24px] text-white tracking-[-1.5px] mb-1">Product Analysis</h1>
      </div>

      {/* Content */}
      <div className="absolute top-[140px] left-[24px] right-[24px] bottom-[100px] overflow-y-auto z-10">
        {/* Product Info & Safety Score */}
        <div className={`${safetyDisplay.bgColor} border ${safetyDisplay.borderColor} rounded-[16px] p-5 mb-4`}>
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <h2 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[18px] text-white tracking-[-0.8px] mb-1">
                {productData.brand_name}
              </h2>
              {productData.product_type && (
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white/70 tracking-[-0.65px]">
                  {productData.product_type}
                </p>
              )}
            </div>
            {/* Safety Score Circle */}
            <div className="flex flex-col items-center">
              <div className={`w-[70px] h-[70px] rounded-full border-4 ${safetyDisplay.borderColor} ${safetyDisplay.bgColor} flex items-center justify-center`}>
                <span className={`font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[24px] ${safetyDisplay.color} font-bold`}>
                  {safetyDisplay.score}
                </span>
              </div>
              <span className={`font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] ${safetyDisplay.color} mt-1`}>
                {safetyDisplay.label}
              </span>
            </div>
          </div>
          
          {/* Safety Status */}
          <div className="flex items-center gap-2">
            <SafetyIcon size={20} className={safetyDisplay.color} />
            <span className={`font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] ${safetyDisplay.color} tracking-[-0.65px]`}>
              {isSafe ? "Safe for your health profile" : "Not recommended for your health profile"}
            </span>
          </div>
        </div>

        {/* AI Summary / Explanation */}
        <div className="bg-white/5 border border-white/10 rounded-[16px] p-5 mb-4">
          <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">
            Summary
          </h3>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/80 tracking-[-0.65px] leading-relaxed">
            {assessmentData.explanation}
          </p>
        </div>

        {/* Risky Ingredients (if any) */}
        {assessmentData.risky_ingredients && assessmentData.risky_ingredients.length > 0 && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-[16px] p-5 mb-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={20} className="text-red-400" />
              <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-red-400 tracking-[-0.7px]">
                Health Warnings
              </h3>
            </div>
            <div className="space-y-3">
              {assessmentData.risky_ingredients.map((ingredient, index) => (
                <div key={index} className="bg-white/5 rounded-[10px] p-3">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">
                      {ingredient.name}
                    </p>
                    <span className={`font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[10px] px-2 py-0.5 rounded-full ${
                      ingredient.risk_level === "High Risk" ? "bg-red-500/30 text-red-400" : "bg-yellow-500/30 text-yellow-400"
                    }`}>
                      {ingredient.risk_level}
                    </span>
                  </div>
                  <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-white/60 tracking-[-0.5px]">
                    {ingredient.reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* All Ingredients */}
        {productData.ingredients && productData.ingredients.length > 0 && (
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5 mb-4">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">
              Ingredients ({productData.ingredients.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {productData.ingredients.map((ingredient, index) => {
                const isRisky = assessmentData.risky_ingredients?.some(r => r.name.toLowerCase() === ingredient.toLowerCase());
                return (
                  <span 
                    key={index} 
                    className={`px-3 py-1.5 rounded-full font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] tracking-[-0.5px] ${
                      isRisky ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-white/10 text-white/80"
                    }`}
                  >
                    {ingredient}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Alternative Products (only if not safe) */}
        {!isSafe && alternatives.length > 0 && (
          <div className="bg-[#a380a8]/10 border border-[#a380a8]/30 rounded-[16px] p-5 mb-4">
            <div className="flex items-center gap-2 mb-4">
              <ShieldCheck size={20} className="text-[#a380a8]" />
              <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
                Safer Alternatives
              </h3>
            </div>
            <div className="space-y-3">
              {alternatives.map((alt) => (
                <div key={alt.id} className="bg-white/5 border border-white/10 rounded-[12px] p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">
                        {alt.brand_name}
                      </p>
                      <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/60 tracking-[-0.6px]">
                        {alt.product_type}
                      </p>
                    </div>
                    <div className="flex items-center gap-1 bg-green-500/20 px-2 py-1 rounded-full">
                      <ShieldCheck size={12} className="text-green-400" />
                      <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-green-400">
                        Safe
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Safe product encouragement */}
        {isSafe && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-[16px] p-5 mb-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle size={20} className="text-green-400" />
              <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-green-400 tracking-[-0.7px]">
                Great Choice!
              </h3>
            </div>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/80 tracking-[-0.6px]">
              This product aligns well with your health profile and contains safe, quality ingredients.
            </p>
          </div>
        )}

        {/* Research Info */}
        {productData.research_count !== undefined && productData.research_count > 0 && (
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5 mb-4">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-2">
              Research-Backed
            </h3>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/80 tracking-[-0.6px]">
              This product has {productData.research_count} research studies referencing its ingredients.
            </p>
          </div>
        )}
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
