"use client";

import { useState, useRef, useCallback } from "react";
import ProjectResult from "./ProjectResult";
import {
  MicIcon, EditIcon, MusicNoteIcon, LinkIcon, PhotoIcon,
  CodeIcon, AddIcon, CloseIcon, CheckCircleIcon, RadioUncheckIcon,
} from "./Icons";

type LoadingStep = { label: string; durationMs: number };

const LOADING_STEPS: LoadingStep[] = [
  { label: "Transcrevendo áudio com Whisper...", durationMs: 7000 },
  { label: "Coletando dados das URLs...", durationMs: 9000 },
  { label: "Analisando imagens com Claude Vision...", durationMs: 11000 },
  { label: "Gerando plano completo com Claude...", durationMs: 28000 },
  { label: "Criando estrutura do projeto no PC...", durationMs: 3000 },
];

type AppState = "idle" | "loading" | "success" | "error";

export default function ProspecForm() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [inputMode, setInputMode] = useState<"audio" | "text">("audio");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [transcriptText, setTranscriptText] = useState("");
  const [urls, setUrls] = useState<string[]>(["", "", ""]);
  const [images, setImages] = useState<File[]>([]);
  const [openVscode, setOpenVscode] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const stepTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const startStepTimer = useCallback(() => {
    let step = 0;
    const advance = () => {
      if (step < LOADING_STEPS.length - 1) {
        step++;
        setCurrentStep(step);
        stepTimerRef.current = setTimeout(advance, LOADING_STEPS[step].durationMs);
      }
    };
    stepTimerRef.current = setTimeout(advance, LOADING_STEPS[0].durationMs);
  }, []);

  const stopStepTimer = useCallback(() => {
    if (stepTimerRef.current) clearTimeout(stepTimerRef.current);
  }, []);

  const addUrl = () => setUrls((prev) => [...prev, ""]);
  const removeUrl = (i: number) => setUrls((prev) => prev.filter((_, idx) => idx !== i));
  const updateUrl = (i: number, val: string) =>
    setUrls((prev) => prev.map((u, idx) => (idx === i ? val : u)));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMode === "audio" && !audioFile) {
      setError("Selecione um arquivo de áudio ou grave pelo celular.");
      return;
    }
    if (inputMode === "text" && !transcriptText.trim()) {
      setError("Digite o texto do briefing.");
      return;
    }

    setAppState("loading");
    setCurrentStep(0);
    setError("");
    startStepTimer();

    const formData = new FormData();
    if (inputMode === "audio" && audioFile) {
      formData.append("audio", audioFile);
    } else {
      formData.append("transcript", transcriptText);
    }
    urls.filter((u) => u.trim()).forEach((u) => formData.append("urls", u));
    images.forEach((img) => formData.append("images", img));
    formData.append("language", "pt");
    formData.append("open_vscode", String(openVscode));

    try {
      const res = await fetch(`${API_URL}/api/projects`, {
        method: "POST",
        body: formData,
      });

      stopStepTimer();
      setCurrentStep(LOADING_STEPS.length - 1);

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail ?? `Erro ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      setAppState("success");
    } catch (err: unknown) {
      stopStepTimer();
      const msg = err instanceof Error ? err.message : "Erro desconhecido.";
      setError(msg);
      setAppState("error");
    }
  };

  const reset = () => {
    setAppState("idle");
    setResult(null);
    setError("");
    setCurrentStep(0);
    setAudioFile(null);
    setTranscriptText("");
    setUrls(["", "", ""]);
    setImages([]);
  };

  if (appState === "success" && result) {
    return <ProjectResult result={result} onNew={reset} />;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Toggle áudio / texto */}
      <div className="flex rounded-xl overflow-hidden border border-surface-700">
        {(["audio", "text"] as const).map((mode) => (
          <button
            key={mode}
            type="button"
            onClick={() => setInputMode(mode)}
            className={`flex-1 py-3 text-sm font-medium transition-colors inline-flex items-center justify-center gap-1.5 ${
              inputMode === mode
                ? "bg-brand-600 text-white"
                : "bg-surface-800 text-zinc-400 hover:text-white"
            }`}
          >
            {mode === "audio" ? (
              <><MicIcon size={16} /> Áudio</>
            ) : (
              <><EditIcon size={16} /> Texto</>
            )}
          </button>
        ))}
      </div>

      {/* Input de áudio */}
      {inputMode === "audio" && (
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Áudio do briefing
          </label>
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-surface-600 rounded-xl cursor-pointer hover:border-brand-500 transition-colors bg-surface-800/50">
            {audioFile ? (
              <div className="text-center">
                <MusicNoteIcon size={28} className="text-brand-400 mx-auto mb-1" />
                <div className="text-sm text-brand-400">{audioFile.name}</div>
                <div className="text-xs text-zinc-500 mt-1">
                  {(audioFile.size / 1024 / 1024).toFixed(1)} MB
                </div>
              </div>
            ) : (
              <div className="text-center">
                <MicIcon size={32} className="text-zinc-500 mx-auto mb-1" />
                <div className="text-sm text-zinc-400">
                  Toque para gravar ou escolher arquivo
                </div>
                <div className="text-xs text-zinc-600 mt-1">
                  MP3, M4A, WAV, OGG, WEBM
                </div>
              </div>
            )}
            <input
              type="file"
              accept="audio/*"
              className="hidden"
              onChange={(e) => setAudioFile(e.target.files?.[0] ?? null)}
            />
          </label>
        </div>
      )}

      {/* Input de texto */}
      {inputMode === "text" && (
        <div>
          <label className="block text-sm font-medium text-zinc-300 mb-2">
            Texto do briefing
          </label>
          <textarea
            value={transcriptText}
            onChange={(e) => setTranscriptText(e.target.value)}
            placeholder="Descreva o projeto: o que é, para quem é, funcionalidades, referências, prazo estimado..."
            rows={6}
            className="w-full bg-surface-800 border border-surface-700 rounded-xl px-4 py-3 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-brand-500 resize-none"
          />
        </div>
      )}

      {/* URLs */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-zinc-300 inline-flex items-center gap-1.5">
            <LinkIcon size={15} className="text-zinc-500" />
            URLs de referência{" "}
            <span className="text-zinc-600 font-normal">(opcional)</span>
          </label>
          <button
            type="button"
            onClick={addUrl}
            className="text-xs text-brand-400 hover:text-brand-300 inline-flex items-center gap-0.5"
          >
            <AddIcon size={14} /> Adicionar
          </button>
        </div>
        <div className="space-y-2">
          {urls.map((url, i) => (
            <div key={i} className="flex gap-2">
              <input
                type="url"
                value={url}
                onChange={(e) => updateUrl(i, e.target.value)}
                placeholder="https://site-referencia.com"
                className="flex-1 bg-surface-800 border border-surface-700 rounded-lg px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-brand-500"
              />
              {urls.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeUrl(i)}
                  className="text-zinc-600 hover:text-red-400 px-1.5 flex items-center"
                >
                  <CloseIcon size={18} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Imagens */}
      <div>
        <label className="block text-sm font-medium text-zinc-300 mb-2">
          Imagens de referência{" "}
          <span className="text-zinc-600 font-normal">(opcional)</span>
        </label>
        <label className="flex items-center gap-3 w-full border border-surface-700 rounded-xl px-4 py-3 cursor-pointer hover:border-brand-500 transition-colors bg-surface-800/50">
          <PhotoIcon size={20} className="text-zinc-500 shrink-0" />
          <span className="text-sm text-zinc-400">
            {images.length > 0
              ? `${images.length} imagem(ns) selecionada(s)`
              : "Selecionar imagens"}
          </span>
          <input
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => setImages(Array.from(e.target.files ?? []))}
          />
        </label>
        {images.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {images.map((img, i) => (
              <span
                key={i}
                className="text-xs bg-surface-700 text-zinc-300 rounded px-2 py-1"
              >
                {img.name}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Toggle abrir editor */}
      <div
        className="flex items-center gap-3 cursor-pointer select-none"
        onClick={() => setOpenVscode((v) => !v)}
      >
        <div
          className={`w-10 h-6 rounded-full transition-colors relative shrink-0 ${
            openVscode ? "bg-brand-600" : "bg-surface-700"
          }`}
        >
          <div
            className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
              openVscode ? "translate-x-5" : "translate-x-1"
            }`}
          />
        </div>
        <span className="text-sm text-zinc-400 inline-flex items-center gap-1.5">
          <CodeIcon size={15} className="text-zinc-600" />
          Abrir VS Code ao finalizar
        </span>
      </div>

      {/* Loading */}
      {appState === "loading" && (
        <div className="bg-surface-800/50 border border-surface-700 rounded-xl p-4 space-y-3">
          {LOADING_STEPS.map((step, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="w-5 h-5 flex items-center justify-center shrink-0">
                {i < currentStep ? (
                  <CheckCircleIcon size={18} className="text-green-400" />
                ) : i === currentStep ? (
                  <div className="w-4 h-4 border-2 border-brand-400 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <RadioUncheckIcon size={16} className="text-zinc-700" />
                )}
              </div>
              <span
                className={`text-sm ${
                  i < currentStep
                    ? "text-green-400"
                    : i === currentStep
                    ? "text-brand-300"
                    : "text-zinc-700"
                }`}
              >
                {step.label}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Erro */}
      {appState === "error" && (
        <div className="bg-red-950/50 border border-red-800 rounded-xl p-4 text-sm text-red-300">
          {error}
          <button
            type="button"
            onClick={() => setAppState("idle")}
            className="block mt-2 text-xs text-red-400 underline"
          >
            Tentar novamente
          </button>
        </div>
      )}

      {/* Botão enviar */}
      <button
        type="submit"
        disabled={appState === "loading"}
        className="w-full py-4 bg-brand-600 hover:bg-brand-500 disabled:bg-surface-700 disabled:text-zinc-500 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors text-sm"
      >
        {appState === "loading" ? "Gerando projeto..." : "Gerar Projeto"}
      </button>
    </form>
  );
}
