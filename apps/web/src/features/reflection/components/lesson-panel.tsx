import { useState, type FormEvent } from "react";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { ApiError } from "@/lib/api-client";
import {
  LESSON_CONFIDENCES,
  LESSON_SCOPES,
  type EvidenceInput,
} from "@/types/api";
import { EvidenceEditor } from "./evidence-editor";
import { LessonCard } from "./lesson-card";
import { useCreateLesson, useLessons } from "../use-reflection";

/** Right column: lessons (optionally scoped to a retrospective), with manual capture. */
export function LessonPanel({ retrospectiveId }: { retrospectiveId: string | undefined }) {
  const [statusFilter, setStatusFilter] = useState("");
  const lessons = useLessons({ retrospectiveId, status: statusFilter || undefined });
  const create = useCreateLesson();

  const [claim, setClaim] = useState("");
  const [confidence, setConfidence] = useState("medium");
  const [scope, setScope] = useState("global");
  const [evidence, setEvidence] = useState<EvidenceInput[]>([]);

  function onCreate(e: FormEvent) {
    e.preventDefault();
    const c = claim.trim();
    if (!c) return;
    create.mutate(
      { claim: c, confidence, scope, retrospective_id: retrospectiveId, evidence },
      {
        onSuccess: () => {
          setClaim("");
          setEvidence([]);
        },
      },
    );
  }

  return (
    <Card>
      <CardHeader className="flex items-center justify-between gap-2">
        <CardTitle>Lessons</CardTitle>
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="py-1 text-xs"
          aria-label="Filter by status"
        >
          <option value="">all</option>
          <option value="active">active</option>
          <option value="superseded">superseded</option>
        </Select>
      </CardHeader>
      <CardBody className="space-y-4">
        <form onSubmit={onCreate} className="space-y-2.5 rounded-md border border-zinc-800 p-3">
          <Field label="Claim" hint="A durable lesson worth carrying forward.">
            <Input
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder="e.g. RRF beats neural rerank for our corpus size"
            />
          </Field>
          <div className="grid grid-cols-2 gap-2">
            <Field label="Confidence">
              <Select
                value={confidence}
                onChange={(e) => setConfidence(e.target.value)}
                className="py-1 text-xs"
              >
                {LESSON_CONFIDENCES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Scope">
              <Select
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                className="py-1 text-xs"
              >
                {LESSON_SCOPES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </Select>
            </Field>
          </div>
          <Field label="Evidence" hint="Link the goals, tasks, or memories that justify this.">
            <EvidenceEditor value={evidence} onChange={setEvidence} />
          </Field>
          {create.error instanceof ApiError && (
            <p className="text-xs text-red-300">{create.error.detail}</p>
          )}
          <Button type="submit" disabled={!claim.trim() || create.isPending}>
            Record lesson
          </Button>
        </form>

        {lessons.isLoading ? (
          <p className="text-sm text-zinc-400">Loading…</p>
        ) : lessons.error ? (
          <p className="text-sm text-red-300">
            {lessons.error instanceof ApiError ? lessons.error.detail : "Failed to load lessons."}
          </p>
        ) : lessons.data && lessons.data.length > 0 ? (
          <div className="space-y-3">
            {lessons.data.map((l) => (
              <LessonCard key={l.id} lesson={l} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-zinc-500">
            {retrospectiveId
              ? "No lessons for this retrospective yet."
              : "No lessons recorded yet."}
          </p>
        )}
      </CardBody>
    </Card>
  );
}
