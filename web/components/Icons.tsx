type IconProps = { className?: string; size?: number };

function Icon({
  d,
  size = 20,
  className = "",
}: { d: string | string[] } & IconProps) {
  const paths = Array.isArray(d) ? d : [d];
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden="true"
    >
      {paths.map((p, i) => (
        <path key={i} d={p} />
      ))}
    </svg>
  );
}

/* ── Formulário ─────────────────────────────────────────────────── */

export const MicIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15c-.08-.49-.49-.85-.98-.85-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08c3.02-.43 5.42-2.78 5.91-5.78.1-.6-.39-1.14-1-1.14z"
  />
);

export const EditIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
  />
);

export const MusicNoteIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"
  />
);

export const LinkIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"
  />
);

export const PhotoIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"
  />
);

export const CodeIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"
  />
);

export const AddIcon = (p: IconProps) => (
  <Icon {...p} d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
);

export const CloseIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
  />
);

export const CheckCircleIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
  />
);

export const RadioUncheckIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"
  />
);

/* ── Resultado ──────────────────────────────────────────────────── */

export const RocketIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M9.19 6.35c-2.04 2.29-3.44 5.58-3.57 5.89L2 10.69l4.09-4.09c.47-.47 1.15-.64 1.79-.45l1.31.2zM11.17 18c-.01.01-3.7 1.66-3.7 1.66l4.09-4.09c.44.03.87.13 1.27.3l-.13-.13.47 2.26zM21.99 2.01L22 2s-5.83.6-11.6 6.38L8.7 8.35c.38-.38.77-.55 1.35-.4l6.01 6.01c.15.59-.03.97-.41 1.35l-.03.03 1.97-1.7C23.36 7.87 21.99 2.01 21.99 2.01zm-8.95 8.12l-3.16-3.16C13.93 3.93 17.76 2.6 20.22 2c-.6 2.46-1.93 6.29-5.18 9.53l-2-1.4z"
  />
);

export const CalendarIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13z"
  />
);

export const PaymentsIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"
  />
);

export const BotIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zM7.5 11.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5S9.83 13 9 13s-1.5-.67-1.5-1.5zM16 17H8v-2h8v2zm-1-4c-.83 0-1.5-.67-1.5-1.5S14.17 10 15 10s1.5.67 1.5 1.5S15.83 13 15 13z"
  />
);

export const VerifiedIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M23 12l-2.44-2.79.34-3.69-3.61-.82-1.89-3.2L12 2.96 8.6 1.5 6.71 4.69 3.1 5.5l.34 3.7L1 12l2.44 2.79-.34 3.7 3.61.82 1.89 3.2L12 21.04l3.4 1.46 1.89-3.2 3.61-.82-.34-3.69L23 12zm-12.91 4.72l-3.8-3.81 1.48-1.48 2.32 2.33 5.85-5.87 1.48 1.48-7.33 7.35z"
  />
);

export const CreditCardIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"
  />
);

export const ChevronRightIcon = (p: IconProps) => (
  <Icon {...p} d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" />
);

export const FolderIcon = (p: IconProps) => (
  <Icon
    {...p}
    d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"
  />
);
