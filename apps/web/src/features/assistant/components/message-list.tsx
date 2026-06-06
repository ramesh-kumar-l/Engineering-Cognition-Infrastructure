import { Card, CardBody } from "@/components/ui/card";
import type { ChatMessage } from "../use-assistant";
import { MessageBubble } from "./message-bubble";

/** Scrolling transcript. Shows a primer when the conversation is empty. */
export function MessageList({ messages }: { messages: ChatMessage[] }) {
  if (messages.length === 0) {
    return (
      <Card>
        <CardBody className="text-sm text-fg-muted">
          Ask a question about your engineering memory. Answers are synthesized only from
          retrieved sources and arrive with their citations — if nothing matches, the assistant
          says so rather than guessing.
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-5">
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}
    </div>
  );
}
