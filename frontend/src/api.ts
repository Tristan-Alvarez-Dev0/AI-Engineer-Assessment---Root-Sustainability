import type { Address } from "./types";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export async function fetchAddresses(): Promise<Address[]> {
  const res = await fetch(`${API_BASE}/addresses`);
  if (!res.ok) {
    throw new Error("Failed to fetch addresses");
  }
  return res.json();
}

export async function updateAddress({id, address}: {
  id: number;
  address: string;
}): Promise<Address> {
  const res = await fetch(`${API_BASE}/addresses/${id}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({address})
  });
  if (!res.ok) {
    throw new Error("Failed to create address");
  }
  return res.json();
}

export async function fetchAddress(id: number): Promise<Address> {
  const res = await fetch(`${API_BASE}/addresses/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch address");
  }
  return res.json();
}

export async function createAddress(input: {
  address: string;
}): Promise<Address> {
  const res = await fetch(`${API_BASE}/addresses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });
  if (!res.ok) {
    throw new Error("Failed to create address");
  }
  return res.json();
}

export async function refreshAddresses(input: {
  ids: number[] | null;
}): Promise<Address[]> {
  const res = await fetch(`${API_BASE}/addresses/refresh`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });
  if (!res.ok) {
    throw new Error("Failed to refresh addresses");
  }
  return res.json();
}
