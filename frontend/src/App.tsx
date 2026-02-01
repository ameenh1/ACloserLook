import { useState } from "react";
import HomeScreen from "./components/HomeScreen";
import LoginScreen from "./components/LoginScreen";
import CreateAccountScreen from "./components/CreateAccountScreen";
import HomePageScreen from "./components/HomePageScreen";
import BarcodeScannerScreen from "./components/BarcodeScannerScreen";
import ProductResultScreen from "./components/ProductResultScreen";
import ProfileScreen from "./components/ProfileScreen";

type Screen = "home" | "login" | "create-account" | "homepage" | "scanner" | "result" | "profile";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>("home");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [scannedBarcode, setScannedBarcode] = useState("");

  const handleLogin = () => {
    setIsLoggedIn(true);
    setCurrentScreen("homepage");
  };

  const handleCreateAccount = () => {
    setIsLoggedIn(true);
    setCurrentScreen("homepage");
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentScreen("home");
  };

  const handleScanSuccess = (barcode: string) => {
    setScannedBarcode(barcode);
    setCurrentScreen("result");
  };

  const handleScanProduct = (barcode?: string) => {
    if (barcode) {
      // User clicked on recent scan - go directly to results
      setScannedBarcode(barcode);
      setCurrentScreen("result");
    } else {
      // User wants to scan new product
      setCurrentScreen("scanner");
    }
  };

  return (
    <div className="size-full flex items-center justify-center bg-black">
      {currentScreen === "home" && (
        <HomeScreen
          onLogin={() => setCurrentScreen("login")}
          onCreateAccount={() => setCurrentScreen("create-account")}
        />
      )}
      {currentScreen === "login" && (
        <LoginScreen
          onBack={() => setCurrentScreen("home")}
          onLoginSuccess={handleLogin}
        />
      )}
      {currentScreen === "create-account" && (
        <CreateAccountScreen
          onBack={() => setCurrentScreen("home")}
          onAccountCreated={handleCreateAccount}
        />
      )}
      {currentScreen === "homepage" && (
        <HomePageScreen
          onScanProduct={handleScanProduct}
          onLogout={handleLogout}
          onProfile={() => setCurrentScreen("profile")}
        />
      )}
      {currentScreen === "scanner" && (
        <BarcodeScannerScreen
          onBack={() => setCurrentScreen("homepage")}
          onScanSuccess={handleScanSuccess}
        />
      )}
      {currentScreen === "result" && (
        <ProductResultScreen
          barcode={scannedBarcode}
          onBack={() => setCurrentScreen("homepage")}
          onScanAnother={() => setCurrentScreen("scanner")}
        />
      )}
      {currentScreen === "profile" && (
        <ProfileScreen
          onBack={() => setCurrentScreen("homepage")}
        />
      )}
    </div>
  );
}