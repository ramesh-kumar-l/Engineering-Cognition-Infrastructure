import type { SearchResponse } from "@/types/api";
import { ApiError } from "@/lib/api-client";
import { CitationCard } from "@/components/provenance/citation-card";
import { HasCitationsBanner } from "@/components/provenance/has-citations-banner";
import { RetrievalStagesChip } from "@/components/provenance/retrieval-stages-chip";
import { Card, CardBody } from "@/components/ui/card";

interface Props {
  data: SearchResponse | undefined;
  isPending: boolean;
  error: unknown;
  hasSearched: boolean;
}

export function SearchResults({ data, isPending, error, hasSearched }: Props) {
  if (isPending) {
    return <StatusCard>Searching across documents and notes…</StatusCard>;
  }

  if (error) {
    const detail = error instanceof ApiError ? error.detail : "Unexpected error";
    const hint =
      error instanceof ApiError && error.status === 401
        ? " — sign in is required for retrieval."
        : "";
    return (
      <StatusCard tone="error">
        Search failed: {detail}
        {hint}
      </StatusCard>
    );
  }

  if (!hasSearched) {
    return (
      <StatusCard>
        Ask a question. Every result returns with its sources so you can verify the answer.
      </StatusCard>
    );
  }

  if (!data || data.citations.length === 0) {
    return (
      <div className="space-y-4">
        <HasCitationsBanner hasCitations={false} count={0} />
        <StatusCard>No matching evidence found. Try ingesting more sources first.</StatusCard>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <HasCitationsBanner hasCitations={data.has_citations} count={data.citations.length} />
      </div>
      <RetrievalStagesChip stages={data.retrieval_stages} />
      <div className="space-y-3">
        {data.citations.map((citation, i) => (
          <CitationCard
            key={`${citation.source_id}-${citation.chunk_index ?? i}`}
            citation={citation}
            rank={i + 1}
          />
        ))}
      </div>
    </div>
  );
}

function StatusCard({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "neutral" | "error";
}) {
  return (
    <Card>
      <CardBody className={tone === "error" ? "text-sm text-red-300" : "text-sm text-zinc-400"}>
        {children}
      </CardBody>
    </Card>
  );
}
