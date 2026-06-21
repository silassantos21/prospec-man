import { useEffect, useState } from "react";
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { C } from "../constants";
import { loadProjects, deleteProject, HistoryEntry } from "../utils/storage";

const TYPE_LABELS: Record<string, string> = {
  landing_page: "Landing Page", fullstack_web: "Full Stack Web",
  api_backend: "API Backend", mobile_app: "App Mobile",
  crm_erp: "CRM / ERP", ecommerce: "E-commerce",
  saas: "SaaS", data_pipeline: "Data Pipeline", chatbot: "Chatbot",
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" });
}

interface Props {
  onBack: () => void;
  onOpen: (data: Record<string, unknown>) => void;
}

export default function HistoryScreen({ onBack, onOpen }: Props) {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    loadProjects().then(setEntries);
  }, []);

  const handleDelete = (entry: HistoryEntry) => {
    Alert.alert("Remover projeto", `Remover "${entry.projectName}" do histórico?`, [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Remover", style: "destructive",
        onPress: async () => {
          await deleteProject(entry.id);
          setEntries((prev) => prev.filter((e) => e.id !== entry.id));
        },
      },
    ]);
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backBtn}>
          <Text style={styles.backTxt}>← Voltar</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Histórico</Text>
        <View style={{ width: 64 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {entries.length === 0 ? (
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>📋</Text>
            <Text style={styles.emptyTxt}>Nenhum projeto gerado ainda.</Text>
            <Text style={styles.emptySubtxt}>Seus projetos aparecerão aqui após a geração.</Text>
          </View>
        ) : (
          entries.map((entry) => (
            <TouchableOpacity key={entry.id} style={styles.card} onPress={() => onOpen(entry.data)}>
              <View style={styles.cardTop}>
                <Text style={styles.cardName} numberOfLines={1}>{entry.projectName}</Text>
                <TouchableOpacity onPress={() => handleDelete(entry)} hitSlop={{ top: 8, right: 8, bottom: 8, left: 8 }}>
                  <Text style={styles.deleteBtn}>✕</Text>
                </TouchableOpacity>
              </View>
              <View style={styles.cardBottom}>
                <Text style={styles.cardType}>
                  {TYPE_LABELS[entry.projectType] ?? entry.projectType.replace(/_/g, " ")}
                </Text>
                <Text style={styles.cardDate}>{formatDate(entry.savedAt)}</Text>
              </View>
            </TouchableOpacity>
          ))
        )}
        <View style={{ height: 32 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.bg },

  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: C.surface700,
  },
  backBtn: { width: 64 },
  backTxt: { color: C.brand400, fontSize: 14, fontWeight: "600" },
  title: { fontSize: 16, fontWeight: "700", color: C.textPrimary },

  content: { padding: 16, gap: 12 },

  empty: { alignItems: "center", paddingTop: 80, gap: 12 },
  emptyIcon: { fontSize: 48 },
  emptyTxt: { fontSize: 16, fontWeight: "600", color: C.textSecondary },
  emptySubtxt: { fontSize: 13, color: C.textMuted, textAlign: "center" },

  card: {
    backgroundColor: C.surface800,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: C.surface700,
    padding: 16,
    gap: 8,
  },
  cardTop: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  cardName: { fontSize: 15, fontWeight: "700", color: C.textPrimary, flex: 1, marginRight: 8 },
  deleteBtn: { color: C.textMuted, fontSize: 14 },
  cardBottom: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  cardType: { fontSize: 12, color: C.brand400, textTransform: "capitalize" },
  cardDate: { fontSize: 11, color: C.textMuted },
});
