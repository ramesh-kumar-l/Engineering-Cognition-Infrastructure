import { Link } from "@tanstack/react-router";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ApiError } from "@/lib/api-client";
import { useEmbedDocument } from "../use-compress";

/** Embed a document into the vector index so it becomes searchable. */
export function EmbedPanel({ documentId }: { documentId: string }) {
  const embed = useEmbedDocument();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Make searchable</CardTitle>
      </CardHeader>
      <CardBody className="space-y-3 text-sm text-zinc-400">
        <p>Generate embeddings so this document surfaces in hybrid search with citations.</p>
        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={() => embed.mutate(documentId)} disabled={embed.isPending}>
            {embed.isPending ? "Embedding…" : "Embed for search"}
          </Button>
          {embed.isSuccess && (
            <>
              <Badge tone="good">{embed.data.chunks_embedded} chunks embedded</Badge>
              <Link to="/search" className="text-[--color-accent] hover:underline">
                Go to Search →
              </Link>
            </>
          )}
        </div>
        {embed.error && (
          <p className="text-red-300">
            Embedding failed:{" "}
            {embed.error instanceof ApiError ? embed.error.detail : "Unexpected error"}
          </p>
        )}
      </CardBody>
    </Card>
  );
}
