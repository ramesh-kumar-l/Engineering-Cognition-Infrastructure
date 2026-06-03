import { useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { RetrospectivePanel } from "./components/retrospective-panel";
import { LessonPanel } from "./components/lesson-panel";

/** Reflection screen — run retrospectives, then browse the lessons they yield. */
export function ReflectionRoute() {
  const [retrospectiveId, setRetrospectiveId] = useState<string | undefined>();

  return (
    <>
      <PageHeader
        title="Reflection"
        subtitle="Close the loop: turn completed work into durable, evidence-backed lessons. Supersede a lesson when belief changes — the lineage stays traceable."
      />

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.5fr)]">
        <RetrospectivePanel selectedId={retrospectiveId} onSelect={setRetrospectiveId} />
        <LessonPanel retrospectiveId={retrospectiveId} />
      </div>
    </>
  );
}
