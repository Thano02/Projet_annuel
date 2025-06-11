import { useState } from "react";
import { Button } from "@/components/ui/button";

const categories = [
  { label: "Biologique", emoji: "🍌🥙" },
  { label: "Carton", emoji: "📦" },
  { label: "Verre", emoji: "🫙" },
  { label: "Métal", emoji: "🍴" },
  { label: "Papier", emoji: "📄" },
  { label: "Plastique", emoji: "🧴" },
];

export function CorrectionDialog({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState<1 | 2>(1);
  const [wrongCategory, setWrongCategory] = useState<string | null>(null);
  const [correctedCategory, setCorrectedCategory] = useState<string | null>(null);

  const submitCorrection = async () => {
    if (!wrongCategory || !correctedCategory) return;

    try {
      const res = await fetch("http://localhost:8000/correction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          wrong: wrongCategory,
          corrected: correctedCategory,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        console.error("Erreur API :", data);
        alert("❌ Erreur : " + data.message || "Problème d’envoi.");
        return;
      }

      alert("✅ Correction enregistrée !");
      onClose();
    } catch (err) {
      console.error("Erreur réseau :", err);
      alert("❌ Erreur réseau");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
        {step === 1 && (
          <>
            <h2 className="text-xl font-semibold mb-4 text-center">
              Quelle catégorie a été assignée par erreur ?
            </h2>

            <div className="grid grid-cols-2 gap-3 mb-6">
              {categories.map((cat) => (
                <button
                  key={cat.label}
                  onClick={() => setWrongCategory(cat.label)}
                  className={`rounded-xl border p-4 flex items-center justify-center text-lg font-medium transition ${
                    wrongCategory === cat.label
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 hover:bg-gray-200"
                  }`}
                >
                  <span className="mr-2 text-xl">{cat.label}</span>
                  {cat.emoji}
                </button>
              ))}
            </div>

            <div className="flex justify-between">
              <Button variant="ghost" onClick={onClose}>
                Annuler
              </Button>
              <Button
                onClick={() => setStep(2)}
                disabled={!wrongCategory}
              >
                Valider
              </Button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="text-xl font-semibold mb-4 text-center">
              Quelle est la bonne catégorie pour le déchet ?
            </h2>

            <div className="grid grid-cols-2 gap-3 mb-6">
              {categories.map((cat) => (
                <button
                  key={cat.label}
                  onClick={() => setCorrectedCategory(cat.label)}
                  className={`rounded-xl border p-4 flex items-center justify-center text-lg font-medium transition ${
                    correctedCategory === cat.label
                      ? "bg-green-600 text-white"
                      : "bg-gray-100 hover:bg-gray-200"
                  }`}
                >
                  <span className="mr-2 text-xl">{cat.label}</span>
                  {cat.emoji}
                </button>
              ))}
            </div>

            <div className="flex justify-between">
              <Button variant="ghost" onClick={() => setStep(1)}>
                Retour
              </Button>
              <Button
                onClick={submitCorrection}
                disabled={!correctedCategory}
              >
                Valider
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
