import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import img12 from "figma:asset/3e71b2e76e3163500ce459fc35ad01faa42108fa.png";
import img3 from "figma:asset/d4d40c58bbd603e907bcf97d939af54f73bf95c2.png";
import { ArrowLeft, CheckCircle, AlertTriangle, XCircle, Loader2, Shield, ShieldCheck, ShieldX, Sparkles, ChevronDown } from "lucide-react";
import { supabase } from "../lib/supabase";
import "./ProductResultScreen.css";
import alwaysPadImage from "../assets/61Hqf13WNcL._AC_UF1000,1000_QL80_.jpg";
import tampaxPearlImage from "../assets/817YKHYbLPS._AC_UF1000,1000_QL80_.jpg";
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "./ui/collapsible";
import { GlassCard } from "./ui/GlassCard";
import { AnimatedScoreRing } from "./ui/AnimatedScoreRing";
import { FloatingProductImage } from "./ui/FloatingProductImage";
import { HealthWarningPill } from "./ui/HealthWarningPill";

// Product images map by barcode or brand name
const PRODUCT_IMAGES: Record<string, string> = {
  '037000818052': alwaysPadImage,
  'always': alwaysPadImage,
  '073010719743': tampaxPearlImage,
  'tampax': tampaxPearlImage,
};

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

interface SaferAlternative {
  id: number;
  brand_name: string;
  product_type: string;
  safety_label: string;
  url?: string;
}

interface AssessmentData {
  scan_id: string;
  user_id: string;
  product: ProductData;
  overall_risk_level: string; // "Low Risk" | "Caution" | "High Risk"
  risk_score?: number; // 0-100, where 100 is safest
  risky_ingredients: RiskyIngredient[];
  explanation: string;
  safer_alternatives?: SaferAlternative[];
  timestamp: string;
}

interface AlternativeProduct {
  id: number;
  brand_name: string;
  product_type: string;
  risk_level: string;
  url?: string;
}

interface ProductResultScreenProps {
  barcode: string;
  onBack: () => void;
  onScanAnother: () => void;
}

