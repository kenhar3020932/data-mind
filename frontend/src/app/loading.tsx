"use client";

/** Loading Page - Skeleton UI */
export default function Loading() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header skeleton */}
        <div className="space-y-2">
          <div className="h-8 w-48 bg-card rounded animate-pulse" />
          <div className="h-4 w-72 bg-card rounded animate-pulse" />
        </div>

        {/* Main content grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="glass-card p-6 space-y-4">
              <div className="h-5 w-32 bg-card rounded animate-pulse" />
              <div className="h-20 bg-card rounded animate-pulse" />
              <div className="flex gap-2">
                <div className="h-8 w-20 bg-card rounded animate-pulse" />
                <div className="h-8 w-16 bg-card rounded animate-pulse" />
              </div>
            </div>
          ))}
        </div>

        {/* Brain Theater skeleton */}
        <div className="glass-card p-6">
          <div className="h-6 w-40 bg-card rounded animate-pulse mb-4" />
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-card rounded animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}