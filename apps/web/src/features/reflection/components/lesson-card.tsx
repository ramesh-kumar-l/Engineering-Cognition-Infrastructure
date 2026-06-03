import { useState } from "react";
import { Card, CardBody } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Field } from "@/components/ui/field";
import { ApiError } from "@/lib/api-client";
import { EvidenceList } from "@/components/provenance/evidence-list";
import {
  LESSON_CONFIDENCES,
  LESSON_SCOPES,
  type EvidenceInput,
  type Lesson,
} from "@/types/api";
import { EvidenceEditor } from "./evidence-editor";
import { useSupersedeLesson } from "../use-reflection";

const CONFIDENCE_TONE = { low: "warn", medium: "info", high: "good" } as const;

/** One lesson: claim, confidence/scope/status badges, evidence, and supersession. */
export function LessonCard({ lesson }: { lesson: Lesson }) {
  const supersede = useSupersedeLesson();
  const [open, setOpen] = useState(false);
  const [claim, setClaim] = useState("");
  const [confidence, setConfidence] = useState("medium");
  const [scope, setScope] = useState(lesson.scope);
  const [evidence, setEvidence] = useState<EvidenceInput[]>([]);

  const isActive = lesson.status === "active";
  const tone = CONFIDENCE_TONE[lesson.confidence as keyof typeof CONFIDENCE_TONE] ?? "neutral";

  function onSupersede() {
    const c = claim.trim();
    if (!c) return;
    supersede.mutate(
      { id: lesson.id, input: { claim: c, confidence, scope, evidence } },
      {
        onSuccess: () => {
          setOpen(false);
          setClaim("");
          setEvidence([]);
        },
      },
    );
  }

  return (
    <Card>
      <CardBody className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <p className="min-w-0 flex-1 text-sm font-medium text-zinc-100">{lesson.claim}</p>
          <div className="flex shrink-0 flex-wrap items-center justify-end gap-1.5">
            <Badge tone={tone}>{lesson.confidence}</Badge>
            <Badge tone="neutral">{lesson.scope}</Badge>
            <Badge tone={isActive ? "good" : "warn"}>{lesson.status}</Badge>
          </div>
        </div>

        {lesson.supersedes_id && (
          <p className="font-mono text-[11px] text-zinc-500">
            supersedes {lesson.supersedes_id.slice(0, 8)}
          </p>
        )}

        <EvidenceList evidence={lesson.evidence} />

        {isActive && (
          <div className="border-t border-zinc-800 pt-2">
            <Button
              variant="ghost"
              className="px-2 py-1 text-xs"
              onClick={() => setOpen((v) => !v)}
            >
              {open ? "Cancel" : "Supersede…"}
            </Button>

            {open && (
              <div className="mt-2 space-y-2.5">
                <Field label="New claim">
                  <Input
                    value={claim}
                    onChange={(e) => setClaim(e.target.value)}
                    placeholder="What we now believe instead"
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
                {supersede.error instanceof ApiError && (
                  <p className="text-xs text-red-300">{supersede.error.detail}</p>
                )}
                <Button
                  variant="outline"
                  className="text-xs"
                  disabled={!claim.trim() || supersede.isPending}
                  onClick={onSupersede}
                >
                  Replace lesson
                </Button>
              </div>
            )}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
