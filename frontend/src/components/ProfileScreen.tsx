import { useState, useEffect } from "react";
import img1 from "figma:asset/e153f9d3e6a9dfd2dd435434c4341330f8e8ab0c.png";
import img11 from "figma:asset/15822d0d5d333944328a5265ff0f4b30240d07a8.png";
import { ArrowLeft, Save, Loader2, Check } from "lucide-react";
import { supabase } from "../lib/supabase";

interface ProfileScreenProps {
  onBack: () => void;
}

export default function ProfileScreen({ onBack }: ProfileScreenProps) {
  // Loading & Status States
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

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

  // Load profile on mount
  useEffect(() => {
    loadProfile();
  }, []);

  // Auto-hide save message after 3 seconds
  useEffect(() => {
    if (saveMessage) {
      const timer = setTimeout(() => setSaveMessage(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [saveMessage]);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      
      // Get the currently logged-in user
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        console.log('No user logged in');
        setIsLoading(false);
        return;
      }

      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (error && error.code !== 'PGRST116') { // PGRST116 = no rows found
        console.error('Error loading profile:', error);
        return;
      }

      if (data) {
        // Restore saved data
        setSkinType(data.skin_type || "");
        setPriceRange(data.price_range || "");
        
        if (data.allergies) {
          setAllergies(data.allergies);
        }
        if (data.conditions) {
          setConditions(data.conditions);
        }
        if (data.preferences) {
          setPreferences(data.preferences);
        }
      }
    } catch (err) {
      console.error('Error loading profile:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setSaveMessage(null);

      // Get the currently logged-in user
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        setSaveMessage({ type: 'error', text: 'Please log in to save your profile.' });
        return;
      }

      const profileData = {
        user_id: user.id,
        skin_type: skinType,
        allergies,
        conditions,
        preferences,
        price_range: priceRange,
        updated_at: new Date().toISOString()
      };

      // Upsert (insert or update) the profile
      const { error } = await supabase
        .from('profiles')
        .upsert(profileData, { onConflict: 'user_id' });

      if (error) {
        console.error('Error saving profile:', error);
        setSaveMessage({ type: 'error', text: 'Failed to save. Please try again.' });
        return;
      }

      setSaveMessage({ type: 'success', text: 'Profile saved successfully!' });
    } catch (err) {
      console.error('Error saving profile:', err);
      setSaveMessage({ type: 'error', text: 'An error occurred. Please try again.' });
    } finally {
      setIsSaving(false);
    }
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
      <div className="absolute top-[80px] left-[24px] right-[24px] z-10">
        <button 
          onClick={onBack}
          className="text-white flex items-center gap-2 hover:text-[#a380a8] transition-colors mb-3"
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
                <button
                  key={type}
                  type="button"
                  onClick={() => setSkinType(type)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-[10px] transition-all ${
                    skinType === type
                      ? 'bg-[#a380a8] border border-[#a380a8]'
                      : 'bg-white/10 border border-white/20 hover:bg-white/15'
                  }`}
                >
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">{type}</span>
                  {skinType === type && <Check size={16} className="text-white" />}
                </button>
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
              ].map(({ key, label }) => {
                const isSelected = allergies[key as keyof typeof allergies] as boolean;
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setAllergies({ ...allergies, [key]: !isSelected })}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-[10px] transition-all ${
                      isSelected
                        ? 'bg-[#a380a8] border border-[#a380a8]'
                        : 'bg-white/10 border border-white/20 hover:bg-white/15'
                    }`}
                  >
                    <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">{label}</span>
                    {isSelected && <Check size={16} className="text-white" />}
                  </button>
                );
              })}
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
              ].map(({ key, label }) => {
                const isSelected = conditions[key as keyof typeof conditions] as boolean;
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setConditions({ ...conditions, [key]: !isSelected })}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-[10px] transition-all ${
                      isSelected
                        ? 'bg-[#a380a8] border border-[#a380a8]'
                        : 'bg-white/10 border border-white/20 hover:bg-white/15'
                    }`}
                  >
                    <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">{label}</span>
                    {isSelected && <Check size={16} className="text-white" />}
                  </button>
                );
              })}
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
              ].map(({ key, label }) => {
                const isSelected = preferences[key as keyof typeof preferences];
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setPreferences({ ...preferences, [key]: !isSelected })}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-[10px] transition-all ${
                      isSelected
                        ? 'bg-[#a380a8] border border-[#a380a8]'
                        : 'bg-white/10 border border-white/20 hover:bg-white/15'
                    }`}
                  >
                    <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">{label}</span>
                    {isSelected && <Check size={16} className="text-white" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Price Range Section */}
          <div className="bg-white/5 border border-white/10 rounded-[16px] p-5">
            <h3 className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px] mb-3">Price Range</h3>
            <div className="space-y-2">
              {["Budget-Friendly", "Mid-Range", "Premium", "No Preference"].map((range) => (
                <button
                  key={range}
                  type="button"
                  onClick={() => setPriceRange(range)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-[10px] transition-all ${
                    priceRange === range
                      ? 'bg-[#a380a8] border border-[#a380a8]'
                      : 'bg-white/10 border border-white/20 hover:bg-white/15'
                  }`}
                >
                  <span className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] text-white tracking-[-0.65px]">{range}</span>
                  {priceRange === range && <Check size={16} className="text-white" />}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/95 to-transparent p-6 pt-8 z-20">
        {/* Status Message */}
        {saveMessage && (
          <div className={`mb-3 p-3 rounded-[10px] text-center font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[13px] tracking-[-0.65px] ${
            saveMessage.type === 'success' 
              ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
              : 'bg-red-500/20 text-red-300 border border-red-500/30'
          }`}>
            {saveMessage.text}
          </div>
        )}
        <button
          onClick={handleSave}
          disabled={isSaving || isLoading}
          className="w-full h-[50px] bg-[#a380a8] rounded-[12px] shadow-[0px_4px_12px_0px_rgba(0,0,0,0.25)] hover:bg-[#8d6d91] transition-colors active:scale-95 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? (
            <Loader2 size={20} className="text-white animate-spin" />
          ) : (
            <Save size={20} className="text-white" />
          )}
          <p className="font-['Konkhmer_Sleokchher:Regular',sans-serif] text-[16px] text-white tracking-[-0.7px]">
            {isSaving ? 'Saving...' : 'Save Health Profile'}
          </p>
        </button>
      </div>
    </div>
  );
}