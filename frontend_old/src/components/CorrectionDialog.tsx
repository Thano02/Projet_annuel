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

export function CorrectionDialog({ objet, onClose }: { objet: any; onClose: () => void }) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const handleSubmit = () => {
    if (!selectedCategory) return;
    alert(`Merci ! Vous avez corrigé "${objet.nom}" en : ${selectedCategory}`);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-2xl p-6 shadow-xl w-[90%] max-w-md">
        <h2 className="text-xl font-bold mb-4 text-center">
          Quelle est la bonne catégorie pour <strong>{objet.nom}</strong> ?
        </h2>

        <div className="grid grid-cols-2 gap-4 mb-6">
          {categories.map((cat) => (
            <button
              key={cat.label}
              onClick={() => setSelectedCategory(cat.label)}
              className={`flex items-center justify-center p-4 rounded-xl border text-lg font-medium transition ${
                selectedCategory === cat.label
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 hover:bg-gray-200"
              }`}
            >
              <span className="mr-2 text-xl">{cat.emoji}</span>
              {cat.label}
            </button>
          ))}
        </div>

        <div className="text-center">
          <Button onClick={handleSubmit} disabled={!selectedCategory}>
            Suivant
          </Button>
        </div>
      </div>
    </div>
  );
}
