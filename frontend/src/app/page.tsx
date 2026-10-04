import BrainTheater from "@/features/brain-theater/BrainTheater";
import DatasetExplorer from "@/features/dataset-explorer/DatasetExplorer";
import SQLStudio from "@/features/sql-studio/SQLStudio";
import ChartStudio from "@/features/chart-studio/ChartStudio";
import DashboardBuilder from "@/features/dashboard-builder/DashboardBuilder";

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight">DataMind-King</h1>
          <p className="text-muted-foreground mt-2">
            World's most advanced AI Data Analyst platform
          </p>
        </header>

        {/* Brain Theater */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Brain Theater</h2>
          <BrainTheater />
        </section>

        {/* Dataset Explorer */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Dataset Explorer</h2>
          <DatasetExplorer />
        </section>

        {/* SQL Studio */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">SQL Studio</h2>
          <SQLStudio />
        </section>

        {/* Chart Studio */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Chart Studio</h2>
          <ChartStudio />
        </section>

        {/* Dashboard Builder */}
        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Dashboard Builder</h2>
          <DashboardBuilder />
        </section>
      </div>
    </main>
  );
}
