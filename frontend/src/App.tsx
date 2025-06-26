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

export default function App() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [selected, setSelected] = useState<Detection | null>(null);
  const [apiUrl, setApiUrl] = useState<string | null>(null);
  const [backendReady, setBackendReady] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  // Chargement config.json
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const res = await fetch("/config.json");
        const data = await res.json();
        setApiUrl(data.API_URL);
      } catch (err) {
        console.error("Erreur chargement config.json", err);
      }
    };
    loadConfig();
  }, []);

  // Ping backend (dès qu'il répond, on monte l'image MJPEG)
  useEffect(() => {
    if (!apiUrl) return;
    const checkBackend = async () => {
      let attempts = 0;
      while (attempts < 30) {
        try {
          const res = await fetch(`${apiUrl}/detections`);
          if (res.ok) {
            setBackendReady(true);
            return;
          }
        } catch {}
        await new Promise((r) => setTimeout(r, 500));
        attempts++;
      }
    };
    checkBackend();
  }, [apiUrl]);

  // Récupération des détections toutes les 500ms
  useEffect(() => {
    if (!backendReady || !apiUrl) return;
    const fetchDetections = async () => {
      try {
        const res = await fetch(`${apiUrl}/detections`);
        const data = await res.json();
        setDetections(data);
      } catch (err) {
        console.error("Erreur fetch detections:", err);
      }
    };

    fetchDetections();
    const interval = setInterval(fetchDetections, 500);
    return () => clearInterval(interval);
  }, [backendReady, apiUrl]);

  // Dessin des bounding boxes
  useEffect(() => {
    if (!backendReady) return;
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    const img = imgRef.current;
    if (!canvas || !ctx || !img) return;

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

        ctx.strokeStyle = "rgba(255, 0, 0, 0.7)";
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);
      });

      requestAnimationFrame(draw);
    };

    draw();
  }, [detections, backendReady]);

  // Gestion des clics sur les bounding boxes
  useEffect(() => {
    if (!backendReady) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

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
  }, [detections, backendReady]);

  if (!apiUrl) {
    return (
      <div className="flex items-center justify-center min-h-screen text-xl font-semibold">
        Chargement configuration...
      </div>
    );
  }

  if (!backendReady) {
    return (
      <div className="flex items-center justify-center min-h-screen text-xl font-semibold">
        Initialisation du backend cloud...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold text-center mb-4">
        Déposez votre plateau.
      </h1>

      <div className="flex justify-center mb-8 relative w-[1000px] mx-auto">
        <img
          ref={imgRef}
          src={`${apiUrl}/video_feed`}
          alt="Flux vidéo"
          className="rounded-2xl shadow-lg w-full border"
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