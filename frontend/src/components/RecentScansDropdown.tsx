import { useState, useEffect } from "react";
import { ChevronDown, ChevronUp, Clock, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { supabase } from "../lib/supabase";

interface ScanHistoryItem {
  scan_id: string;
  barcode: string;
  brand_name: string;
  product_type: string;
  risk_level: string;
  risk_score?: number;
  scanned_at: string;
}

interface RecentScansDropdownProps {
  onScanClick: (barcode: string) => void;
}

export default function RecentScansDropdown({ onScanClick }: RecentScansDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchRecentScans();
    }
  }, [isOpen]);

  const fetchRecentScans = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get current user
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        setError("Please log in to view scan history");
        return;
      }

      // Fetch recent scans from backend
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/scan/history?user_id=${user.id}&limit=5`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch scan history");
      }

      const data = await response.json();
      setScans(data.scans || []);
    } catch (err) {
      console.error("Error fetching recent scans:", err);
      setError("Could not load scan history");
    } finally {
      setLoading(false);
    }
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case "Low Risk":
        return <CheckCircle size={16} className="text-green-500" />;
      case "Caution":
        return <AlertTriangle size={16} className="text-yellow-500" />;
      case "High Risk":
        return <XCircle size={16} className="text-red-500" />;
      default:
        return null;
    }
  };

  const formatDate = (isoDate: string) => {
    const date = new Date(isoDate);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-[12px] overflow-hidden">
      {/* Header - Clickable */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Clock size={16} className="text-white/60" />
          <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">
            Recent Scans
          </h3>
        </div>
        {isOpen ? (
          <ChevronUp size={20} className="text-white/60" />
        ) : (
          <ChevronDown size={20} className="text-white/60" />
        )}
      </button>

      {/* Dropdown Content */}
      {isOpen && (
        <div className="border-t border-white/10">
          {loading ? (
            <div className="p-4 text-center">
              <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/60 tracking-[-0.6px]">
                Loading...
              </p>
            </div>
          ) : error ? (
            <div className="p-4 text-center">
              <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-red-400 tracking-[-0.6px]">
                {error}
              </p>
            </div>
          ) : scans.length === 0 ? (
            <div className="p-4 text-center">
              <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/60 tracking-[-0.6px]">
                No products scanned yet
              </p>
            </div>
          ) : (
            <div className="max-h-[300px] overflow-y-auto">
              {scans.map((scan) => (
                <button
                  key={scan.scan_id}
                  onClick={() => {
                    onScanClick(scan.barcode);
                    setIsOpen(false);
                  }}
                  className="w-full p-3 flex items-center gap-3 hover:bg-white/5 transition-colors border-t border-white/5 first:border-t-0"
                >
                  {/* Risk Icon */}
                  <div className="flex-shrink-0">
                    {getRiskIcon(scan.risk_level)}
                  </div>

                  {/* Product Info */}
                  <div className="flex-1 text-left">
                    <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px] truncate">
                      {scan.brand_name}
                    </p>
                    <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-white/50 tracking-[-0.6px]">
                      {formatDate(scan.scanned_at)}
                    </p>
                  </div>

                  {/* Risk Score (if available) */}
                  {scan.risk_score !== undefined && (
                    <div className="flex-shrink-0 text-right">
                      <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/70 tracking-[-0.6px]">
                        {scan.risk_score}
                      </p>
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
