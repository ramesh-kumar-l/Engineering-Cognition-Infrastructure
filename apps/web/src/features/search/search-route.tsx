import { useState, type FormEvent } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useSearch } from "./use-search";
import { SearchResults } from "./components/search-results";

/** Search screen — the provenance showcase: query in, cited evidence out. */
export function SearchRoute() {
  const [query, setQuery] = useState("");
  const search = useSearch();

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    search.mutate({ query: q });
  }

  return (
    <>
      <PageHeader
        title="Search"
        subtitle="Hybrid keyword + semantic retrieval. Answers always arrive with their sources."
      />

      <form onSubmit={onSubmit} className="mb-6 flex gap-2.5">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Why did we choose hybrid retrieval?"
          aria-label="Search query"
        />
        <Button type="submit" disabled={search.isPending || !query.trim()}>
          {search.isPending ? "Searching…" : "Search"}
        </Button>
      </form>

      <SearchResults
        data={search.data}
        isPending={search.isPending}
        error={search.error}
        hasSearched={search.isPending || search.isSuccess || search.isError}
      />
    </>
  );
}
