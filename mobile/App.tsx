import { useState } from "react";
import { StyleSheet } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import FormScreen from "./screens/FormScreen";
import ResultScreen from "./screens/ResultScreen";
import HistoryScreen from "./screens/HistoryScreen";
import { C } from "./constants";
import { saveProject } from "./utils/storage";

type Screen = "form" | "result" | "history";

export default function App() {
  const [screen, setScreen] = useState<Screen>("form");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [fromHistory, setFromHistory] = useState(false);

  const handleResult = async (data: Record<string, unknown>) => {
    await saveProject(data);
    setResult(data);
    setFromHistory(false);
    setScreen("result");
  };

  const handleOpenFromHistory = (data: Record<string, unknown>) => {
    setResult(data);
    setFromHistory(true);
    setScreen("result");
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" backgroundColor={C.bg} />
        {screen === "form" && (
          <FormScreen
            onResult={handleResult}
            onHistory={() => setScreen("history")}
          />
        )}
        {screen === "result" && (
          <ResultScreen
            result={result!}
            onNew={() => { setResult(null); setScreen("form"); }}
            onHistory={() => setScreen("history")}
            showBack={fromHistory}
            onBack={() => setScreen("history")}
          />
        )}
        {screen === "history" && (
          <HistoryScreen
            onBack={() => setScreen("form")}
            onOpen={handleOpenFromHistory}
          />
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: C.bg },
});
