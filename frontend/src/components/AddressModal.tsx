import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import React, { useEffect, useState } from "react";
import { createAddress, fetchAddress, updateAddress } from "../api";
import type { Address } from "../types";

interface AddressModalProps {
  addressId?: number;
  open: boolean;
  onClose: () => void;
  onSaved: (updated: Address) => void;
}

const formatScore = (score: number | undefined) =>
  typeof score === "number" ? `${(score * 100).toFixed(1)}%` : "—";

export const AddressModal: React.FC<AddressModalProps> = ({
  addressId,
  open,
  onClose,
  onSaved,
}) => {
  const isCreate = addressId === undefined;

  const [address, setAddress] = useState("");
  const [matchedAddress, setMatchedAddress] = useState("");
  const [matchScore, setMatchScore] = useState<number | undefined>(undefined);

  const { data, isLoading, isFetching, isError } = useQuery({
    queryKey: ["addresses", "detail", addressId],
    queryFn: () => fetchAddress(addressId || -1),
    enabled: !!addressId,
  });

  const queryClient = useQueryClient();

  useEffect(() => {
    if (data) {
      setAddress(data?.address || "");
      setMatchScore(data?.match_score || 0);
      setMatchedAddress(data?.matched_address || "");
    } else {
      setAddress("");
      setMatchScore(undefined);
      setMatchedAddress("");
    }
  }, [data]);

  const updateAddressMutation = useMutation({
    mutationFn: updateAddress,
  });

  const createAddressMutation = useMutation({
    mutationFn: createAddress,
  });

  if (!open) return null;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();

    createAddressMutation
      .mutateAsync({
        address: address,
      })
      .then((address) => {
        queryClient.invalidateQueries({
          queryKey: ["addresses", "list"],
        });
        onSaved(address);
      });
  };

  const handleUpdate = async () => {
    if (addressId && address) {
      updateAddressMutation.mutateAsync({ id: addressId, address }).then(() => {
        queryClient.invalidateQueries({
          queryKey: ["addresses", "detail", addressId],
        });
        queryClient.invalidateQueries({
          queryKey: ["addresses", "list"],
        });
      });
    }
  };

  const title = isCreate ? "Add address" : "Address details";

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <form onSubmit={isCreate ? handleCreate : (e) => e.preventDefault()}>
          <div className="modal-header">
            <h2>{title}</h2>
            <button
              type="button"
              className="secondary small"
              onClick={onClose}
              disabled={isLoading}
            >
              ✕
            </button>
          </div>
          <div className="modal-body">
            {createAddressMutation.isError ||
              (updateAddressMutation.isError && (
                <div className="error-banner">
                  Something went wrong when saving the address.
                </div>
              ))}

            {isError && (
              <div className="error-banner">
                Something went wrong while loading the address.
              </div>
            )}

            {isLoading ? (
              <p className="muted">Loading address...</p>
            ) : (
              <>
                <div className="form-row">
                  <label htmlFor="address">Input address</label>
                  <textarea
                    id="address"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    required
                  />
                  <p className="muted">
                    For new addresses, the backend will query Mapbox and compute
                    a <code>matched_address</code> and <code>match_score</code>.
                  </p>
                </div>
                {!isCreate && (
                  <>
                    <div className="form-row">
                      <label>Matched address</label>
                      <textarea value={matchedAddress} disabled readOnly />
                    </div>
                    <div className="form-row">
                      <label>Current similarity score</label>
                      <div className="pill-group">
                        <span className="chip filled">
                          {formatScore(matchScore)}
                        </span>
                        <span className="chip">
                          The score is computed on the server using your
                          similarity logic.
                        </span>
                      </div>
                    </div>
                  </>
                )}
              </>
            )}
          </div>
          <div className="modal-footer">
            <div />
            <div className="toolbar-right">
              {!isCreate && (
                <button
                  type="button"
                  className="secondary"
                  onClick={handleUpdate}
                  disabled={updateAddressMutation.isPending}
                >
                  {updateAddressMutation.isPending
                    ? "⟳ Updating..."
                    : "⟳ Update"}
                </button>
              )}
              {isCreate && (
                <button
                  type="submit"
                  disabled={createAddressMutation.isPending}
                >
                  {createAddressMutation.isPending
                    ? "⟳ Creating..."
                    : "⟳ Create"}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
