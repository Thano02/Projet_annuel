// frontend/src/App.tsx
import React, { useEffect, useState } from "react";

const API_URL = "https://fa-garbage-classify.azurewebsites.net/api/classifyTrigger";

export default function App() {
  const [prediction, setPrediction] = useState<{ label: string; score: number } | null>(null);

  useEffect(() => {
    // On crée video + canvas
    const video = document.createElement("video");
    video.width = 320;
    video.height = 240;
    video.style.border = "2px solid #555";

    const container = document.getElementById("video-container");
    if (container) container.appendChild(video);

    const canvas = document.createElement("canvas");
    canvas.width = 320;
    canvas.height = 240;

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        video.srcObject = stream;
        video.play();

        const intervalId = setInterval(async () => {
          const ctx = canvas.getContext("2d")!;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          const blob: Blob = await new Promise(r => canvas.toBlob(r, "image/jpeg")!);
          const buf = await blob.arrayBuffer();
          const b64 = btoa(
            Array.from(new Uint8Array(buf))
                 .map(b => String.fromCharCode(b))
                 .join("")
          );

          const resp = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ data: [b64] })
          });
          const json = await resp.json();
          setPrediction({ label: json.predicted_label, score: json.score });
        }, 500);

        return () => {
          clearInterval(intervalId);
          (video.srcObject as MediaStream).getTracks().forEach(t => t.stop());
        };
      })
      .catch(err => console.error("Erreur caméra :", err));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Live Garbage Classifier</h1>
      <div id="video-container" className="mb-4" />
      {prediction && (
        <div className="p-2 bg-gray-800 text-white rounded">
          Classe : <strong>{prediction.label}</strong> — Confiance : {Math.round(prediction.score * 100)}%
        </div>
      )}
    </div>
  );
}
