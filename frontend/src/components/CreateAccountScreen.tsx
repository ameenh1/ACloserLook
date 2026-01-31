import { useState } from "react";
import img3 from "figma:asset/d4d40c58bbd603e907bcf97d939af54f73bf95c2.png";
import img6 from "figma:asset/6e4a41e6bc8c632007a3be70ab1f910b722fc541.png";
import { ArrowLeft, Loader2 } from "lucide-react";
import { supabase } from "../lib/supabase";

interface CreateAccountScreenProps {
  onBack: () => void;
  onAccountCreated?: () => void;
}

export default function CreateAccountScreen({ onBack, onAccountCreated }: CreateAccountScreenProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (password !== confirmPassword) {
      setError("Passwords don't match!");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setIsLoading(true);

    try {
      // Create user with Supabase Auth
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: name,
          }
        }
      });

      if (signUpError) {
        setError(signUpError.message);
        return;
      }

      if (data.user) {
        console.log("Account created successfully:", data.user);
        if (onAccountCreated) {
          onAccountCreated();
        }
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
      console.error("Sign up error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
      {/* Top right flower decoration */}
      <div className="absolute flex h-[280px] items-center justify-center left-[140px] top-[-60px] w-[320px] pointer-events-none">
        <div className="flex-none rotate-[95deg]">
          <div className="h-[180px] relative w-[280px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-60" src={img3} />
          </div>
        </div>
      </div>

      {/* Bottom left flower decoration */}
      <div className="absolute flex h-[300px] items-center justify-center left-[-100px] top-[600px] w-[350px] pointer-events-none">
        <div className="flex-none rotate-[-145deg]">
          <div className="h-[200px] relative w-[300px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-60" src={img6} />
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
      <div className="absolute top-[130px] left-[40px] right-[40px] z-10">
        <h1 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[36px] text-white tracking-[-2px] mb-2">Join Us</h1>
        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/80 tracking-[-0.65px] mb-5">Create your account</p>

        <form onSubmit={handleCreateAccount} className="space-y-3">
          {/* Name Input */}
          <div>
            <label className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/90 tracking-[-0.6px] block mb-2">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full h-[45px] bg-white/10 border border-white/20 rounded-[10px] px-4 text-white placeholder:text-white/40 focus:outline-none focus:border-[#a380a8] focus:bg-white/15 transition-all"
              placeholder="Enter your name"
              required
            />
          </div>

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
              placeholder="Create a password"
              required
              minLength={8}
            />
          </div>

          {/* Confirm Password Input */}
          <div>
            <label className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/90 tracking-[-0.6px] block mb-2">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full h-[45px] bg-white/10 border border-white/20 rounded-[10px] px-4 text-white placeholder:text-white/40 focus:outline-none focus:border-[#a380a8] focus:bg-white/15 transition-all"
              placeholder="Confirm your password"
              required
              minLength={8}
            />
          </div>

          {/* Terms */}
          <div className="flex items-start gap-2 pt-2">
            <input 
              type="checkbox" 
              required 
              className="mt-1 accent-[#a380a8]"
            />
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-white/70 tracking-[-0.55px]">
              I agree to the Terms of Service and Privacy Policy
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-[10px] bg-red-500/20 text-red-300 border border-red-500/30 text-center font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] tracking-[-0.6px]">
              {error}
            </div>
          )}

          {/* Create Account Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-[45px] bg-[#a380a8] rounded-[10px] shadow-[0px_4px_4px_0px_rgba(0,0,0,0.25)] hover:bg-[#8d6d91] transition-colors active:scale-95 mt-4 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading && <Loader2 size={18} className="text-white animate-spin" />}
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] text-white tracking-[-0.65px]">
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </p>
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 my-3">
            <div className="flex-1 h-[1px] bg-white/20" />
            <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[11px] text-white/50 tracking-[-0.55px]">or</span>
            <div className="flex-1 h-[1px] bg-white/20" />
          </div>

          {/* Social Signup */}
          <button
            type="button"
            className="w-full h-[45px] bg-white/10 border border-white/20 rounded-[10px] hover:bg-white/15 transition-colors"
          >
            <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">Sign up with Google</p>
          </button>
        </form>
      </div>
    </div>
  );
}