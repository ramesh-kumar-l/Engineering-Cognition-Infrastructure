import { useEffect, useRef } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { useAssistant } from "./use-assistant";
import { MessageList } from "./components/message-list";
import { Composer } from "./components/composer";

/** Assistant screen — grounded, citation-backed chat over the corpus (fail-closed). */
export function AssistantRoute() {
  const { messages, isStreaming, send, stop } = useAssistant();
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="Assistant"
        subtitle="Ask questions over your engineering memory. Every answer is synthesized only from cited sources."
      />

      <div className="min-h-0 flex-1 overflow-y-auto pb-4">
        <MessageList messages={messages} />
        <div ref={endRef} />
      </div>

      <div className="shrink-0 border-t border-border pt-4">
        <Composer onSend={send} onStop={stop} isStreaming={isStreaming} />
      </div>
    </div>
  );
}
