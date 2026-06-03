import type { ReactNode } from "react";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface Props {
  kindLabel: string;
  id: string;
  contentHash: string;
  source: string;
  deduplicated: boolean;
  ingestedAt: string;
  /** Optional next-step action (e.g. "Compress →"). */
  action?: ReactNode;
}

/** Confirmation card shown after a successful ingest, with provenance + next step. */
export function IngestResult({
  kindLabel,
  id,
  contentHash,
  source,
  deduplicated,
  ingestedAt,
  action,
}: Props) {
  return (
    <Card className="border-emerald-900/60">
      <CardHeader className="flex items-center justify-between gap-3">
        <CardTitle>{kindLabel} ingested</CardTitle>
        {deduplicated ? (
          <Badge tone="warn">Deduplicated — identical content already stored</Badge>
        ) : (
          <Badge tone="good">Created</Badge>
        )}
      </CardHeader>
      <CardBody className="space-y-2 text-sm">
        <Field label="ID" value={id} mono />
        <Field label="Content hash" value={contentHash} mono />
        <Field label="Source" value={source} />
        <Field label="Ingested at" value={new Date(ingestedAt).toLocaleString()} />
        {action && <div className="pt-1">{action}</div>}
      </CardBody>
    </Card>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex gap-3">
      <span className="w-28 shrink-0 text-zinc-500">{label}</span>
      <span className={mono ? "break-all font-mono text-xs text-zinc-300" : "text-zinc-200"}>
        {value}
      </span>
    </div>
  );
}
