import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import type { EvidenceInput } from "@/types/api";

const SOURCE_TYPES = ["goal", "task", "memory_entry"] as const;

const EMPTY: EvidenceInput = { source_type: "goal", source_id: "", summary: "" };

/** Controlled add/remove editor for the evidence backing a lesson (source + summary). */
export function EvidenceEditor({
  value,
  onChange,
}: {
  value: EvidenceInput[];
  onChange: (next: EvidenceInput[]) => void;
}) {
  function update(i: number, patch: Partial<EvidenceInput>) {
    onChange(value.map((row, idx) => (idx === i ? { ...row, ...patch } : row)));
  }

  return (
    <div className="space-y-2">
      {value.map((row, i) => (
        <div key={i} className="space-y-1.5 rounded-md border border-zinc-800 p-2">
          <div className="flex gap-2">
            <Select
              value={row.source_type}
              onChange={(e) => update(i, { source_type: e.target.value })}
              className="py-1 text-xs"
              aria-label="Evidence source type"
            >
              {SOURCE_TYPES.map((s) => (
                <option key={s} value={s}>
                  {s.replace("_", " ")}
                </option>
              ))}
            </Select>
            <Input
              value={row.source_id}
              onChange={(e) => update(i, { source_id: e.target.value })}
              placeholder="Source ID (UUID)"
              className="font-mono text-xs"
            />
            <Button
              type="button"
              variant="ghost"
              className="px-2 py-1 text-xs"
              onClick={() => onChange(value.filter((_, idx) => idx !== i))}
              aria-label="Remove evidence"
            >
              ✕
            </Button>
          </div>
          <Input
            value={row.summary}
            onChange={(e) => update(i, { summary: e.target.value })}
            placeholder="What this proves"
            className="text-xs"
          />
        </div>
      ))}
      <Button
        type="button"
        variant="outline"
        className="px-2 py-1 text-xs"
        onClick={() => onChange([...value, { ...EMPTY }])}
      >
        + Evidence
      </Button>
    </div>
  );
}
