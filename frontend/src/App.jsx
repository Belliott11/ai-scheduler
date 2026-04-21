import { useState } from "react";
import Upload from "./pages/Upload";
import Calendar from "./pages/Calendar";
import Schedule from "./pages/Schedule";
import Export from "./pages/Export";
import "./index.css";

const steps = [
  { id: 1, name: "Upload" },
  { id: 2, name: "Review" },
  { id: 3, name: "Calendar" },
  { id: 4, name: "Schedule" },
  { id: 5, name: "Export" },
];

export default function App() {
  const [step, setStep] = useState(1);

  const renderStep = () => {
    switch (step) {
      case 1: return <Upload next={() => setStep(2)} />;
      case 3: return <Calendar next={() => setStep(4)} />;
      case 4: return <Schedule next={() => setStep(5)} />;
      case 5: return <Export />;
      default: return <Upload next={() => setStep(2)} />;
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
            onClick={() => setStep(s.id)}
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