import { useState, type FormEvent } from "react";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";
import { WhyDrawer } from "@/components/provenance/why-drawer";
import { StatusSelect } from "./status-select";
import {
  useAddTaskDependency,
  useCreateTask,
  useTaskWhy,
  useTasks,
  useUpdateTaskStatus,
} from "../use-execution";

/** Right column: tasks for the active goal — status, upstream dependencies, "Why?". */
export function TaskPanel({ goalId }: { goalId: string }) {
  const tasks = useTasks(goalId);
  const create = useCreateTask();
  const updateStatus = useUpdateTaskStatus();
  const addDep = useAddTaskDependency(goalId);
  const [title, setTitle] = useState("");
  const [whyId, setWhyId] = useState<string | undefined>();
  const [depFor, setDepFor] = useState<string | undefined>();
  const [upstream, setUpstream] = useState("");
  const why = useTaskWhy(whyId, Boolean(whyId));

  function onCreate(e: FormEvent) {
    e.preventDefault();
    const t = title.trim();
    if (!t) return;
    create.mutate(
      { title: t, goal_id: goalId, position: tasks.data?.length ?? 0 },
      { onSuccess: () => setTitle("") },
    );
  }

  function onAddDep(taskId: string) {
    const up = upstream.trim();
    if (!up) return;
    addDep.mutate(
      { taskId, upstreamId: up },
      {
        onSuccess: () => {
          setUpstream("");
          setDepFor(undefined);
        },
      },
    );
  }

  const whyTask = tasks.data?.find((t) => t.id === whyId);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tasks</CardTitle>
      </CardHeader>
      <CardBody className="space-y-3">
        <form onSubmit={onCreate} className="flex gap-2">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="New task title"
          />
          <Button type="submit" disabled={!title.trim() || create.isPending}>
            Add
          </Button>
        </form>
        {create.error instanceof ApiError && (
          <p className="text-xs text-red-300">{create.error.detail}</p>
        )}

        {tasks.isLoading ? (
          <p className="text-sm text-zinc-400">Loading…</p>
        ) : tasks.error ? (
          <p className="text-sm text-red-300">
            {tasks.error instanceof ApiError ? tasks.error.detail : "Failed to load tasks."}
          </p>
        ) : tasks.data && tasks.data.length > 0 ? (
          <ul className="space-y-2">
            {tasks.data.map((t) => (
              <li key={t.id} className="rounded-md border border-zinc-800 px-3 py-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="min-w-0 flex-1 truncate text-sm font-medium text-zinc-100">
                    <span className="mr-2 font-mono text-xs text-zinc-600">{t.position}</span>
                    {t.title}
                  </span>
                  <div className="flex shrink-0 items-center gap-1">
                    <Button
                      variant="ghost"
                      className="px-2 py-1 text-xs"
                      onClick={() => setDepFor(depFor === t.id ? undefined : t.id)}
                    >
                      Depends…
                    </Button>
                    <Button
                      variant="ghost"
                      className="px-2 py-1 text-xs"
                      onClick={() => setWhyId(t.id)}
                    >
                      Why?
                    </Button>
                  </div>
                </div>
                <div className="mt-2">
                  <StatusSelect
                    value={t.status}
                    disabled={updateStatus.isPending}
                    onChange={(status) => updateStatus.mutate({ id: t.id, input: { status } })}
                  />
                </div>
                {depFor === t.id && (
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center gap-2">
                      <Input
                        value={upstream}
                        onChange={(e) => setUpstream(e.target.value)}
                        placeholder="Upstream task ID (must finish first)"
                        className="font-mono text-xs"
                      />
                      <Button
                        variant="outline"
                        className="px-2 py-1 text-xs"
                        disabled={!upstream.trim() || addDep.isPending}
                        onClick={() => onAddDep(t.id)}
                      >
                        Link
                      </Button>
                    </div>
                    {addDep.error instanceof ApiError && (
                      <p className="text-xs text-red-300">{addDep.error.detail}</p>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-500">No tasks for this goal yet.</p>
        )}
      </CardBody>

      <WhyDrawer
        open={Boolean(whyId)}
        onOpenChange={(o) => !o && setWhyId(undefined)}
        title={whyTask?.title ?? "Task"}
        citations={why.data}
        isLoading={why.isLoading}
        error={why.error}
      />
    </Card>
  );
}
