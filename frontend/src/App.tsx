import { useEffect, useRef, useState } from "react";
import { CorrectionDialog } from "@/components/CorrectionDialog";

export default function App() {
  const [showDialog, setShowDialog] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    const img = imgRef.current;
    if (!canvas || !ctx || !img) return;

    // Taille du canvas = taille du flux caméra
    canvas.width = img.clientWidth;
    canvas.height = img.clientHeight;

    // Ajoute un événement de clic
    const handleClick = () => {
      setShowDialog(true);
    };

    canvas.addEventListener("click", handleClick);
    return () => canvas.removeEventListener("click", handleClick);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold text-center mb-6">
        Déposez votre plateau.
      </h1>

      <div
        style={{
          position: "relative",
          width: "1000px",
          margin: "0 auto",
        }}
      >
        <img
          id="stream"
          ref={imgRef}
          src="http://localhost:8000/video_feed"
          alt="Flux caméra"
          style={{ width: "100%", borderRadius: "12px" }}
        />
        <canvas
          ref={canvasRef}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            zIndex: 10,
            pointerEvents: "auto",
          }}
        />
      </div>

      {showDialog && (
        <CorrectionDialog objet={{ label: "Inconnu" }} onClose={() => setShowDialog(false)} />
      )}
    </div>
  );
}
