import { useState, type FormEvent } from "react";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Field } from "@/components/ui/field";
import { ApiError } from "@/lib/api-client";
import { cn } from "@/lib/cn";
import { REFLECTION_CADENCES } from "@/types/api";
import { useCreateRetrospective, useRetrospectives } from "../use-reflection";

/** Left column: run a retrospective and pick one to scope the lessons column. */
export function RetrospectivePanel({
  selectedId,
  onSelect,
}: {
  selectedId: string | undefined;
  onSelect: (id: string | undefined) => void;
}) {
  const retros = useRetrospectives();
  const create = useCreateRetrospective();
  const [cadence, setCadence] = useState("weekly");
  const [notes, setNotes] = useState("");

  function onRun(e: FormEvent) {
    e.preventDefault();
    create.mutate(
      { cadence, notes: notes.trim() || undefined },
      {
        onSuccess: (r) => {
          setNotes("");
          onSelect(r.id);
        },
      },
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Retrospectives</CardTitle>
      </CardHeader>
      <CardBody className="space-y-3">
        <form onSubmit={onRun} className="space-y-2.5 rounded-md border border-zinc-800 p-3">
          <Field label="Cadence">
            <Select value={cadence} onChange={(e) => setCadence(e.target.value)} className="py-1.5 text-sm">
              {REFLECTION_CADENCES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Notes" hint="Optional framing for this cycle.">
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="What prompted this reflection?"
              className="min-h-16 text-sm"
            />
          </Field>
          {create.error instanceof ApiError && (
            <p className="text-xs text-red-300">{create.error.detail}</p>
          )}
          <Button type="submit" disabled={create.isPending}>
            {create.isPending ? "Running…" : "Run retrospective"}
          </Button>
        </form>

        {retros.isLoading ? (
          <p className="text-sm text-zinc-400">Loading…</p>
        ) : retros.error ? (
          <p className="text-sm text-red-300">
            {retros.error instanceof ApiError ? retros.error.detail : "Failed to load retrospectives."}
          </p>
        ) : retros.data && retros.data.length > 0 ? (
          <ul className="space-y-1">
            <li>
              <button
                onClick={() => onSelect(undefined)}
                className={cn(
                  "w-full rounded-md px-3 py-2 text-left text-sm transition",
                  selectedId === undefined
                    ? "bg-zinc-800/70 text-zinc-100"
                    : "text-zinc-300 hover:bg-zinc-800/40",
                )}
              >
                All lessons
              </button>
            </li>
            {retros.data.map((r) => (
              <li key={r.id}>
                <button
                  onClick={() => onSelect(r.id)}
                  className={cn(
                    "w-full rounded-md px-3 py-2 text-left transition",
                    r.id === selectedId
                      ? "bg-zinc-800/70 text-zinc-100"
                      : "text-zinc-300 hover:bg-zinc-800/40",
                  )}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium capitalize">{r.cadence}</span>
                    <div className="flex items-center gap-1.5">
                      <Badge tone={r.status === "completed" ? "good" : "info"}>{r.status}</Badge>
                      <Badge tone="neutral">{r.lesson_count} lessons</Badge>
                    </div>
                  </div>
                  {r.notes && (
                    <span className="mt-1 block truncate text-xs text-zinc-500">{r.notes}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-500">No retrospectives yet. Run one to extract lessons.</p>
        )}
      </CardBody>
    </Card>
  );
}
