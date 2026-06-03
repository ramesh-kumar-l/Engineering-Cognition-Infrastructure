import { useState, type FormEvent } from "react";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api-client";
import { cn } from "@/lib/cn";
import { useCreateRoadmap, useRoadmaps } from "../use-execution";

/** Left column: create roadmaps and pick the active one (drives the goals column). */
export function RoadmapPanel({
  selectedId,
  onSelect,
}: {
  selectedId: string | undefined;
  onSelect: (id: string) => void;
}) {
  const roadmaps = useRoadmaps();
  const create = useCreateRoadmap();
  const [title, setTitle] = useState("");

  function onCreate(e: FormEvent) {
    e.preventDefault();
    const t = title.trim();
    if (!t) return;
    create.mutate(
      { title: t },
      {
        onSuccess: (r) => {
          setTitle("");
          onSelect(r.id);
        },
      },
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Roadmaps</CardTitle>
      </CardHeader>
      <CardBody className="space-y-3">
        <form onSubmit={onCreate} className="flex gap-2">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="New roadmap title"
          />
          <Button type="submit" disabled={!title.trim() || create.isPending}>
            Add
          </Button>
        </form>
        {create.error instanceof ApiError && (
          <p className="text-xs text-red-300">{create.error.detail}</p>
        )}

        {roadmaps.isLoading ? (
          <p className="text-sm text-zinc-400">Loading…</p>
        ) : roadmaps.error ? (
          <p className="text-sm text-red-300">
            {roadmaps.error instanceof ApiError ? roadmaps.error.detail : "Failed to load roadmaps."}
          </p>
        ) : roadmaps.data && roadmaps.data.length > 0 ? (
          <ul className="space-y-1">
            {roadmaps.data.map((r) => (
              <li key={r.id}>
                <button
                  onClick={() => onSelect(r.id)}
                  className={cn(
                    "w-full rounded-md px-3 py-2 text-left text-sm transition",
                    r.id === selectedId
                      ? "bg-zinc-800/70 text-zinc-100"
                      : "text-zinc-300 hover:bg-zinc-800/40",
                  )}
                >
                  <span className="block truncate font-medium">{r.title}</span>
                  {r.description && (
                    <span className="block truncate text-xs text-zinc-500">{r.description}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-zinc-500">No roadmaps yet. Create one to begin.</p>
        )}
      </CardBody>
    </Card>
  );
}
