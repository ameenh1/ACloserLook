import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Camera, Keyboard } from "lucide-react";
import { Html5Qrcode, Html5QrcodeSupportedFormats } from "html5-qrcode";

interface BarcodeScannerScreenProps {
  onBack: () => void;
  onScanSuccess: (barcode: string) => void;
}

export default function BarcodeScannerScreen({ onBack, onScanSuccess }: BarcodeScannerScreenProps) {
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState("");
  const [showManualInput, setShowManualInput] = useState(false);
  const [manualBarcode, setManualBarcode] = useState("");
  const [validationError, setValidationError] = useState("");

  useEffect(() => {
    startScanner();
    
    return () => {
      stopScanner();
    };
  }, []);

  const startScanner = async () => {
    try {
      const scanner = new Html5Qrcode("reader", {
        formatsToSupport: [
          Html5QrcodeSupportedFormats.UPC_A,      // Standard US barcodes
          Html5QrcodeSupportedFormats.UPC_E,      // Short US barcodes
          Html5QrcodeSupportedFormats.EAN_13,     // International barcodes
          Html5QrcodeSupportedFormats.EAN_8,      // Short international
          Html5QrcodeSupportedFormats.CODE_128,   // Shipping/logistics
          Html5QrcodeSupportedFormats.CODE_39,    // Alternate format
          Html5QrcodeSupportedFormats.QR_CODE     // QR codes (optional)
        ],
        verbose: false
      });
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: "environment" },
        {
          fps: 15,
          qrbox: { width: 300, height: 200 }
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

  const validateBarcode = (barcode: string): { valid: boolean; error?: string } => {
    const trimmed = barcode.trim();
    
    // Check if empty
    if (!trimmed) {
      return { valid: false, error: 'Barcode cannot be empty' };
    }
    
    // Check if contains only digits (most common barcode formats)
    if (!/^\d+$/.test(trimmed)) {
      return { valid: false, error: 'Barcode should contain only numbers' };
    }
    
    // Check common barcode lengths
    const validLengths = [6, 8, 12, 13, 14]; // UPC-E, EAN-8, UPC-A, EAN-13, ITF-14
    if (!validLengths.includes(trimmed.length)) {
      return {
        valid: false,
        error: `Invalid length. Expected 6, 8, 12, 13, or 14 digits`
      };
    }
    
    return { valid: true };
  };

  const handleManualSubmit = () => {
    const validation = validateBarcode(manualBarcode);
    
    if (!validation.valid) {
      setValidationError(validation.error || 'Invalid barcode');
      return;
    }
    
    // Clean up and submit
    const cleanBarcode = manualBarcode.trim();
    stopScanner(); // Stop camera if running
    onScanSuccess(cleanBarcode);
  };

  const handleShowManualInput = () => {
    stopScanner(); // Stop camera when switching to manual
    setShowManualInput(true);
  };

  const handleBackToScanner = () => {
    setShowManualInput(false);
    setManualBarcode("");
    setValidationError("");
    startScanner();
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

      {/* Scanner Container or Manual Input */}
      <div className="absolute top-[80px] left-0 right-0 bottom-[100px] flex items-center justify-center">
        {showManualInput ? (
          // Manual Input Mode
          <div className="px-8 w-full">
            <div className="bg-white/10 rounded-[20px] p-6 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-4">
                <Keyboard size={24} className="text-[#a380a8]" />
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.65px]">Enter Barcode Number</p>
              </div>
              
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                value={manualBarcode}
                onChange={(e) => {
                  setManualBarcode(e.target.value);
                  setValidationError('');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleManualSubmit();
                  }
                }}
                placeholder="e.g., 037000561538"
                className="w-full px-4 py-3 rounded-[10px] bg-white text-black font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] mb-2"
                autoFocus
              />
              
              {validationError && (
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-red-400 mb-4 tracking-[-0.6px]">{validationError}</p>
              )}
              
              <button
                onClick={handleManualSubmit}
                className="w-full bg-[#a380a8] py-3 rounded-[10px] hover:bg-[#8d6d91] transition-colors mb-3"
              >
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">Look Up Product</p>
              </button>
              
              <button
                onClick={handleBackToScanner}
                className="w-full bg-white/10 py-3 rounded-[10px] hover:bg-white/20 transition-colors"
              >
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">Back to Scanner</p>
              </button>
              
              <div className="mt-4 pt-4 border-t border-white/20">
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-white/60 tracking-[-0.55px] text-center">
                  Enter the barcode number found on the product package
                </p>
              </div>
            </div>
          </div>
        ) : (
          // Camera Scanner Mode
          <>
            {error ? (
              <div className="px-8 text-center">
                <Camera size={64} className="text-white/30 mx-auto mb-4" />
                <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px] mb-4">{error}</p>
                <button
                  onClick={startScanner}
                  className="bg-[#a380a8] px-6 py-3 rounded-[10px] hover:bg-[#8d6d91] transition-colors mb-3"
                >
                  <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">Try Again</p>
                </button>
                <button
                  onClick={handleShowManualInput}
                  className="bg-white/10 px-6 py-3 rounded-[10px] hover:bg-white/20 transition-colors flex items-center gap-2 mx-auto"
                >
                  <Keyboard size={18} />
                  <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">Enter Manually</p>
                </button>
              </div>
            ) : (
              <div className="w-full px-8">
                <div id="reader" className="w-full rounded-[20px] overflow-hidden"></div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Instructions */}
      <div className="absolute bottom-0 left-0 right-0 bg-black/80 backdrop-blur-sm p-6 z-20">
        {showManualInput ? (
          <div className="text-center">
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.65px] mb-2">Manual Barcode Entry</p>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/70 tracking-[-0.6px]">Enter the numbers from the barcode on your product</p>
          </div>
        ) : (
          <div className="text-center">
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.65px] mb-2">Position Barcode in Frame</p>
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/70 tracking-[-0.6px]">The barcode will be scanned automatically</p>
            {!error && (
              <button
                onClick={handleShowManualInput}
                className="mt-3 text-[#a380a8] hover:text-[#8d6d91] transition-colors flex items-center gap-2 mx-auto"
              >
                <Keyboard size={16} />
                <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] tracking-[-0.6px]">Can't scan? Enter manually</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
