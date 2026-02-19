import React from "react";
import type { Address } from "../types";

interface AddressTableProps {
  addresses: Address[];
  selectedIds: number[];
  onToggleSelect: (id: number) => void;
  onToggleSelectAll: () => void;
  onRowClick: (id: number) => void;
}

const formatScore = (score: number) => `${(score * 100).toFixed(1)}%`;

export const AddressTable: React.FC<AddressTableProps> = ({
  addresses,
  selectedIds,
  onToggleSelect,
  onToggleSelectAll,
  onRowClick
}) => {
  const allSelected =
    addresses.length > 0 && selectedIds.length === addresses.length;

  return (
    <table>
      <thead>
        <tr>
          <th>
            <input
              type="checkbox"
              checked={allSelected}
              onChange={onToggleSelectAll}
            />
          </th>
          <th>ID</th>
          <th>Input address</th>
          <th>Matched address</th>
          <th className="align-right">Match score</th>
        </tr>
      </thead>
      <tbody>
        {addresses.map((addr) => {
          const isSelected = selectedIds.includes(addr.id);
          return (
            <tr key={addr.id} onClick={() => onRowClick(addr.id)}>
              <td
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleSelect(addr.id);
                }}
              >
                <input type="checkbox" checked={isSelected} readOnly />
              </td>
              <td>{addr.id}</td>
              <td>{addr.address}</td>
              <td>{addr.matched_address}</td>
              <td className="align-right">
                <div style={{ minWidth: 110 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: "0.25rem",
                      marginBottom: "0.15rem"
                    }}
                  >
                    <span className="badge-score">
                      {formatScore(addr.match_score)}
                    </span>
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-bar"
                      style={{
                        width: `${Math.max(
                          0,
                          Math.min(1, addr.match_score)
                        ) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};
