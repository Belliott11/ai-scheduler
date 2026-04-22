import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import Upload from "./pages/Upload";
import Calendar from "./pages/Calendar";
import Schedule from "./pages/Schedule";
import Export from "./pages/Export";
import "./index.css";

const steps = [
  { id: 1, name: "Upload", path: "/" },
  { id: 2, name: "Calendar", path: "/calendar" },
  { id: 3, name: "Schedule", path: "/schedule" },
  { id: 4, name: "Export", path: "/export" },
];

function AppContent() {
  const [step, setStep] = useState(1);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const currentPath = location.pathname;
    const currentStep = steps.find(s => s.path === currentPath);
    if (currentStep) {
      setStep(currentStep.id);
    }
  }, [location.pathname]);

  const handleStepClick = (stepId) => {
    setStep(stepId);
    const stepData = steps.find(s => s.id === stepId);
    if (stepData) {
      navigate(stepData.path);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1: return <Upload next={() => handleStepClick(2)} />;
      case 2: return <Calendar next={() => handleStepClick(3)} />;
      case 3: return <Schedule next={() => handleStepClick(4)} />;
      case 4: return <Export />;
      default: return <Upload next={() => handleStepClick(2)} />;
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>AI Scheduler</h2>
        {steps.map(s => (
          <div
            key={s.id}
            className={`step ${step === s.id ? "active" : ""}`}
            onClick={() => handleStepClick(s.id)}
          >
            {s.name}
          </div>
        ))}
      </aside>

      <main className="main">
        {renderStep()}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}