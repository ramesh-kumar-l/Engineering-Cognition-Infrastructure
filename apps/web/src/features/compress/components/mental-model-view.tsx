import type { MentalModel } from "@/types/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type Dict = Record<string, unknown>;

function pick(d: Dict, keys: string[]): string | undefined {
  for (const k of keys) {
    const v = d[k];
    if (typeof v === "string" && v.trim()) return v;
  }
  return undefined;
}

function entityLabel(e: Dict): string {
  const name = pick(e, ["name", "label", "title", "id"]);
  const type = pick(e, ["type", "kind", "category"]);
  if (name && type) return `${name} · ${type}`;
  return name ?? type ?? JSON.stringify(e);
}

function relationLabel(r: Dict): string {
  const from = pick(r, ["source", "from", "subject", "head"]);
  const rel = pick(r, ["type", "predicate", "relation", "label"]);
  const to = pick(r, ["target", "to", "object", "tail"]);
  if (from && to) return `${from} → ${rel ?? "related to"} → ${to}`;
  return JSON.stringify(r);
}

/** Renders the structured mental model: claims, entities, relationships. */
export function MentalModelView({ model }: { model: MentalModel }) {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between gap-3">
        <CardTitle>Mental model</CardTitle>
        <Badge tone="neutral" className="font-mono">
          {model.model_used}
        </Badge>
      </CardHeader>
      <CardBody className="space-y-5 text-sm">
        <Section title={`Claims (${model.claims.length})`}>
          {model.claims.length ? (
            <ul className="list-disc space-y-1 pl-5 text-zinc-300">
              {model.claims.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          ) : (
            <Empty />
          )}
        </Section>

        <Section title={`Entities (${model.entities.length})`}>
          {model.entities.length ? (
            <div className="flex flex-wrap gap-2">
              {model.entities.map((e, i) => (
                <Badge key={i} tone="info">
                  {entityLabel(e)}
                </Badge>
              ))}
            </div>
          ) : (
            <Empty />
          )}
        </Section>

        <Section title={`Relationships (${model.relationships.length})`}>
          {model.relationships.length ? (
            <ul className="space-y-1 font-mono text-xs text-zinc-300">
              {model.relationships.map((r, i) => (
                <li key={i}>{relationLabel(r)}</li>
              ))}
            </ul>
          ) : (
            <Empty />
          )}
        </Section>
      </CardBody>
    </Card>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-zinc-500">{title}</h4>
      {children}
    </div>
  );
}

function Empty() {
  return <p className="text-zinc-500">None extracted.</p>;
}
