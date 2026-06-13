import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Permite acesso pelo celular via Wi-Fi/hotspot no modo dev
  allowedDevOrigins: [
    "192.168.0.39",
    "192.168.0.39:3000",
    "192.168.43.1",
    "172.20.10.1",
  ],
  // Fixa o root do Turbopack para evitar warning de workspace detection
  turbopack: {
    root: import.meta.dirname,
  },
};

export default nextConfig;
