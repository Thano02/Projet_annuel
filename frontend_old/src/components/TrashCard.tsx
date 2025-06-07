import { Card, CardContent } from "@/components/ui/card";

export function TrashCard({ objet, onClick }: { objet: any; onClick: () => void }) {
  return (
    <Card
      onClick={onClick}
      className="cursor-pointer bg-white hover:shadow-lg transition border-2 border-gray-200 hover:border-blue-400 rounded-2xl"
    >
      <CardContent className="p-6 flex flex-col items-center text-center space-y-2">
        <div className="text-4xl">🗑️</div>
        <p className="text-lg font-semibold">{objet.nom}</p>
        <p className="text-sm text-gray-500">Catégorie : {objet.categorie}</p>
      </CardContent>
    </Card>
  );
}
