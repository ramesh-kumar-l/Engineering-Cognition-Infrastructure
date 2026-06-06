import { type ReactNode } from "react";
import { cn } from "@/lib/cn";

/**
 * Small, dependency-free markdown renderer. Supports headings, fenced code,
 * bullet/ordered lists, blockquotes, inline code, bold, and links. Renders to
 * React nodes (no HTML injection), which is enough for document bodies and
 * assistant answers without pulling in a parser dependency.
 */
export function Markdown({ text, className }: { text: string; className?: string }) {
  return <div className={cn("space-y-3 text-sm leading-relaxed text-fg", className)}>{renderBlocks(text)}</div>;
}

function renderBlocks(text: string): ReactNode[] {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const blocks: ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.trim() === "") {
      i++;
      continue;
    }

    // Fenced code block.
    if (line.startsWith("```")) {
      const body: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) body.push(lines[i++]);
      i++; // closing fence
      blocks.push(
        <pre
          key={key++}
          className="overflow-x-auto rounded-md border border-border bg-surface-raised px-3.5 py-3 font-mono text-xs text-fg"
        >
          <code>{body.join("\n")}</code>
        </pre>,
      );
      continue;
    }

    // Heading.
    const heading = /^(#{1,6})\s+(.*)$/.exec(line);
    if (heading) {
      const level = heading[1].length;
      const size = level <= 1 ? "text-lg" : level === 2 ? "text-base" : "text-sm";
      blocks.push(
        <p key={key++} className={cn("font-semibold tracking-tight text-fg", size)}>
          {renderInline(heading[2])}
        </p>,
      );
      i++;
      continue;
    }

    // List (consecutive - / * / 1. lines).
    if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const ordered = /^\s*\d+\.\s+/.test(line);
      const items: string[] = [];
      while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*([-*]|\d+\.)\s+/, ""));
        i++;
      }
      const ListTag = ordered ? "ol" : "ul";
      blocks.push(
        <ListTag
          key={key++}
          className={cn("space-y-1 pl-5 text-fg", ordered ? "list-decimal" : "list-disc")}
        >
          {items.map((it, idx) => (
            <li key={idx}>{renderInline(it)}</li>
          ))}
        </ListTag>,
      );
      continue;
    }

    // Blockquote.
    if (line.startsWith(">")) {
      blocks.push(
        <blockquote
          key={key++}
          className="border-l-2 border-border-strong pl-3 text-fg-muted italic"
        >
          {renderInline(line.replace(/^>\s?/, ""))}
        </blockquote>,
      );
      i++;
      continue;
    }

    // Paragraph (gather until blank line).
    const para: string[] = [];
    while (i < lines.length && lines[i].trim() !== "" && !lines[i].startsWith("```")) {
      para.push(lines[i]);
      i++;
    }
    blocks.push(
      <p key={key++} className="text-fg">
        {renderInline(para.join(" "))}
      </p>,
    );
  }

  return blocks;
}

const INLINE = /(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g;

function renderInline(text: string): ReactNode[] {
  const parts = text.split(INLINE).filter(Boolean);
  return parts.map((part, idx) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={idx} className="rounded bg-surface-raised px-1 py-0.5 font-mono text-[0.85em]">
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={idx} className="font-semibold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    const link = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(part);
    if (link) {
      return (
        <a
          key={idx}
          href={link[2]}
          target="_blank"
          rel="noreferrer"
          className="text-accent underline underline-offset-2 hover:brightness-110"
        >
          {link[1]}
        </a>
      );
    }
    return <span key={idx}>{part}</span>;
  });
}
