import { useState } from "react";
import img1 from "figma:asset/e153f9d3e6a9dfd2dd435434c4341330f8e8ab0c.png";
import img11 from "figma:asset/15822d0d5d333944328a5265ff0f4b30240d07a8.png";
import { ArrowLeft, Loader2 } from "lucide-react";
import { supabase } from "../lib/supabase";

interface LoginScreenProps {
  onBack: () => void;
  onLoginSuccess?: () => void;
}

export default function LoginScreen({ onBack, onLoginSuccess }: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (signInError) {
        setError(signInError.message);
        return;
      }

      if (data.user) {
        console.log("Login successful:", data.user);
        if (onLoginSuccess) {
          onLoginSuccess();
        }
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
      {/* Top flower decoration */}
      <div className="absolute flex h-[300px] items-center justify-center left-[-80px] top-[-80px] w-[350px] pointer-events-none">
        <div className="flex-none rotate-[125deg]">
          <div className="h-[200px] relative w-[300px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-60" src={img1} />
          </div>
        </div>
      </div>

      {/* Bottom right flower decoration */}
      <div className="absolute flex h-[280px] items-center justify-center left-[180px] top-[620px] w-[320px] pointer-events-none">
        <div className="flex-none rotate-[-35deg]">
          <div className="h-[180px] relative w-[280px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-60" src={img11} />
          </div>
        </div>
      </div>

      {/* Back button */}
      <button 
        onClick={onBack}
        className="absolute top-[60px] left-[24px] text-white flex items-center gap-2 z-10 hover:text-[#a380a8] transition-colors"
      >
        <ArrowLeft size={24} />
        <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] tracking-[-0.65px]">Back</span>
      </button>

      {/* Content */}
      <div className="absolute top-[140px] left-[40px] right-[40px] z-10">
        <h1 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[36px] text-white tracking-[-2px] mb-2">Welcome Back</h1>
        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/80 tracking-[-0.65px] mb-6">Sign in to continue</p>

        <form onSubmit={handleLogin} className="space-y-4">
          {/* Email Input */}
          <div>
            <label className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/90 tracking-[-0.6px] block mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full h-[45px] bg-white/10 border border-white/20 rounded-[10px] px-4 text-white placeholder:text-white/40 focus:outline-none focus:border-[#a380a8] focus:bg-white/15 transition-all"
              placeholder="Enter your email"
              required
            />
          </div>

          {/* Password Input */}
          <div>
            <label className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/90 tracking-[-0.6px] block mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full h-[45px] bg-white/10 border border-white/20 rounded-[10px] px-4 text-white placeholder:text-white/40 focus:outline-none focus:border-[#a380a8] focus:bg-white/15 transition-all"
              placeholder="Enter your password"
              required
            />
          </div>

          {/* Forgot Password */}
          <div className="text-right">
            <button type="button" className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-[#a380a8] tracking-[-0.55px] hover:text-[#8d6d91] transition-colors">
              Forgot Password?
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-[10px] bg-red-500/20 text-red-300 border border-red-500/30 text-center font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] tracking-[-0.6px]">
              {error}
            </div>
          )}

          {/* Login Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-[45px] bg-[#a380a8] rounded-[10px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] hover:bg-[#8d6d91] transition-colors active:scale-95 mt-4 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading && <Loader2 size={18} className="text-white animate-spin" />}
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">
              {isLoading ? 'Signing In...' : 'Sign In'}
            </p>
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 my-4">
            <div className="flex-1 h-[1px] bg-white/20" />
            <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-white/50 tracking-[-0.55px]">or</span>
            <div className="flex-1 h-[1px] bg-white/20" />
          </div>

          {/* Social Login */}
          <button
            type="button"
            className="w-full h-[45px] bg-white/10 border border-white/20 rounded-[10px] hover:bg-white/15 transition-colors"
          >
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">Continue with Google</p>
          </button>
        </form>
      </div>
    </div>
  );
}