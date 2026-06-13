import ProspecForm from "@/components/ProspecForm";

export default function Home() {
  return (
    <main className="min-h-screen bg-surface-950">
      <div className="max-w-lg mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <img
            src="/logo-dark.svg"
            alt="ProspecMan"
            className="w-36 h-36 mx-auto"
            loading="eager"
          />
          <p className="text-sm text-brand-400/60 mt-1">
            Briefing de áudio → projeto documentado com IA
          </p>
        </div>
        <ProspecForm />
      </div>
    </main>
  );
}
