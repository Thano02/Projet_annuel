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
    alert(`Merci ! Vous avez corrigé ${objet.categorie} en ${selectedCategory}`);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
        <h2 className="text-xl font-semibold mb-4 text-center">
          Quelle est la bonne catégorie pour le déchet ?
        </h2>

        <div className="grid grid-cols-2 gap-3 mb-6">
          {categories.map((cat) => (
            <button
              key={cat.label}
              onClick={() => setSelectedCategory(cat.label)}
              className={`rounded-xl border p-4 flex items-center justify-center text-lg font-medium transition ${
                selectedCategory === cat.label
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 hover:bg-gray-200"
              }`}
            >
              <span className="mr-2 text-xl">{cat.label}</span>
              {cat.emoji}
            </button>
          ))}
        </div>

        <div className="text-center">
          <Button disabled={!selectedCategory} onClick={handleSubmit}>
            Suivant
          </Button>
        </div>
      </div>
    </div>
  );
}
