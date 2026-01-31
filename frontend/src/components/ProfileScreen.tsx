import { useState } from "react";
import img1 from "figma:asset/e153f9d3e6a9dfd2dd435434c4341330f8e8ab0c.png";
import img11 from "figma:asset/15822d0d5d333944328a5265ff0f4b30240d07a8.png";
import { ArrowLeft, Save } from "lucide-react";

interface ProfileScreenProps {
  onBack: () => void;
}

export default function ProfileScreen({ onBack }: ProfileScreenProps) {
  // Health Profile State
  const [skinType, setSkinType] = useState("");
  const [allergies, setAllergies] = useState({
    fragrance: false,
    latex: false,
    dyes: false,
    rayon: false,
    other: ""
  });
  const [conditions, setConditions] = useState({
    bv: false,
    yeastInfections: false,
    endometriosis: false,
    pcos: false,
    vulvodynia: false,
    vaginitis: false,
    uti: false,
    cervicitis: false,
    vaginalAtrophy: false,
    pid: false,
    other: ""
  });

  // Preferences State
  const [preferences, setPreferences] = useState({
    organicOnly: false,
    fragranceeFree: false,
    ecoFriendly: false,
    cruealtyFree: false
  });
  const [priceRange, setPriceRange] = useState("");

  const handleSave = () => {
    const profileData = {
      skinType,
      allergies,
      conditions,
      preferences,
      priceRange
    };
    console.log("Saving profile:", profileData);
    // Here you would save to your backend/database
    alert("Health profile saved successfully!");
  };

  return (
    <div className="bg-[#0e0808] relative w-[393px] h-[852px] overflow-hidden">
      {/* Top flower decoration */}
      <div className="absolute flex h-[300px] items-center justify-center left-[120px] top-[-60px] w-[350px] pointer-events-none">
        <div className="flex-none rotate-[155deg]">
          <div className="h-[200px] relative w-[300px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-30" src={img11} />
          </div>
        </div>
      </div>

      {/* Bottom flower decoration */}
      <div className="absolute flex h-[280px] items-center justify-center left-[-80px] top-[620px] w-[320px] pointer-events-none">
        <div className="flex-none rotate-[-135deg]">
          <div className="h-[180px] relative w-[280px]">
            <img alt="" className="absolute inset-0 max-w-none object-cover pointer-events-none size-full opacity-30" src={img1} />
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="absolute top-[110px] left-[24px] right-[24px] z-10">
        <button 
          onClick={onBack}
          className="text-white flex items-center gap-2 hover:text-[#a380a8] transition-colors mb-4"
        >
          <ArrowLeft size={24} />
          <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[14px] tracking-[-0.65px]">Back</span>
        </button>

        <h1 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[28px] text-white tracking-[-1.5px] mb-0.5">My Health Profile</h1>
        <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[12px] text-white/70 tracking-[-0.6px]">Customize your product recommendations</p>
      </div>

      {/* Scrollable Content */}
      <div className="absolute top-[210px] left-[24px] right-[24px] bottom-[90px] overflow-y-auto z-10">
        <div className="space-y-5 pb-4">
          {/* Skin Type Section */}
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">Skin Type</h3>
            <div className="space-y-2">
              {["Normal", "Sensitive", "Very Sensitive", "Allergy-Prone"].map((type) => (
                <label key={type} className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="skinType"
                    value={type}
                    checked={skinType === type}
                    onChange={(e) => setSkinType(e.target.value)}
                    className="accent-[#a380a8] w-4 h-4"
                  />
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px]">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Allergies Section */}
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">Known Allergies</h3>
            <div className="space-y-2 mb-3">
              {[
                { key: "fragrance", label: "Fragrance" },
                { key: "latex", label: "Latex" },
                { key: "dyes", label: "Dyes/Colors" },
                { key: "rayon", label: "Rayon" }
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={allergies[key as keyof typeof allergies] as boolean}
                    onChange={(e) => setAllergies({ ...allergies, [key]: e.target.checked })}
                    className="accent-[#a380a8] w-4 h-4"
                  />
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px]">{label}</span>
                </label>
              ))}
            </div>
            <input
              type="text"
              placeholder="Other allergies (comma separated)"
              value={allergies.other}
              onChange={(e) => setAllergies({ ...allergies, other: e.target.value })}
              className="w-full h-[40px] bg-white/10 border border-white/20 rounded-[10px] px-4 text-white text-[13px] placeholder:text-white/40 focus:outline-none focus:border-[#a380a8] focus:bg-white/15 transition-all"
            />
          </div>

          {/* Conditions Section */}
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">Health Conditions</h3>
            <div className="space-y-2 mb-3">
              {[
                { key: "bv", label: "Bacterial Vaginosis (BV)" },
                { key: "yeastInfections", label: "Yeast Infections" },
                { key: "endometriosis", label: "Endometriosis" },
                { key: "pcos", label: "PCOS" },
                { key: "vulvodynia", label: "Vulvodynia" },
                { key: "vaginitis", label: "Vaginitis" },
                { key: "uti", label: "Urinary Tract Infections (UTI)" },
                { key: "cervicitis", label: "Cervicitis" },
                { key: "vaginalAtrophy", label: "Vaginal Atrophy" },
                { key: "pid", label: "Pelvic Inflammatory Disease (PID)" }
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={conditions[key as keyof typeof conditions] as boolean}
                    onChange={(e) => setConditions({ ...conditions, [key]: e.target.checked })}
                    className="accent-[#a380a8] w-4 h-4"
                  />
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px]">{label}</span>
                </label>
              ))}
            </div>
            <input
              type="text"
              placeholder="Other conditions (comma separated)"
              value={conditions.other}
              onChange={(e) => setConditions({ ...conditions, other: e.target.value })}
              className="w-full h-[40px] bg-white/10 border border-white/20 rounded-[10px] px-4 text-white text-[13px] placeholder:text-white/40 focus:outline-none focus:border-[#a380a8] focus:bg-white/15 transition-all"
            />
          </div>

          {/* Preferences Section */}
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">Product Preferences</h3>
            <div className="space-y-2">
              {[
                { key: "organicOnly", label: "Organic Only" },
                { key: "fragranceeFree", label: "Fragrance-Free" },
                { key: "ecoFriendly", label: "Eco-Friendly" },
                { key: "cruealtyFree", label: "Cruelty-Free" }
              ].map(({ key, label }) => (
                <label key={key} className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={preferences[key as keyof typeof preferences]}
                    onChange={(e) => setPreferences({ ...preferences, [key]: e.target.checked })}
                    className="accent-[#a380a8] w-4 h-4"
                  />
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px]">{label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Price Range Section */}
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">Price Range</h3>
            <div className="space-y-2">
              {["Budget-Friendly", "Mid-Range", "Premium", "No Preference"].map((range) => (
                <label key={range} className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="priceRange"
                    value={range}
                    checked={priceRange === range}
                    onChange={(e) => setPriceRange(e.target.value)}
                    className="accent-[#a380a8] w-4 h-4"
                  />
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white/90 tracking-[-0.65px]">{range}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/95 to-transparent p-6 pt-8 z-20">
        <button
          onClick={handleSave}
          className="w-full h-[50px] bg-[#a380a8] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.25)] hover:bg-[#8d6d91] transition-colors active:scale-95 flex items-center justify-center gap-2"
        >
          <Save size={20} className="text-white" />
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">Save Health Profile</p>
        </button>
      </div>
    </div>
  );
}