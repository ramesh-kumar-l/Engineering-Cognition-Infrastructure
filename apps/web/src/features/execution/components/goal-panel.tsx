import { useState, type FormEvent } from "react";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";
import { cn } from "@/lib/cn";
import { WhyDrawer } from "@/components/provenance/why-drawer";
import { StatusSelect } from "./status-select";
import { useCreateGoal, useGoals, useGoalWhy, useUpdateGoalStatus } from "../use-execution";

/** Middle column: goals for the active roadmap, with status control + "Why?" evidence. */
export function GoalPanel({
  roadmapId,
  selectedGoalId,
  onSelectGoal,
}: {
  roadmapId: string;
  selectedGoalId: string | undefined;
  onSelectGoal: (id: string) => void;
}) {
  const goals = useGoals(roadmapId);
  const create = useCreateGoal();
  const updateStatus = useUpdateGoalStatus();
  const [title, setTitle] = useState("");
  const [whyId, setWhyId] = useState<string | undefined>();
  const why = useGoalWhy(whyId, Boolean(whyId));

  function onCreate(e: FormEvent) {
    e.preventDefault();
    const t = title.trim();
    if (!t) return;
    create.mutate(
      { title: t, roadmap_id: roadmapId },
      { onSuccess: () => setTitle("") },
    );
  }

  const whyGoal = goals.data?.find((g) => g.id === whyId);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Goals</CardTitle>
      </CardHeader>
      <CardBody className="space-y-3">
        <form onSubmit={onCreate} className="flex gap-2">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="New goal title"
          />
          <Button type="submit" disabled={!title.trim() || create.isPending}>
            Add
          </Button>
        </form>
        {create.error instanceof ApiError && (
          <p className="text-xs text-red-300">{create.error.detail}</p>
        )}

        {goals.isLoading ? (
          <p className="text-sm text-zinc-400">Loading…</p>
        ) : goals.error ? (
          <p className="text-sm text-red-300">
            {goals.error instanceof ApiError ? goals.error.detail : "Failed to load goals."}
          </p>
        ) : goals.data && goals.data.length > 0 ? (
          <ul className="space-y-2">
            {goals.data.map((g) => (
              <li
                key={g.id}
                className={cn(
                  "rounded-md border px-3 py-2",
                  g.id === selectedGoalId
                    ? "border-zinc-700 bg-zinc-800/50"
                    : "border-zinc-800",
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <button
                    onClick={() => onSelectGoal(g.id)}
                    className="min-w-0 flex-1 text-left text-sm font-medium text-zinc-100"
                  >
                    <span className="block truncate">{g.title}</span>
                  </button>
                  <Button
                    variant="ghost"
                    className="px-2 py-1 text-xs"
                    onClick={() => setWhyId(g.id)}
                  >
                    Why?
                  </Button>
                </div>
                <div className="mt-2">
                  <StatusSelect
                    value={g.status}
                    disabled={updateStatus.isPending}
                    onChange={(status) => updateStatus.mutate({ id: g.id, input: { status } })}
                  />
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-500">No goals in this roadmap yet.</p>
        )}
      </CardBody>

      <WhyDrawer
        open={Boolean(whyId)}
        onOpenChange={(o) => !o && setWhyId(undefined)}
        title={whyGoal?.title ?? "Goal"}
        citations={why.data}
        isLoading={why.isLoading}
        error={why.error}
      />
    </Card>
  );
}
