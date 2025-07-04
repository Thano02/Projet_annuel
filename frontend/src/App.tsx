import { useEffect, useRef, useState } from "react";
import { CorrectionDialog } from "@/components/CorrectionDialog";

interface Detection {
  id: string;
  label: string;
  bbox: [number, number, number, number];
  score: number;
  image_width: number;
  image_height: number;
}

const CATEGORY_COLORS: Record<string, string> = {
  Biologique: "#28a745",
  Carton: "#ff8c00",
  Verre: "#007bff",
  Métal: "#6f42c1",
  Papier: "#17a2b8",
  Plastique: "#dc3545",
};

export default function App() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [selected, setSelected] = useState<Detection | null>(null);
  const [backendReady, setBackendReady] = useState(false);
  const [imgDims, setImgDims] = useState({ width: 0, height: 0 });
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  const API_URL = "https://turkey-adjusted-namely.ngrok-free.app";

  // Vérification que le backend Colab est prêt
  useEffect(() => {
    const pingBackend = async () => {
      for (let i = 0; i < 30; i++) {
        try {
          const res = await fetch(`${API_URL}/detections`);
          if (res.ok) {
            setBackendReady(true);
            break;
          }
        } catch {}
        await new Promise((r) => setTimeout(r, 1000));
      }
    };
    pingBackend();
  }, []);

  // Fetch des détections
  useEffect(() => {
    if (!backendReady) return;
    const fetchDetections = async () => {
      try {
        const res = await fetch(`${API_URL}/detections`);
        const data = await res.json();
        setDetections(data);
      } catch (err) {
        console.error("Erreur fetch detections:", err);
      }
    };
    fetchDetections();
    const interval = setInterval(fetchDetections, 1000);
    return () => clearInterval(interval);
  }, [backendReady]);

  // Dessin des bounding boxes
  useEffect(() => {
    if (!backendReady) return;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    const img = imgRef.current;
    if (!canvas || !ctx || !img || imgDims.width === 0) return;

    const draw = () => {
      canvas.width = img.clientWidth;
      canvas.height = img.clientHeight;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      detections.forEach((box) => {
        const scaleX = canvas.width / box.image_width;
        const scaleY = canvas.height / box.image_height;
        const [rawX, rawY, rawW, rawH] = box.bbox;
        const x = rawX * scaleX;
        const y = rawY * scaleY;
        const w = rawW * scaleX;
        const h = rawH * scaleY;

        const color = CATEGORY_COLORS[box.label] || "red";
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);

        ctx.fillStyle = color;
        ctx.font = "16px Arial";
        ctx.fillText(`${box.label} (${box.score})`, x, y - 8);
      });

      requestAnimationFrame(draw);
    };

    draw();
  }, [detections, backendReady, imgDims]);

  // Gestion des clics
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !backendReady) return;

    const handleClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      for (const box of detections) {
        const scaleX = canvas.width / box.image_width;
        const scaleY = canvas.height / box.image_height;
        const [rawX, rawY, rawW, rawH] = box.bbox;
        const bx = rawX * scaleX;
        const by = rawY * scaleY;
        const bw = rawW * scaleX;
        const bh = rawH * scaleY;

        if (x >= bx && x <= bx + bw && y >= by && y <= by + bh) {
          setSelected(box);
          break;
        }
      }
    };

    canvas.addEventListener("click", handleClick);
    return () => canvas.removeEventListener("click", handleClick);
  }, [detections, backendReady, imgDims]);

  if (!backendReady) {
    return (
      <div className="flex items-center justify-center min-h-screen text-xl font-semibold">
        Initialisation du backend cloud...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-center mb-4">Déposez votre plateau.</h1>

      <div className="flex justify-center mb-8 relative max-w-[900px] mx-auto">
        <img
          ref={imgRef}
          src={`${API_URL}/video_feed`}
          alt="Flux vidéo"
          onLoad={(e) => {
            const img = e.currentTarget;
            setImgDims({ width: img.naturalWidth, height: img.naturalHeight });
          }}
          className="rounded-2xl shadow-lg w-full max-h-[80vh] object-contain border"
        />
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-full z-10 pointer-events-auto"
        />
      </div>

      {selected && (
        <CorrectionDialog
          detection={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
