import { useEffect, useState } from "react";
import img12 from "figma:asset/3e71b2e76e3163500ce459fc35ad01faa42108fa.png";
import img3 from "figma:asset/d4d40c58bbd603e907bcf97d939af54f73bf95c2.png";
import { ArrowLeft, CheckCircle, AlertTriangle, XCircle, Loader } from "lucide-react";

interface ProductData {
  id: number;
  brand_name: string;
  barcode: string;
  ingredients: string[];
  product_type?: string;
  coverage_score?: number;
  research_count?: number;
}

interface ProductResultScreenProps {
  barcode: string;
  onBack: () => void;
  onScanAnother: () => void;
}

export default function ProductResultScreen({ barcode, onBack, onScanAnother }: ProductResultScreenProps) {
  const [productData, setProductData] = useState<ProductData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Call barcode lookup endpoint
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/scan/barcode`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            barcode: barcode,
          }),
        });

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Product not found in database");
          }
          throw new Error(`Failed to lookup product: ${response.statusText}`);
        }

        const data = await response.json();
        setProductData(data.product);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error occurred";
        setError(errorMessage);
        console.error("Product lookup error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProductData();
  }, [barcode]);

  // Loading state
  if (loading) {
    return (
      <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader size={48} className="text-[#a380a8] animate-spin" />
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
            Looking up product...
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !productData) {
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

  // Success state - display product data
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
          <h2 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[20px] text-white tracking-[-0.8px] mb-1">
            {productData.brand_name}
          </h2>
          {productData.product_type && (
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white/70 tracking-[-0.65px] mb-2">
              Type: {productData.product_type}
            </p>
          )}
          {productData.coverage_score !== undefined && (
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/60 tracking-[-0.6px]">
              Research Coverage: {(productData.coverage_score * 100).toFixed(0)}%
            </p>
          )}
        </div>

        {/* Ingredients */}
        {productData.ingredients && productData.ingredients.length > 0 && (
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5 mb-4">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">
              Ingredients ({productData.ingredients.length})
            </h3>
            <div className="space-y-2">
              {productData.ingredients.map((ingredient, index) => (
                <div key={index} className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-white/50 mt-0.5 flex-shrink-0" />
                  <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px]">
                    {ingredient}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Research Info */}
        {productData.research_count !== undefined && productData.research_count > 0 && (
          <div className="bg-[#a380a8]/10 border border-[#a380a8]/20 rounded-[16px] p-5">
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
