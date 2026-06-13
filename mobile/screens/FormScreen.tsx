import { useState, useRef, useCallback, useEffect } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, Switch,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import AudioRecorder from "../components/AudioRecorder";
import { API_URL, C } from "../constants";

const LOADING_STEPS = [
  "Transcrevendo áudio com Whisper...",
  "Coletando dados das URLs...",
  "Analisando imagens com Claude Vision...",
  "Gerando plano com Claude...",
  "Criando estrutura do projeto no PC...",
];

// Percentual acumulado esperado ao final de cada etapa (baseado nas durações)
const STEP_END_PCT = [12, 28, 47, 95, 99];

type InputMode = "audio" | "text";
type AppState = "idle" | "loading" | "error";

interface Props {
  onResult: (data: Record<string, unknown>) => void;
}

export default function FormScreen({ onResult }: Props) {
  const [inputMode, setInputMode] = useState<InputMode>("audio");
  const [recordedUri, setRecordedUri] = useState<string | null>(null);
  const [transcriptText, setTranscriptText] = useState("");
  const [urls, setUrls] = useState(["", "", ""]);
  const [images, setImages] = useState<ImagePicker.ImagePickerAsset[]>([]);
  const [openVscode, setOpenVscode] = useState(false);
  const [appState, setAppState] = useState<AppState>("idle");
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const stepTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (appState !== "loading") return;
    const target = STEP_END_PCT[currentStep] ?? 99;
    const interval = setInterval(() => {
      setProgress((prev) => (prev >= target ? prev : Math.min(prev + 0.4, target)));
    }, 80);
    return () => clearInterval(interval);
  }, [currentStep, appState]);

  const startStepTimer = useCallback(() => {
    const durations = [7000, 9000, 11000, 28000, 3000];
    let step = 0;
    const advance = () => {
      if (step < durations.length - 1) {
        step++;
        setCurrentStep(step);
        stepTimer.current = setTimeout(advance, durations[step]);
      }
    };
    stepTimer.current = setTimeout(advance, durations[0]);
  }, []);

  const stopStepTimer = () => {
    if (stepTimer.current) clearTimeout(stepTimer.current);
  };

  const pickImages = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== "granted") return;
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      allowsMultipleSelection: true,
      quality: 0.8,
    });
    if (!result.canceled) setImages(result.assets);
  };

  const submit = async () => {
    if (inputMode === "audio" && !recordedUri) {
      setError("Grave ou selecione um áudio primeiro.");
      return;
    }
    if (inputMode === "text" && !transcriptText.trim()) {
      setError("Digite o texto do briefing.");
      return;
    }

    setAppState("loading");
    setCurrentStep(0);
    setProgress(0);
    setError("");
    startStepTimer();

    const formData = new FormData();

    if (inputMode === "audio" && recordedUri) {
      const ext = recordedUri.split(".").pop() ?? "m4a";
      formData.append("audio", {
        uri: recordedUri,
        type: `audio/${ext}`,
        name: `briefing.${ext}`,
      } as unknown as Blob);
    } else {
      formData.append("transcript", transcriptText);
    }

    urls.filter((u) => u.trim()).forEach((u) => formData.append("urls", u));

    images.forEach((img, i) => {
      const ext = img.uri.split(".").pop() ?? "jpg";
      formData.append("images", {
        uri: img.uri,
        type: `image/${ext}`,
        name: `ref_${i}.${ext}`,
      } as unknown as Blob);
    });

    formData.append("language", "pt");
    formData.append("open_vscode", String(openVscode));

    // XMLHttpRequest suporta { uri, type, name } para arquivos locais no React Native
    // fetch nativo do RN 0.85+ não suporta esse padrão (throws "Unsupported FormDataPart")
    try {
      const data = await new Promise<Record<string, unknown>>((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", `${API_URL}/api/projects`);
        xhr.onload = () => {
          stopStepTimer();
          setCurrentStep(LOADING_STEPS.length - 1);
          setProgress(100);
          if (xhr.status >= 200 && xhr.status < 300) {
            try { resolve(JSON.parse(xhr.responseText)); }
            catch { reject(new Error("Resposta inválida da API.")); }
          } else {
            try {
              const err = JSON.parse(xhr.responseText);
              reject(new Error(err.detail ?? `Erro ${xhr.status}`));
            } catch { reject(new Error(`Erro ${xhr.status}`)); }
          }
        };
        xhr.onerror = () => { stopStepTimer(); reject(new Error("Erro de rede. A API está rodando?")); };
        xhr.send(formData);
      });
      onResult(data);
    } catch (err: unknown) {
      stopStepTimer();
      setError(err instanceof Error ? err.message : "Erro desconhecido.");
      setAppState("error");
    }
  };

  const isLoading = appState === "loading";

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.content}
      keyboardShouldPersistTaps="handled"
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>ProspecMan</Text>
        <Text style={styles.subtitle}>Briefing de áudio → projeto com IA</Text>
      </View>

      {/* Toggle modo */}
      <View style={styles.modeRow}>
        {(["audio", "text"] as InputMode[]).map((mode) => (
          <TouchableOpacity
            key={mode}
            style={[styles.modeBtn, inputMode === mode && styles.modeBtnActive]}
            onPress={() => setInputMode(mode)}
          >
            <Text style={[styles.modeTxt, inputMode === mode && styles.modeTxtActive]}>
              {mode === "audio" ? "🎙️  Áudio" : "✏️  Texto"}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Áudio */}
      {inputMode === "audio" && (
        <AudioRecorder
          recordedUri={recordedUri}
          onRecorded={setRecordedUri}
          onClear={() => setRecordedUri(null)}
        />
      )}

      {/* Texto */}
      {inputMode === "text" && (
        <TextInput
          style={styles.textArea}
          multiline
          numberOfLines={6}
          value={transcriptText}
          onChangeText={setTranscriptText}
          placeholder="Descreva o projeto: o que é, para quem, funcionalidades, prazo..."
          placeholderTextColor={C.textMuted}
          textAlignVertical="top"
        />
      )}

      {/* URLs */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.label}>🔗 URLs de referência</Text>
          <TouchableOpacity onPress={() => setUrls((u) => [...u, ""])}>
            <Text style={styles.addBtn}>+ Adicionar</Text>
          </TouchableOpacity>
        </View>
        {urls.map((url, i) => (
          <View key={i} style={styles.urlRow}>
            <TextInput
              style={[styles.input, { flex: 1 }]}
              value={url}
              onChangeText={(v) => setUrls((u) => u.map((x, j) => (j === i ? v : x)))}
              placeholder="https://site-referencia.com"
              placeholderTextColor={C.textMuted}
              keyboardType="url"
              autoCapitalize="none"
              autoCorrect={false}
            />
            {urls.length > 1 && (
              <TouchableOpacity
                onPress={() => setUrls((u) => u.filter((_, j) => j !== i))}
                style={styles.removeBtn}
              >
                <Text style={styles.removeTxt}>✕</Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
      </View>

      {/* Imagens */}
      <View style={styles.section}>
        <Text style={styles.label}>🖼️  Imagens de referência</Text>
        <TouchableOpacity style={styles.imagePickerBtn} onPress={pickImages}>
          <Text style={styles.imagePickerTxt}>
            {images.length > 0
              ? `${images.length} imagem(ns) selecionada(s)`
              : "Selecionar da galeria"}
          </Text>
        </TouchableOpacity>
        {images.length > 0 && (
          <View style={styles.imageChips}>
            {images.map((img, i) => (
              <View key={i} style={styles.chip}>
                <Text style={styles.chipTxt} numberOfLines={1}>
                  {img.fileName ?? `img_${i + 1}`}
                </Text>
              </View>
            ))}
          </View>
        )}
      </View>

      {/* VS Code toggle */}
      <View style={styles.toggleRow}>
        <Text style={styles.toggleLabel}>⌨️  Abrir VS Code ao finalizar</Text>
        <Switch
          value={openVscode}
          onValueChange={setOpenVscode}
          trackColor={{ false: C.surface700, true: C.brand600 }}
          thumbColor="#fff"
        />
      </View>

      {/* Loading */}
      {isLoading && (
        <View style={styles.loadingBox}>
          <View style={styles.progressRow}>
            <View style={styles.progressTrack}>
              <View style={[styles.progressFill, { width: `${progress}%` as `${number}%` }]} />
            </View>
            <Text style={styles.progressPct}>{Math.round(progress)}%</Text>
          </View>
          {LOADING_STEPS.map((step, i) => (
            <View key={i} style={styles.stepRow}>
              <Text style={styles.stepIcon}>
                {i < currentStep ? "✓" : i === currentStep ? "⏳" : "○"}
              </Text>
              <Text
                style={[
                  styles.stepTxt,
                  i < currentStep && styles.stepDone,
                  i === currentStep && styles.stepActive,
                ]}
              >
                {step}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* Erro */}
      {appState === "error" && (
        <View style={styles.errorBox}>
          <Text style={styles.errorTxt}>{error}</Text>
          <TouchableOpacity onPress={() => setAppState("idle")}>
            <Text style={styles.retryTxt}>Tentar novamente</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Botão */}
      <TouchableOpacity
        style={[styles.submitBtn, isLoading && styles.submitDisabled]}
        onPress={submit}
        disabled={isLoading}
      >
        <Text style={styles.submitTxt}>
          {isLoading ? "Gerando projeto..." : "Gerar Projeto"}
        </Text>
      </TouchableOpacity>

      <View style={{ height: 32 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.bg },
  content: { padding: 20, gap: 16 },

  header: { alignItems: "center", paddingVertical: 8 },
  title: { fontSize: 26, fontWeight: "800", color: C.textPrimary, letterSpacing: -0.5 },
  subtitle: { fontSize: 13, color: C.brand400, opacity: 0.7, marginTop: 4 },

  modeRow: {
    flexDirection: "row",
    borderRadius: 14,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: C.surface700,
  },
  modeBtn: {
    flex: 1,
    paddingVertical: 12,
    alignItems: "center",
    backgroundColor: C.surface800,
  },
  modeBtnActive: { backgroundColor: C.brand600 },
  modeTxt: { fontSize: 14, fontWeight: "600", color: C.textMuted },
  modeTxtActive: { color: "#fff" },

  textArea: {
    backgroundColor: C.surface800,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: C.surface700,
    padding: 14,
    fontSize: 14,
    color: C.textPrimary,
    minHeight: 120,
  },

  section: { gap: 8 },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  label: { fontSize: 13, fontWeight: "600", color: C.textSecondary },
  addBtn: { fontSize: 13, color: C.brand400, fontWeight: "600" },

  input: {
    backgroundColor: C.surface800,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: C.surface700,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    color: C.textPrimary,
  },
  urlRow: { flexDirection: "row", alignItems: "center", gap: 8 },
  removeBtn: { padding: 8 },
  removeTxt: { color: C.textMuted, fontSize: 16 },

  imagePickerBtn: {
    backgroundColor: C.surface800,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: C.surface700,
    paddingVertical: 14,
    alignItems: "center",
  },
  imagePickerTxt: { color: C.textSecondary, fontSize: 14 },
  imageChips: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginTop: 4 },
  chip: {
    backgroundColor: C.surface700,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
    maxWidth: 150,
  },
  chipTxt: { color: C.textSecondary, fontSize: 11 },

  toggleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: C.surface800,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: C.surface700,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  toggleLabel: { fontSize: 13, color: C.textSecondary },

  loadingBox: {
    backgroundColor: C.surface800,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: C.surface700,
    padding: 16,
    gap: 10,
  },
  progressRow: { flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 4 },
  progressTrack: {
    flex: 1,
    height: 6,
    backgroundColor: C.surface700,
    borderRadius: 3,
    overflow: "hidden",
  },
  progressFill: {
    height: 6,
    backgroundColor: C.brand400,
    borderRadius: 3,
  },
  progressPct: { fontSize: 12, fontWeight: "700", color: C.brand400, width: 36, textAlign: "right" },
  stepRow: { flexDirection: "row", alignItems: "center", gap: 10 },
  stepIcon: { fontSize: 14, width: 20, textAlign: "center" },
  stepTxt: { fontSize: 13, color: C.textMuted, flex: 1 },
  stepDone: { color: "#22c55e" },
  stepActive: { color: C.brand300 },

  errorBox: {
    backgroundColor: "#2d0a0a",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#7f1d1d",
    padding: 14,
    gap: 6,
  },
  errorTxt: { color: "#fca5a5", fontSize: 13 },
  retryTxt: { color: "#f87171", fontSize: 12, textDecorationLine: "underline" },

  submitBtn: {
    backgroundColor: C.brand600,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 4,
  },
  submitDisabled: { backgroundColor: C.surface700 },
  submitTxt: { color: "#fff", fontWeight: "700", fontSize: 15 },
});
