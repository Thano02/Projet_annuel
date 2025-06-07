import { useState } from "react";
import { TrashCard } from "@/components/TrashCard";
import { CorrectionDialog } from "@/components/CorrectionDialog";

const objetsDetectes = [
  { id: 1, nom: "Bouteille", categorie: "Plastique" },
  { id: 2, nom: "Canette", categorie: "Métal" },
  { id: 3, nom: "Journal", categorie: "Papier" },
];

export default function Home() {
  const [selectedObject, setSelectedObject] = useState<any>(null);

  return (
    <div className="p-4 grid gap-6">
      <h1 className="text-2xl font-bold text-center">Quel déchet est mal classé ?</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {objetsDetectes.map((objet) => (
          <TrashCard
            key={objet.id}
            objet={objet}
            onClick={() => setSelectedObject(objet)}
          />
        ))}
      </div>

      {selectedObject && (
        <CorrectionDialog
          objet={selectedObject}
          onClose={() => setSelectedObject(null)}
        />
      )}
    </div>
  );
}
