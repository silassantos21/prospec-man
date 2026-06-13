import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from "react-native";
import { C } from "../constants";

type TechCat = { primary: string };
type Plan = {
  project_type: string;
  key_features: string[];
  tech_stack: Record<string, TechCat | null>;
  ai_agents: { name: string; role: string }[];
};
type Result = {
  project_name: string;
  project_path: string;
  plan: Plan;
  timeline_days: number;
  cost_monthly_brl: number;
  free_tier_viable: boolean;
};

const STACK_LABELS: Record<string, string> = {
  frontend: "Frontend", backend: "Backend", database: "Banco",
  auth: "Auth", cache: "Cache", infrastructure: "Infra",
  monitoring: "Monitor", ai_ml: "IA / ML",
};

interface Props {
  result: Record<string, unknown>;
  onNew: () => void;
}

export default function ResultScreen({ result, onNew }: Props) {
  const r = result as unknown as Result;
  const plan = r.plan;
  const stackEntries = Object.entries(plan.tech_stack).filter(([, v]) => v != null) as [string, TechCat][];

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      {/* Header sucesso */}
      <View style={styles.header}>
        <View style={styles.successBadge}>
          <Text style={styles.successBadgeTxt}>🚀  Projeto criado com sucesso</Text>
        </View>
        <Text style={styles.projectName}>{r.project_name}</Text>
        <Text style={styles.projectType}>
          {plan.project_type.replace(/_/g, " ")}
        </Text>
      </View>

      {/* Stats */}
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={[styles.statIcon, { color: C.brand400 }]}>📅</Text>
          <Text style={[styles.statValue, { color: C.brand400 }]}>{r.timeline_days}</Text>
          <Text style={styles.statLabel}>dias estimados</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statIcon, { color: "#22c55e" }]}>💳</Text>
          <Text style={[styles.statValue, { color: "#22c55e" }]}>
            R$ {r.cost_monthly_brl.toFixed(0)}
          </Text>
          <Text style={styles.statLabel}>/ mês estimado</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statIcon, { color: C.purple }]}>🤖</Text>
          <Text style={[styles.statValue, { color: C.purple }]}>{plan.ai_agents.length}</Text>
          <Text style={styles.statLabel}>agentes de IA</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statIcon}>{r.free_tier_viable ? "✅" : "💰"}</Text>
          <Text style={[styles.statValue, { color: r.free_tier_viable ? "#22c55e" : C.amber, fontSize: 14, marginTop: 4 }]}>
            {r.free_tier_viable ? "Free tier" : "Plano pago"}
          </Text>
          <Text style={styles.statLabel}>{r.free_tier_viable ? "viável" : "necessário"}</Text>
        </View>
      </View>

      {/* Features */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Funcionalidades principais</Text>
        {plan.key_features.slice(0, 5).map((f, i) => (
          <View key={i} style={styles.featureRow}>
            <Text style={styles.featureDot}>›</Text>
            <Text style={styles.featureTxt}>{f}</Text>
          </View>
        ))}
      </View>

      {/* Stack */}
      {stackEntries.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Stack tecnológica</Text>
          {stackEntries.map(([key, cat]) => (
            <View key={key} style={styles.stackRow}>
              <Text style={styles.stackKey}>{STACK_LABELS[key] ?? key}</Text>
              <View style={styles.stackBadge}>
                <Text style={styles.stackValue} numberOfLines={1}>{cat.primary}</Text>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Path */}
      <View style={styles.pathCard}>
        <Text style={styles.pathLabel}>📁  Projeto criado em:</Text>
        <Text style={styles.pathValue}>{r.project_path}</Text>
      </View>

      {/* Novo projeto */}
      <TouchableOpacity style={styles.newBtn} onPress={onNew}>
        <Text style={styles.newBtnTxt}>+ Novo Projeto</Text>
      </TouchableOpacity>

      <View style={{ height: 32 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: C.bg },
  content: { padding: 20, gap: 16 },

  header: { alignItems: "center", paddingVertical: 8, gap: 8 },
  successBadge: {
    backgroundColor: "#052010",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#14532d",
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  successBadgeTxt: { color: "#22c55e", fontSize: 12, fontWeight: "600" },
  projectName: { fontSize: 22, fontWeight: "800", color: C.textPrimary, textAlign: "center" },
  projectType: { fontSize: 13, color: C.textMuted, textTransform: "capitalize" },

  statsGrid: { flexDirection: "row", flexWrap: "wrap", gap: 12 },
  statCard: {
    flex: 1,
    minWidth: "44%",
    backgroundColor: C.surface800,
    borderRadius: 14,
    padding: 14,
    alignItems: "center",
    gap: 2,
  },
  statIcon: { fontSize: 20 },
  statValue: { fontSize: 22, fontWeight: "800", marginTop: 4 },
  statLabel: { fontSize: 11, color: C.textMuted, marginTop: 2 },

  card: {
    backgroundColor: C.surface800,
    borderRadius: 14,
    padding: 16,
    gap: 8,
  },
  cardTitle: { fontSize: 13, fontWeight: "700", color: C.textSecondary, marginBottom: 4 },

  featureRow: { flexDirection: "row", gap: 8, alignItems: "flex-start" },
  featureDot: { color: C.brand500, fontSize: 16, lineHeight: 20 },
  featureTxt: { color: C.textSecondary, fontSize: 13, flex: 1, lineHeight: 20 },

  stackRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  stackKey: { color: C.textMuted, fontSize: 12 },
  stackBadge: {
    backgroundColor: C.surface700,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
    maxWidth: 200,
  },
  stackValue: { color: C.textPrimary, fontSize: 11, fontFamily: "monospace" },

  pathCard: {
    backgroundColor: C.surface800,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: C.surface700,
    padding: 14,
    gap: 6,
  },
  pathLabel: { fontSize: 12, color: C.textMuted },
  pathValue: { fontSize: 11, color: C.brand400, fontFamily: "monospace" },

  newBtn: {
    backgroundColor: C.brand600,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 4,
  },
  newBtnTxt: { color: "#fff", fontWeight: "700", fontSize: 15 },
});
