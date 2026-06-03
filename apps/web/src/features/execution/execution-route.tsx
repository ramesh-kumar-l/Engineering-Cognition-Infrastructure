import { useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardBody } from "@/components/ui/card";
import { RoadmapPanel } from "./components/roadmap-panel";
import { GoalPanel } from "./components/goal-panel";
import { TaskPanel } from "./components/task-panel";

/** Execution screen — roadmaps → goals → tasks, each with stored-evidence "Why?". */
export function ExecutionRoute() {
  const [roadmapId, setRoadmapId] = useState<string | undefined>();
  const [goalId, setGoalId] = useState<string | undefined>();

  function selectRoadmap(id: string) {
    setRoadmapId(id);
    setGoalId(undefined);
  }

  return (
    <>
      <PageHeader
        title="Execution"
        subtitle="Turn evidence into action. Every goal and task carries the citations that justify it — open “Why?” to inspect the chain."
      />

      <div className="grid items-start gap-5 lg:grid-cols-3">
        <RoadmapPanel selectedId={roadmapId} onSelect={selectRoadmap} />

        {roadmapId ? (
          <GoalPanel roadmapId={roadmapId} selectedGoalId={goalId} onSelectGoal={setGoalId} />
        ) : (
          <EmptyHint text="Select or create a roadmap to add goals." />
        )}

        {goalId ? (
          <TaskPanel goalId={goalId} />
        ) : (
          <EmptyHint text="Select a goal to manage its tasks and dependencies." />
        )}
      </div>
    </>
  );
}

function EmptyHint({ text }: { text: string }) {
  return (
    <Card>
      <CardBody className="text-sm text-zinc-500">{text}</CardBody>
    </Card>
  );
}
