import AsyncStorage from "@react-native-async-storage/async-storage";

const EMAIL_KEY = "@prospecman/email";
const HISTORY_KEY = "@prospecman/history";
const MAX_HISTORY = 20;

export interface HistoryEntry {
  id: string;
  savedAt: string;
  projectName: string;
  projectType: string;
  data: Record<string, unknown>;
}

export async function saveEmail(email: string): Promise<void> {
  await AsyncStorage.setItem(EMAIL_KEY, email);
}

export async function loadEmail(): Promise<string> {
  return (await AsyncStorage.getItem(EMAIL_KEY)) ?? "";
}

export async function saveProject(data: Record<string, unknown>): Promise<void> {
  const history = await loadProjects();
  const entry: HistoryEntry = {
    id: Date.now().toString(),
    savedAt: new Date().toISOString(),
    projectName: (data.project_name as string) ?? "Projeto",
    projectType: (data.project_type as string) ?? "",
    data,
  };
  const updated = [entry, ...history].slice(0, MAX_HISTORY);
  await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
}

export async function loadProjects(): Promise<HistoryEntry[]> {
  const raw = await AsyncStorage.getItem(HISTORY_KEY);
  if (!raw) return [];
  try { return JSON.parse(raw); } catch { return []; }
}

export async function deleteProject(id: string): Promise<void> {
  const history = await loadProjects();
  await AsyncStorage.setItem(HISTORY_KEY, JSON.stringify(history.filter((e) => e.id !== id)));
}
