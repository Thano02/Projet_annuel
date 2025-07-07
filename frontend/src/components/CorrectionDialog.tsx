import { useState } from "react";
import { Button } from "@/components/ui/button";

const categories = [
  { label: "Biologique", value: "biological", emoji: "🍌🥙" },
  { label: "Carton", value: "cardboard", emoji: "📦" },
  { label: "Verre", value: "glass", emoji: "🫙" },
  { label: "Métal", value: "metal", emoji: "🍴" },
  { label: "Papier", value: "paper", emoji: "📄" },
  { label: "Plastique", value: "plastic", emoji: "🧴" },
];

interface Detection {
  id: string;
  label: string;
  bbox: [number, number, number, number];
  score: number;
  image_width: number;
  image_height: number;
}

export function CorrectionDialog({
  onClose,
  detection,
}: {
  onClose: () => void;
  detection: Detection;
}) {
  const [step, setStep] = useState<1 | 2>(1);
  const [wrongCategory, setWrongCategory] = useState<string | null>(null);
  const [correctedCategory, setCorrectedCategory] = useState<string | null>(null);

  const apiUrl =
    import.meta.env.VITE_API_URL ?? import.meta.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const submitCorrection = async () => {
    if (!wrongCategory || !correctedCategory) return;

    try {
      const res = await fetch(`${apiUrl}/correction`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          wrong: wrongCategory,
          corrected: correctedCategory,
          detection: detection,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        console.error("Erreur backend :", data);
        alert("❌ Erreur côté serveur : " + (data.message || "inconnue"));
        return;
      }

      alert("✅ Correction enregistrée !");
      onClose();
    } catch (err) {
      console.error("Erreur réseau :", err);
      alert("❌ Erreur réseau lors de l’envoi de la correction");
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
                  key={cat.value}
                  onClick={() => setWrongCategory(cat.value)}
                  className={`rounded-xl border p-4 flex items-center justify-center text-lg font-medium transition ${
                    wrongCategory === cat.value
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
              <Button onClick={() => setStep(2)} disabled={!wrongCategory}>
                Valider
              </Button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="text-xl font-semibold mb-4 text-center">
              Quelle est la bonne catégorie pour ce déchet ?
            </h2>

            <div className="grid grid-cols-2 gap-3 mb-6">
              {categories.map((cat) => (
                <button
                  key={cat.value}
                  onClick={() => setCorrectedCategory(cat.value)}
                  className={`rounded-xl border p-4 flex items-center justify-center text-lg font-medium transition ${
                    correctedCategory === cat.value
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
              <Button onClick={submitCorrection} disabled={!correctedCategory}>
                Envoyer
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
