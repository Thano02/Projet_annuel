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
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef  = useRef<HTMLVideoElement>(null);

  // 1️⃣ Démarrage de la caméra
  useEffect(() => {
    if (!videoRef.current) return;
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current!.srcObject = stream;
        videoRef.current!.play();
      })
      .catch(err => console.error("Erreur accès caméra :", err));
  }, []);

  // 2️⃣ Polling des détections (envoyer la frame à ton API)
  useEffect(() => {
    const fetchDetections = async () => {
      if (!videoRef.current || !canvasRef.current) return;

      // Capture frame dans le canvas
      const video  = videoRef.current;
      const canvas = canvasRef.current;
      const ctx    = canvas.getContext("2d")!;
      canvas.width  = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convertit en base64
      const blob = await new Promise<Blob>(r => canvas.toBlob(r, "image/jpeg")!);
      const buf  = await blob.arrayBuffer();
      const b64  = btoa(String.fromCharCode(...new Uint8Array(buf)));

      // Envoie au endpoint cloud (remplace par ton URL Functions)
      const res = await fetch("https://fa-garbage-classify.azurewebsites.net/api/classifyTrigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: [b64] })
      });
      const data = await res.json();
      setDetections(data);  // si ton endpoint renvoie un tableau de Detection
    };

    fetchDetections();
    const id = setInterval(fetchDetections, 300);
    return () => clearInterval(id);
  }, []);

  // 3️⃣ Dessin des bounding boxes
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx    = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    detections.forEach(box => {
      const scaleX = canvas.width  / box.image_width;
      const scaleY = canvas.height / box.image_height;
      const [x0, y0, w0, h0] = box.bbox;
      ctx.strokeStyle = "rgba(255,0,0,0.7)";
      ctx.lineWidth   = 2;
      ctx.strokeRect(x0*scaleX, y0*scaleY, w0*scaleX, h0*scaleY);
    });
  }, [detections]);

  // 4️⃣ Gestion du clic comme avant
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const onClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      for (const b of detections) {
        const scaleX = canvas.width  / b.image_width;
        const scaleY = canvas.height / b.image_height;
        const [x0, y0, w0, h0] = b.bbox;
        if (x >= x0*scaleX && x <= (x0+w0)*scaleX &&
            y >= y0*scaleY && y <= (y0+h0)*scaleY) {
          setSelected(b);
          break;
        }
      }
    };

    canvas.addEventListener("click", onClick);
    return () => canvas.removeEventListener("click", onClick);
  }, [detections]);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold text-center mb-4">
        Déposez votre plateau.
      </h1>

      <div className="flex justify-center mb-8 relative w-[1000px] mx-auto">
        {/* 1️⃣ la vidéo live */}
        <video
          ref={videoRef}
          className="rounded-2xl shadow-lg w-full border"
          muted
        />
        {/* 2️⃣ le canvas pour les boxes */}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-full z-10 pointer-events-auto"
        />
      </div>

      {/* 3️⃣ Dialog de correction si sélectionné */}
      {selected && (
        <CorrectionDialog
          detection={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
