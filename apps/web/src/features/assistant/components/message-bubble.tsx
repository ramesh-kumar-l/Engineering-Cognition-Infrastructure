import { Markdown } from "@/components/ui/markdown";
import { CitationCard } from "@/components/provenance/citation-card";
import { HasCitationsBanner } from "@/components/provenance/has-citations-banner";
import type { ChatMessage } from "../use-assistant";

/** One conversation turn. Assistant turns carry their evidence inline (AP-2). */
export function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-accent-strong px-4 py-2.5 text-sm text-accent-fg">
          {message.content}
        </div>
      </div>
    );
  }

  const failClosed = message.hasCitations === false && !message.streaming && !message.error;

  return (
    <div className="space-y-3">
      <div className="max-w-[85%] rounded-2xl rounded-bl-sm border border-border bg-surface px-4 py-3">
        {message.error ? (
          <p className="text-sm text-danger">{message.error}</p>
        ) : failClosed ? (
          <p className="text-sm text-fg-muted">
            I couldn’t find any sources for that, so I won’t answer — ECI fails closed when
            there’s no evidence. Try ingesting and embedding relevant documents first.
          </p>
        ) : (
          <div className="flex items-start">
            <Markdown text={message.content} />
            {message.streaming && (
              <span
                aria-hidden
                className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-fg-muted align-text-bottom"
              />
            )}
          </div>
        )}
      </div>

      {message.hasCitations !== undefined && !message.error && (
        <div className="max-w-[85%] space-y-2">
          <HasCitationsBanner
            hasCitations={message.hasCitations}
            count={message.citations?.length ?? 0}
          />
          {message.citations?.map((c, i) => (
            <CitationCard key={`${c.source_id}-${c.chunk_index ?? i}`} citation={c} rank={i + 1} />
          ))}
        </div>
      )}
    </div>
  );
}
