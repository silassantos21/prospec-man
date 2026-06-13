import { useState } from "react";
import { StyleSheet } from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import FormScreen from "./screens/FormScreen";
import ResultScreen from "./screens/ResultScreen";
import { C } from "./constants";

type Screen = "form" | "result";

export default function App() {
  const [screen, setScreen] = useState<Screen>("form");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const handleResult = (data: Record<string, unknown>) => {
    setResult(data);
    setScreen("result");
  };

  const handleNew = () => {
    setResult(null);
    setScreen("form");
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" backgroundColor={C.bg} />
        {screen === "form" ? (
          <FormScreen onResult={handleResult} />
        ) : (
          <ResultScreen result={result!} onNew={handleNew} />
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: C.bg,
  },
});
