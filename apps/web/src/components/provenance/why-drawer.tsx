import * as Dialog from "@radix-ui/react-dialog";
import type { Citation } from "@/types/api";
import { ApiError } from "@/lib/api-client";
import { CitationCard } from "./citation-card";

interface WhyDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Title of the goal/task whose evidence is shown. */
  title: string;
  citations: Citation[] | undefined;
  isLoading: boolean;
  error: unknown;
}

/**
 * Slide-over panel rendering the stored citations behind a goal or task.
 * Fail-closed (AP-2): when there is no evidence, it says so explicitly rather
 * than implying the item is justified.
 */
export function WhyDrawer({ open, onOpenChange, title, citations, isLoading, error }: WhyDrawerProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm data-[state=open]:animate-in" />
        <Dialog.Content className="fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col border-l border-zinc-800 bg-zinc-950 shadow-2xl outline-none">
          <div className="flex items-start justify-between gap-3 border-b border-zinc-800 px-5 py-4">
            <div className="min-w-0">
              <Dialog.Title className="text-sm font-semibold text-zinc-100">
                Why does this exist?
              </Dialog.Title>
              <Dialog.Description className="mt-0.5 truncate text-xs text-zinc-500">
                {title}
              </Dialog.Description>
            </div>
            <Dialog.Close
              aria-label="Close"
              className="rounded-md px-2 py-1 text-sm text-zinc-400 outline-none hover:bg-zinc-800/60 focus-visible:ring-2 focus-visible:ring-zinc-600"
            >
              ✕
            </Dialog.Close>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto px-5 py-4">
            {isLoading ? (
              <p className="text-sm text-zinc-400">Loading evidence…</p>
            ) : error ? (
              <p className="text-sm text-red-300">
                {error instanceof ApiError ? error.detail : "Could not load evidence."}
              </p>
            ) : citations && citations.length > 0 ? (
              citations.map((c, i) => (
                <CitationCard key={`${c.source_id}-${i}`} citation={c} rank={i + 1} />
              ))
            ) : (
              <div className="rounded-lg border border-amber-800 bg-amber-950/40 px-4 py-3 text-sm text-amber-300">
                No stored evidence — this item is unverifiable. Create goals and tasks from cited
                Search results to build a traceable provenance chain.
              </div>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
