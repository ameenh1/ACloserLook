import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Camera } from "lucide-react";
import { Html5Qrcode } from "html5-qrcode";

interface BarcodeScannerScreenProps {
  onBack: () => void;
  onScanSuccess: (barcode: string) => void;
}

export default function BarcodeScannerScreen({ onBack, onScanSuccess }: BarcodeScannerScreenProps) {
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    startScanner();
    
    return () => {
      stopScanner();
    };
  }, []);

  const startScanner = async () => {
    try {
      const scanner = new Html5Qrcode("reader");
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: "environment" },
        {
          fps: 10,
          qrbox: { width: 250, height: 150 },
        },
        (decodedText) => {
          // Success callback
          console.log("Barcode scanned:", decodedText);
          stopScanner();
          onScanSuccess(decodedText);
        },
        (errorMessage) => {
          // Error callback - this fires constantly, so we ignore it
        }
      );
      
      setIsScanning(true);
      setError("");
    } catch (err) {
      console.error("Error starting scanner:", err);
      setError("Unable to access camera. Please allow camera permissions.");
    }
  };

  const stopScanner = () => {
    if (scannerRef.current) {
      scannerRef.current.stop().then(() => {
        scannerRef.current = null;
        setIsScanning(false);
      }).catch((err) => {
        console.error("Error stopping scanner:", err);
      });
    }
  };

  const handleBack = () => {
    stopScanner();
    onBack();
  };

  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 bg-black/80 backdrop-blur-sm z-20 p-4">
        <button 
          onClick={handleBack}
          className="text-white flex items-center gap-2 hover:text-[#a380a8] transition-colors"
        >
          <ArrowLeft size={24} />
          <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] tracking-[-0.65px]">Back</span>
        </button>
      </div>

      {/* Scanner Container */}
      <div className="absolute top-[80px] left-0 right-0 bottom-[100px] flex items-center justify-center">
        {error ? (
          <div className="px-8 text-center">
            <Camera size={64} className="text-white/30 mx-auto mb-4" />
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px] mb-4">{error}</p>
            <button
              onClick={startScanner}
              className="bg-[#a380a8] px-6 py-3 rounded-[10px] hover:bg-[#8d6d91] transition-colors"
            >
              <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">Try Again</p>
            </button>
          </div>
        ) : (
          <div className="w-full px-8">
            <div id="reader" className="w-full rounded-[20px] overflow-hidden"></div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm p-6 z-20">
        <div className="text-center">
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.65px] mb-2">Position Barcode in Frame</p>
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/70 tracking-[-0.6px]">The barcode will be scanned automatically</p>
        </div>
      </div>
    </div>
  );
}
