import { useState } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { useAudioRecorder, useAudioRecorderState, AudioModule, RecordingPresets } from "expo-audio";
import * as DocumentPicker from "expo-document-picker";
import * as Sharing from "expo-sharing";
import { C } from "../constants";

interface Props {
  recordedUri: string | null;
  onRecorded: (uri: string) => void;
  onClear: () => void;
}

export default function AudioRecorder({ recordedUri, onRecorded, onClear }: Props) {
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const state = useAudioRecorderState(recorder);
  const [finalSeconds, setFinalSeconds] = useState(0);

  const seconds = Math.floor((state.durationMillis ?? 0) / 1000);

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  const start = async () => {
    const { granted } = await AudioModule.requestRecordingPermissionsAsync();
    if (!granted) {
      Alert.alert("Permissão negada", "Habilite o microfone nas configurações do celular.");
      return;
    }
    await recorder.prepareToRecordAsync();
    recorder.record();
  };

  const stop = async () => {
    setFinalSeconds(seconds);
    await recorder.stop();
    if (recorder.uri) onRecorded(recorder.uri);
  };

  const pickAudio = async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: "audio/*" });
    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];
      setFinalSeconds(0);
      onRecorded(asset.uri);
    }
  };

  const shareAudio = async () => {
    if (!recordedUri) return;
    const available = await Sharing.isAvailableAsync();
    if (!available) { Alert.alert("Compartilhamento não disponível neste dispositivo."); return; }
    await Sharing.shareAsync(recordedUri, { mimeType: "audio/m4a", dialogTitle: "Salvar ou compartilhar áudio" });
  };

  if (recordedUri) {
    return (
      <View style={styles.doneBox}>
        <Text style={styles.doneIcon}>🎵</Text>
        <View style={styles.doneText}>
          <Text style={styles.doneLabel}>Áudio gravado</Text>
          <Text style={styles.doneSub}>{formatTime(finalSeconds)} · pronto para enviar</Text>
        </View>
        <TouchableOpacity onPress={shareAudio} style={styles.shareBtn}>
          <Text style={styles.shareText}>⬇</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={onClear} style={styles.clearBtn}>
          <Text style={styles.clearText}>✕</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.recorderBox}>
      {state.isRecording ? (
        <>
          <View style={styles.pulseRing} />
          <Text style={styles.timerText}>{formatTime(seconds)}</Text>
          <Text style={styles.recLabel}>Gravando...</Text>
          <TouchableOpacity style={styles.stopBtn} onPress={stop}>
            <Text style={styles.stopText}>⏹ Parar</Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Text style={styles.micIcon}>🎙️</Text>
          <Text style={styles.hint}>Toque para gravar o briefing</Text>
          <TouchableOpacity style={styles.startBtn} onPress={start}>
            <Text style={styles.startText}>● Gravar</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.pickBtn} onPress={pickAudio}>
            <Text style={styles.pickText}>📎  Anexar arquivo de áudio</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  recorderBox: {
    backgroundColor: C.surface800,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: C.surface600,
    borderStyle: "dashed",
    paddingVertical: 28,
    alignItems: "center",
    gap: 10,
  },
  micIcon: { fontSize: 36 },
  hint: { color: C.textMuted, fontSize: 14 },
  startBtn: {
    backgroundColor: C.brand600,
    paddingHorizontal: 28,
    paddingVertical: 10,
    borderRadius: 20,
    marginTop: 4,
  },
  startText: { color: "#fff", fontWeight: "600", fontSize: 15 },
  pulseRing: {
    width: 56,
    height: 56,
    borderRadius: 28,
    borderWidth: 3,
    borderColor: C.brand400,
    opacity: 0.5,
  },
  timerText: { fontSize: 28, fontWeight: "700", color: C.brand400, letterSpacing: 2 },
  recLabel: { color: C.textMuted, fontSize: 13 },
  stopBtn: {
    backgroundColor: C.surface700,
    borderWidth: 1,
    borderColor: C.surface600,
    paddingHorizontal: 28,
    paddingVertical: 10,
    borderRadius: 20,
    marginTop: 4,
  },
  stopText: { color: C.textPrimary, fontWeight: "600", fontSize: 15 },
  pickBtn: {
    borderWidth: 1,
    borderColor: C.surface600,
    paddingHorizontal: 24,
    paddingVertical: 8,
    borderRadius: 20,
  },
  pickText: { color: C.textMuted, fontSize: 13 },
  doneBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: C.surface800,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: C.brand600,
    padding: 16,
    gap: 12,
  },
  doneIcon: { fontSize: 28 },
  doneText: { flex: 1 },
  doneLabel: { color: C.brand400, fontWeight: "600", fontSize: 14 },
  doneSub: { color: C.textMuted, fontSize: 12, marginTop: 2 },
  shareBtn: { padding: 4, marginRight: 4 },
  shareText: { color: C.brand400, fontSize: 18 },
  clearBtn: { padding: 4 },
  clearText: { color: C.textMuted, fontSize: 18 },
});
