"use client";

import {
  RocketIcon, CalendarIcon, PaymentsIcon, BotIcon,
  VerifiedIcon, CreditCardIcon, ChevronRightIcon, FolderIcon, AddIcon,
} from "./Icons";

type TechCat = { primary: string };
type TechStack = Record<string, TechCat | null>;
type AIAgent = { name: string; role: string };

type Plan = {
  project_type: string;
  key_features: string[];
  tech_stack: TechStack;
  ai_agents: AIAgent[];
  timeline: { total_weeks: number };
};

type Result = {
  project_name: string;
  project_path: string;
  plan: Plan;
  timeline_days: number;
  cost_monthly_brl: number;
  free_tier_viable: boolean;
};

type Props = { result: Record<string, unknown>; onNew: () => void };

const STACK_LABELS: Record<string, string> = {
  frontend: "Frontend",
  backend: "Backend",
  database: "Banco",
  auth: "Auth",
  cache: "Cache",
  infrastructure: "Infra",
  monitoring: "Monitor",
  ai_ml: "IA / ML",
};

export default function ProjectResult({ result, onNew }: Props) {
  const r = result as unknown as Result;
  const plan = r.plan;

  const stackEntries = Object.entries(plan.tech_stack).filter(
    ([, v]) => v != null
  ) as [string, TechCat][];

  return (
    <div className="space-y-4">
      {/* Header de sucesso */}
      <div className="text-center py-2">
        <div className="flex justify-center mb-3">
          <img src="/logo-dark.svg" alt="ProspecMan" className="w-20 h-20" />
        </div>
        <div className="inline-flex items-center gap-2 bg-green-950/60 border border-green-800/50 rounded-full px-3 py-1 mb-3">
          <RocketIcon size={14} className="text-green-400" />
          <span className="text-xs text-green-400 font-medium">Projeto criado com sucesso</span>
        </div>
        <h2 className="text-xl font-bold text-white">{r.project_name}</h2>
        <p className="text-sm text-zinc-500 mt-1 capitalize">
          {plan.project_type.replace(/_/g, " ")}
        </p>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-surface-800 rounded-xl p-4 text-center">
          <CalendarIcon size={20} className="text-brand-400 mx-auto mb-1" />
          <div className="text-2xl font-bold text-brand-400">{r.timeline_days}</div>
          <div className="text-xs text-zinc-500 mt-0.5">dias estimados</div>
        </div>
        <div className="bg-surface-800 rounded-xl p-4 text-center">
          <PaymentsIcon size={20} className="text-green-400 mx-auto mb-1" />
          <div className="text-2xl font-bold text-green-400">
            R$ {r.cost_monthly_brl.toFixed(0)}
          </div>
          <div className="text-xs text-zinc-500 mt-0.5">/ mês estimado</div>
        </div>
        <div className="bg-surface-800 rounded-xl p-4 text-center">
          <BotIcon size={20} className="text-purple-400 mx-auto mb-1" />
          <div className="text-2xl font-bold text-purple-400">
            {plan.ai_agents.length}
          </div>
          <div className="text-xs text-zinc-500 mt-0.5">agentes de IA</div>
        </div>
        <div className="bg-surface-800 rounded-xl p-4 text-center">
          {r.free_tier_viable ? (
            <VerifiedIcon size={20} className="text-green-400 mx-auto mb-1" />
          ) : (
            <CreditCardIcon size={20} className="text-amber-400 mx-auto mb-1" />
          )}
          <div className={`text-sm font-semibold mt-1 ${r.free_tier_viable ? "text-green-400" : "text-amber-400"}`}>
            {r.free_tier_viable ? "Free tier" : "Plano pago"}
          </div>
          <div className="text-xs text-zinc-500 mt-0.5">
            {r.free_tier_viable ? "viável" : "necessário"}
          </div>
        </div>
      </div>

      {/* Funcionalidades */}
      <div className="bg-surface-800 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-zinc-300 mb-3">
          Funcionalidades principais
        </h3>
        <ul className="space-y-1.5">
          {plan.key_features.slice(0, 5).map((f, i) => (
            <li key={i} className="text-sm text-zinc-400 flex gap-2 items-start">
              <ChevronRightIcon size={16} className="text-brand-500 mt-0.5 shrink-0" />
              {f}
            </li>
          ))}
        </ul>
      </div>

      {/* Stack */}
      {stackEntries.length > 0 && (
        <div className="bg-surface-800 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-zinc-300 mb-3">
            Stack tecnológica
          </h3>
          <div className="space-y-2">
            {stackEntries.map(([key, cat]) => (
              <div key={key} className="flex justify-between items-center text-sm">
                <span className="text-zinc-500">
                  {STACK_LABELS[key] ?? key}
                </span>
                <span className="text-zinc-200 font-mono text-xs bg-surface-700 rounded px-2 py-0.5">
                  {cat.primary}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Caminho do projeto */}
      <div className="bg-surface-800/50 border border-surface-700 rounded-xl p-4">
        <p className="text-xs text-zinc-500 mb-1 inline-flex items-center gap-1.5">
          <FolderIcon size={13} /> Projeto criado em:
        </p>
        <p className="text-xs text-brand-400 font-mono break-all mt-1">
          {r.project_path}
        </p>
      </div>

      {/* Novo projeto */}
      <button
        onClick={onNew}
        className="w-full py-4 bg-brand-600 hover:bg-brand-500 text-white font-semibold rounded-xl transition-colors text-sm inline-flex items-center justify-center gap-2"
      >
        <AddIcon size={18} /> Novo Projeto
      </button>
    </div>
  );
}
