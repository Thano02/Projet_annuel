import { useState } from "react";
import { CorrectionDialog } from "@/components/CorrectionDialog";

const objetsDetectes = [
  { id: 1, categorie: "Plastique" },
  { id: 2, categorie: "Biologique" },
  { id: 3, categorie: "Métal" },
  { id: 4, categorie: "Papier" },
  { id: 5, categorie: "Verre" },
  { id: 6, categorie: "Carton" },
];

const exemples: Record<string, string> = {
  Biologique: "(restes de repas, peau de fruits)",
  Carton: "(boîtes, emballages)",
  Verre: "(bouteilles, pots)",
  Métal: "(canettes, couvercles)",
  Papier: "(journaux, feuilles)",
  Plastique: "(bouteilles, emballages)",
};

export default function App() {
  const [objetSelectionne, setObjetSelectionne] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold text-center mb-6">
        Quels déchets reconnais-tu ?
      </h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {objetsDetectes.map((objet, index) => (
          <div
            key={index}
            onClick={() => setObjetSelectionne(objet)}
            className="bg-white rounded-2xl shadow-md p-4 cursor-pointer hover:bg-blue-50 border border-gray-200 text-center"
          >
            <p className="text-2xl font-bold mb-2">
              {objet.categorie} {getEmoji(objet.categorie)}
            </p>
            <p className="text-sm text-gray-500">
              {exemples[objet.categorie]}
            </p>
          </div>
        ))}
      </div>

      {objetSelectionne && (
        <CorrectionDialog
          objet={objetSelectionne}
          onClose={() => setObjetSelectionne(null)}
        />
      )}
    </div>
  );
}

function getEmoji(categorie: string): string {
  const map: Record<string, string> = {
    Biologique: "🍌🥙",
    Carton: "📦",
    Verre: "🫙",
    Métal: "🍴",
    Papier: "📄",
    Plastique: "🧴",
  };
  return map[categorie] || "";
}
