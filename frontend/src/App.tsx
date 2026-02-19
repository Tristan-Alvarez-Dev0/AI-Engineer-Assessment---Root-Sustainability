import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import React, { useState } from "react";
import { fetchAddresses, refreshAddresses } from "./api";
import { AddressModal } from "./components/AddressModal";
import { AddressTable } from "./components/AddressTable";

const App: React.FC = () => {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"view" | "create">("view");
  const [activeId, setActiveId] = useState<number | undefined>(undefined);

  const { data, isLoading, isFetching, isError } = useQuery({
    queryKey: ["addresses", "list"],
    queryFn: () => fetchAddresses(),
  });

  const refreshAddressesMutation = useMutation({
    mutationFn: refreshAddresses,
  });

  const queryClient = useQueryClient();

  const addresses = data || [];

  const handleToggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleToggleSelectAll = () => {
    if (selectedIds.length === addresses.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(addresses.map((a) => a.id));
    }
  };

  const handleRowClick = (id: number) => {
    setModalMode("view");
    setActiveId(id);
    setModalOpen(true);
  };

  const handleAddClick = () => {
    setModalMode("create");
    setActiveId(undefined);
    setModalOpen(true);
  };

  const refreshPage = () => {
    queryClient.invalidateQueries({
      queryKey: ["addresses", "list"],
    });
  };

  const handleRefreshSelected = async () => {
    refreshAddressesMutation
      .mutateAsync({ ids: selectedIds })
      .then(() => refreshPage());
  };

  const handleRefreshAll = async () => {
    refreshAddressesMutation
      .mutateAsync({ ids: null })
      .then(() => refreshPage());
  };

  const numSelected = selectedIds.length;

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Address similarity assessment</h1>
        <span className="muted">
          Frontend stub &mdash; focus your work on the backend + Mapbox +
          similarity logic.
        </span>
      </header>

      <main className="app-main">
        <div className="card">
          <div className="toolbar">
            <div className="toolbar-left">
              <button type="button" onClick={handleAddClick}>
                ＋ Add address
              </button>
              {numSelected > 0 ? (
                <button
                  type="button"
                  className="secondary"
                  disabled={
                    numSelected === 0 || refreshAddressesMutation.isPending
                  }
                  onClick={handleRefreshSelected}
                >
                  {refreshAddressesMutation.isPending
                    ? "⟳ Refreshing..."
                    : "⟳ Refresh selected"}
                </button>
              ) : (
                <button
                  type="button"
                  className="secondary"
                  onClick={handleRefreshAll}
                  disabled={refreshAddressesMutation.isPending}
                >
                  {refreshAddressesMutation.isPending
                    ? "⟳ Refreshing..."
                    : "⟳ Refresh all"}
                </button>
              )}
            </div>
            <div className="toolbar-right">
              <button
                type="button"
                className="secondary small"
                onClick={refreshPage}
                disabled={isLoading}
              >
                ⟳ Reload
              </button>
              <span className="muted">
                {numSelected > 0 ? (
                  <>
                    <strong>{numSelected}</strong> selected
                  </>
                ) : (
                  `${addresses.length} addresses`
                )}
              </span>
            </div>
          </div>

          {isError && (
            <div className="error-banner">
              Something went wrong while loading the addresses.
            </div>
          )}

          {isLoading || isFetching ? (
            <div className="empty-state">
              <h2>Loading addresses…</h2>
              <p className="muted">
                If this takes long, check that your backend is running and{" "}
                <code>VITE_API_BASE_URL</code> is configured.
              </p>
            </div>
          ) : addresses.length === 0 ? (
            <div className="empty-state">
              <h2>No addresses yet</h2>
              <p className="muted">
                Use &ldquo;Add address&rdquo; to create one. The backend will
                query Mapbox and compute a similarity score.
              </p>
            </div>
          ) : (
            <AddressTable
              addresses={addresses}
              selectedIds={selectedIds}
              onToggleSelect={handleToggleSelect}
              onToggleSelectAll={handleToggleSelectAll}
              onRowClick={handleRowClick}
            />
          )}
        </div>
      </main>

      <AddressModal
        open={modalOpen}
        addressId={activeId}
        onClose={() => setModalOpen(false)}
        onSaved={(address) => setActiveId(address.id)}
      />
    </div>
  );
};

export default App;
