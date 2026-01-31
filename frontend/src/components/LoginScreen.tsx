import { useState } from "react";
import img1 from "figma:asset/e153f9d3e6a9dfd2dd435434c4341330f8e8ab0c.png";
import img11 from "figma:asset/15822d0d5d333944328a5265ff0f4b30240d07a8.png";
import { ArrowLeft } from "lucide-react";

interface LoginScreenProps {
  onBack: () => void;
  onLoginSuccess?: () => void;
}

export default function LoginScreen({ onBack, onLoginSuccess }: LoginScreenProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Mock login functionality
    console.log("Login attempt with:", { email, password });
    if (onLoginSuccess) {
      onLoginSuccess();
    } else {
      alert("Login successful! (Demo mode)");
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

          {/* Login Button */}
          <button
            type="submit"
            className="w-full h-[45px] bg-[#a380a8] rounded-[10px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] hover:bg-[#8d6d91] transition-colors active:scale-95 mt-4"
          >
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">Sign In</p>
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