export default function ProductResultScreen({ barcode, onBack, onScanAnother }: ProductResultScreenProps) {
  const [basicProduct, setBasicProduct] = useState<ProductData | null>(null);
  const [assessmentData, setAssessmentData] = useState<AssessmentData | null>(null);
  const [alternatives, setAlternatives] = useState<AlternativeProduct[]>([]);
  const [assessmentLoading, setAssessmentLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  useEffect(() => {
    // Stage 1: Fetch basic product info immediately (no assessment)
    const fetchBasicProduct = async () => {
      try {
        setError(null);
        setIsInitialLoading(true);

        // Call basic barcode lookup (fast, no assessment)
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/scan/barcode`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ barcode: barcode }),
        });

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Product not found in database");
          }
          throw new Error(`Failed to lookup product: ${response.statusText}`);
        }

        const basicData = await response.json();
        setBasicProduct(basicData.product);
        setIsInitialLoading(false);

        // Stage 2: Fetch full assessment in background (optional)
        fetchFullAssessment();
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error occurred";
        setError(errorMessage);
        setIsInitialLoading(false);
        console.error("Product lookup error:", err);
      }
    };

    const fetchFullAssessment = async () => {
      try {
        setAssessmentLoading(true);

        // Get current user for personalized assessment
        const { data: { user } } = await supabase.auth.getUser();
        const userId = user?.id || "anonymous";

        // Call barcode assessment endpoint (includes risk scoring) - runs in background
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

        if (response.ok) {
          const data: AssessmentData = await response.json();
          setAssessmentData(data);

          // Use safer_alternatives from backend response if available
          if (data.safer_alternatives && data.safer_alternatives.length > 0) {
            setAlternatives(data.safer_alternatives.map(p => ({
              ...p,
              risk_level: "Low Risk"
            })));
          } else if (data.overall_risk_level === "High Risk" || data.overall_risk_level === "Caution") {
            // Fallback: fetch alternatives from Supabase if not provided by backend
            fetchAlternatives(data.product.product_type);
          }
        } else {
          console.warn("Full assessment not available, showing basic product info only");
        }
      } catch (err) {
        console.warn("Could not fetch full assessment:", err);
        // Non-blocking error - user can still see basic product info
      } finally {
        setAssessmentLoading(false);
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

    fetchBasicProduct();
  }, [barcode]);

  // Get safety display properties based on risk level and score
  const getSafetyDisplay = (riskLevel: string, score?: number) => {
    // If we have a score, use it to determine colors more accurately
    if (score !== undefined) {
      if (score >= 71) {
        return {
          color: "text-green-400",
          bgColor: "bg-green-500/20",
          borderColor: "border-green-500/30",
          icon: ShieldCheck,
          label: "Safe",
          score: score,
          scoreColor: "text-green-400"
        };
      } else if (score >= 41) {
        return {
          color: "text-yellow-400",
          bgColor: "bg-yellow-500/20",
          borderColor: "border-yellow-500/30",
          icon: Shield,
          label: "Caution",
          score: score,
          scoreColor: "text-yellow-400"
        };
      } else {
        return {
          color: "text-red-400",
          bgColor: "bg-red-500/20",
          borderColor: "border-red-500/30",
          icon: ShieldX,
          label: "Unsafe",
          score: score,
          scoreColor: "text-red-400"
        };
      }
    }
    
    // Fallback to categorical risk level
    switch (riskLevel) {
      case "Low Risk":
        return {
          color: "text-green-400",
          bgColor: "bg-green-500/20",
          borderColor: "border-green-500/30",
          icon: ShieldCheck,
          label: "Safe",
          score: 85,
          scoreColor: "text-green-400"
        };
      case "Caution":
        return {
          color: "text-yellow-400",
          bgColor: "bg-yellow-500/20",
          borderColor: "border-yellow-500/30",
          icon: Shield,
          label: "Caution",
          score: 55,
          scoreColor: "text-yellow-400"
        };
      case "High Risk":
        return {
          color: "text-red-400",
          bgColor: "bg-red-500/20",
          borderColor: "border-red-500/30",
          icon: ShieldX,
          label: "Unsafe",
          score: 25,
          scoreColor: "text-red-400"
        };
      default:
        return {
          color: "text-yellow-400",
          bgColor: "bg-yellow-500/20",
          borderColor: "border-yellow-500/30",
          icon: Shield,
          label: "Unknown",
          score: 50,
          scoreColor: "text-yellow-400"
        };
    }
  };

  // Show loading animation while fetching initial product data
  if (isInitialLoading) {
    return (
      <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="w-12 h-12 rounded-full border-3 border-[#a380a8] border-t-white animate-spin absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"></div>
        </div>
      </div>
    );
  }

  // Error state - product not found
  if (error || !basicProduct) {
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

  // Stage 1: Show basic product info immediately (no assessment needed)
  const safetyDisplay = assessmentData
    ? getSafetyDisplay(assessmentData.overall_risk_level, assessmentData.risk_score)
    : getSafetyDisplay("Caution");
  const SafetyIcon = safetyDisplay.icon;
  const isSafe = assessmentData?.overall_risk_level === "Low Risk";

  // Success state - display product info with optional assessment overlay
  return (
    <div className="bg-black relative w-[393px] h-[852px] overflow-hidden overflow-x-hidden">
      {/* Top flower decoration - hide during loading */}
      {!assessmentLoading && (
        <div className="absolute flex h-[280px] items-center justify-center left-[-90px] top-[-80px] w-[350px] pointer-events-none z-0">
          <div className="flex-none rotate-[135deg]">
            <div className="h-[180px] relative w-[300px]">
              <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-30" src={img12} />
            </div>
          </div>
        </div>
      )}

      {/* Bottom right flower decoration - hide during loading */}
      {!assessmentLoading && (
        <div className="absolute flex h-[260px] items-center justify-center left-[150px] top-[640px] w-[320px] pointer-events-none z-0">
          <div className="flex-none rotate-[-45deg]">
            <div className="h-[160px] relative w-[280px]">
              <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-30" src={img3} />
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="absolute top-[50px] left-[24px] right-[24px] z-20">
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
      <div className="absolute top-[140px] left-[24px] right-[24px] bottom-[100px] overflow-y-auto overflow-x-hidden z-20">
        {/* Product Info & Circular Score */}
        <GlassCard className="mb-6 relative overflow-visible">
          {/* Floating Product Image - overlapping top-right */}
          {(PRODUCT_IMAGES[barcode] || PRODUCT_IMAGES[basicProduct.brand_name.toLowerCase()]) && (
            <FloatingProductImage
              src={PRODUCT_IMAGES[barcode] || PRODUCT_IMAGES[basicProduct.brand_name.toLowerCase()]}
              alt={basicProduct.brand_name}
              size={85}
            />
          )}

          <div className="flex flex-col items-center pt-2">
            {/* Product Name */}
            <h2 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.8px] mb-4">
              {basicProduct.brand_name}{basicProduct.product_type ? ` ${basicProduct.product_type}` : ''}
            </h2>

            {/* Animated Circular Score Ring */}
            <div className="flex flex-col items-center mb-3">
              {assessmentLoading ? (
                <div className="skeleton skeleton-box" style={{ width: "60px", height: "60px", borderRadius: "50%" }}></div>
              ) : (
                <AnimatedScoreRing score={safetyDisplay.score} size={60} />
              )}
            </div>

            {/* Caution/Safe Label with Shield */}
            <div className="flex items-center gap-2">
              <SafetyIcon
                size={16}
                style={{
                  color: safetyDisplay.score >= 71 ? '#4ade80' : safetyDisplay.score >= 41 ? '#facc15' : '#f87171'
                }}
              />
              <span
                className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] font-semibold"
                style={{
                  color: safetyDisplay.score >= 71 ? '#4ade80' : safetyDisplay.score >= 41 ? '#facc15' : '#f87171'
                }}
              >
                {safetyDisplay.label}
              </span>
            </div>
          </div>
        </GlassCard>

        {/* AI Analysis - Only show when assessment is loaded */}
        {assessmentLoading ? (
          <GlassCard className="mb-6" animated={false}>
            <div className="skeleton skeleton-text large" style={{ width: "40%", marginBottom: "1rem" }}></div>
            <div className="skeleton skeleton-text" style={{ width: "100%" }}></div>
            <div className="skeleton skeleton-text" style={{ width: "95%" }}></div>
            <div className="skeleton skeleton-text" style={{ width: "90%" }}></div>
          </GlassCard>
        ) : assessmentData ? (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={20} className="text-white" />
              <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
                AI Analysis
              </h3>
            </div>
            <div className="space-y-3">
              {assessmentData.explanation.split('. ').filter(s => s.trim()).map((sentence, index) => (
                <motion.div
                  key={index}
                  className="flex items-start gap-3"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.3 }}
                >
                  <span className="text-white mt-1.5 text-lg">•</span>
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px] leading-relaxed">
                    {sentence.trim().replace(/\.$/, '')}
                  </span>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        ) : null}

        {/* Risky Ingredients (if any) - Only show when assessment is loaded */}
        {assessmentData && assessmentData.risky_ingredients && assessmentData.risky_ingredients.length > 0 && (
          <GlassCard className="bg-red-500/10 border-red-500/40 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle size={20} className="text-red-400" />
              <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
                Health Warnings
              </h3>
            </div>
            <div className="space-y-3">
              {assessmentData.risky_ingredients.map((ingredient, index) => (
                <HealthWarningPill
                  key={index}
                  name={ingredient.name}
                  reason={ingredient.reason}
                  severity={ingredient.risk_level as "High Risk" | "Caution"}
                />
              ))}
            </div>
          </GlassCard>
        )}

        {/* All Ingredients - Collapsible (closed by default) */}
        {basicProduct.ingredients && basicProduct.ingredients.length > 0 && (
          <GlassCard className="mb-6 overflow-hidden p-0" animated={false}>
            <Collapsible defaultOpen={false}>
              <CollapsibleTrigger className="w-full p-6 flex items-center justify-between hover:bg-white/5 transition-colors">
                <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
                  Ingredients ({basicProduct.ingredients.length})
                </h3>
                <ChevronDown className="h-5 w-5 text-white transition-transform duration-200 data-[state=open]:rotate-180" />
              </CollapsibleTrigger>
              <CollapsibleContent className="overflow-hidden">
                <div className="px-6 pb-6 flex flex-col gap-3">
                  {basicProduct.ingredients.map((ingredient, index) => (
                    <motion.div
                      key={index}
                      className="flex items-center gap-3 px-3 py-2.5 rounded-lg font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] tracking-[-0.5px] bg-white/10 text-white border border-white/10"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.02, duration: 0.2 }}
                    >
                      <span className="text-white/60">●</span>
                      <span className="flex-1">{ingredient}</span>
                    </motion.div>
                  ))}
                </div>
              </CollapsibleContent>
            </Collapsible>
          </GlassCard>
        )}

        {/* Alternative Products (only if assessment available and not safe) */}
        {assessmentData && !isSafe && alternatives.length > 0 && (
          <GlassCard className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <ShieldCheck size={20} className="text-[#a380a8]" />
              <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
                Safer Alternatives
              </h3>
            </div>
            <div className="space-y-3">
              {alternatives.map((alt, index) => {
                // Hardcoded URLs for specific alternatives
                const productUrls: Record<string, string> = {
                  "Rael Organic Cotton Cover Pads": "https://www.getrael.com/collections/pads/products/petite-organic-cotton-pads?variant=51779702718829",
                  "Cora Organic Ultra Thin Period Pads": "https://www.walmart.com/ip/Cora-Compact-Applicator-Tampons-100-Organic-Cotton-Regular-Super-32-Count/693365963",
                  "Organyc Heavy Night Pads": "https://thehoneypot.co/products/organic-duo-pack-tampons?variant=32026105249885&country=US&currency=USD"
                };
                const url = alt.url || productUrls[alt.brand_name];
                
                return (
                  <motion.div
                    key={alt.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1, duration: 0.3 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      if (url) {
                        window.open(url, '_blank', 'noopener,noreferrer');
                      }
                    }}
                    className={`backdrop-blur-md bg-white/5 border border-white/20 rounded-[12px] p-4 ${url ? 'hover:bg-white/10 hover:border-white/30 transition-all cursor-pointer' : ''}`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">
                          {alt.brand_name}
                        </p>
                        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/70 tracking-[-0.6px]">
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
                  </motion.div>
                );
              })}
            </div>
          </GlassCard>
        )}

        {/* Safe product encouragement */}
        {assessmentData && isSafe && (
          <GlassCard className="bg-green-500/10 border-green-500/40 mb-6">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle size={20} className="text-green-400" />
              <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-green-400 tracking-[-0.7px]">
                Great Choice!
              </h3>
            </div>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white tracking-[-0.6px]">
              This product aligns well with your health profile and contains safe, quality ingredients.
            </p>
          </GlassCard>
        )}

        {/* Research Info */}
        {basicProduct.research_count !== undefined && basicProduct.research_count > 0 && (
          <GlassCard className="mb-6">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-2">
              Research-Backed
            </h3>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white tracking-[-0.6px]">
              This product has {basicProduct.research_count} research studies referencing its ingredients.
            </p>
          </GlassCard>
        )}
      </div>

      {/* Bottom Action */}
      <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm p-6 z-30">
        <motion.button
          onClick={onScanAnother}
          className="w-full h-[50px] bg-gradient-to-r from-purple-600 to-pink-500 rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.25)] transition-all"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">Scan Another Product</p>
        </motion.button>
      </div>
    </div>
  );
}
