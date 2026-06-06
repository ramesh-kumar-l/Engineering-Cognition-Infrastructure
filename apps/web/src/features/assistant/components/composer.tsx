import { useState, type FormEvent, type KeyboardEvent } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface Props {
  onSend: (query: string) => void;
  onStop: () => void;
  isStreaming: boolean;
}

/** Chat composer: Enter sends, Shift+Enter inserts a newline. */
export function Composer({ onSend, onStop, isStreaming }: Props) {
  const [text, setText] = useState("");

  function submit(e: FormEvent) {
    e.preventDefault();
    const q = text.trim();
    if (!q || isStreaming) return;
    onSend(q);
    setText("");
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit(e);
    }
  }

  return (
    <form onSubmit={submit} className="flex items-end gap-2.5">
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Ask about decisions, lessons, or past work…"
        aria-label="Assistant question"
        className="min-h-12"
        rows={1}
      />
      {isStreaming ? (
        <Button type="button" variant="outline" onClick={onStop}>
          Stop
        </Button>
      ) : (
        <Button type="submit" disabled={!text.trim()}>
          Ask
        </Button>
      )}
    </form>
  );
}
