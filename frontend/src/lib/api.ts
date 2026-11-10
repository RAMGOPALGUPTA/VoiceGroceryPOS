export const API_BASE = "http://127.0.0.1:8000/api/v1";

export type Product = {
  id: number;
  sku: string;
  name: string;
  brand?: string | null;
  selling_price: string | number;
  cost_price?: string | number | null;
  stock_quantity: string | number;
  stock_unit: string;
  sale_unit: string;
  reorder_level?: string | number;
  tax_rate?: string | number | null;
  is_active: boolean;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export type Sale = {
  id: number;
  receipt_number: string;
  status: string;
  subtotal: string;
  tax_total: string;
  discount_total: string;
  grand_total: string;
  payment_method: string;
  created_at: string;
  items: {
    product_id: number;
    name_snapshot: string;
    sku_snapshot: string;
    quantity: string;
    unit_price: string;
    line_total: string;
    unit_snapshot: string;
  }[];
};
export type StockSummary = {
  product_count: number;
  low_stock_count: number;
  products: Product[];
};
export type ReportSummary = {
  today_sales_count: number;
  today_revenue: string;
  all_time_sales_count: number;
  all_time_revenue: string;
  low_stock_count: number;
  inventory_units: string;
};
export type VoiceStatus = {
  enabled: boolean;
  package_available: boolean;
  model_available: boolean;
  model_path: string;
  message: string;
};
export type ImportRow = {
  row_number: number;
  sku?: string | null;
  name?: string | null;
  selling_price?: string | null;
  stock_quantity?: string | null;
  action: string;
  errors: string[];
};
export type ImportPreview = {
  import_id: string;
  filename: string;
  row_count: number;
  valid_count: number;
  error_count: number;
  rows: ImportRow[];
  stock_modes: string[];
};
export const api = {
  previewImport: async (file: File) => {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/inventory/import/preview",
      { method: "POST", body },
    );
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || "Import preview failed");
    }
    return response.json() as Promise<ImportPreview>;
  },
  commitImport: (id: string, mode: "replace" | "add") =>
    request<{ status: string; processed_rows: number }>(
      `/inventory/import/${id}/commit?stock_mode=${mode}`,
      { method: "POST" },
    ),
  products: () => request<Product[]>("/products"),
  voiceStatus: () => request<VoiceStatus>("/voice/status"),
  transcribe: async (blob: Blob) => {
    const form = new FormData();
    form.append("file", blob, "voice.webm");
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/voice/transcribe",
      { method: "POST", body: form },
    );
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || "Voice transcription failed");
    }
    const transcript = (await response.json()) as {
      text: string;
      language: string;
      language_probability: number;
    };
    return request<{
      transcript: string;
      items: {
        product_id: number;
        name: string;
        quantity: string;
        unit: string;
        selling_price: string;
        confidence: number;
        requires_confirmation: boolean;
      }[];
      unmatched_text: string;
      confirmation_required: boolean;
    }>("/voice/interpret", {
      method: "POST",
      body: JSON.stringify({ transcript: transcript.text }),
    });
  },
  checkout: (payload: {
    idempotency_key: string;
    payment_method: "cash" | "upi" | "card" | "other";
    discount: string;
    items: { product_id: number; quantity: number }[];
  }) =>
    request<Sale>("/sales/checkout", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  sales: () => request<Sale[]>("/sales"),
  refund: (id: number, reason: string) =>
    request("/sales/" + id + "/refund", {
      method: "POST",
      body: JSON.stringify({
        idempotency_key: crypto.randomUUID(),
        reason,
        method: "cash",
      }),
    }),
  inventory: () => request<StockSummary>("/inventory/summary"),
  reports: () => request<ReportSummary>("/reports/summary"),
  updateProduct: (
    id: number,
    patch: Partial<
      Pick<Product, "name" | "selling_price" | "brand" | "reorder_level" | "cost_price">
    >,
  ) =>
    request<Product>("/products/" + id, {
      method: "PATCH",
      body: JSON.stringify(patch),
    }),
  deactivateProduct: async (id: number) => {
    const response = await fetch(API_BASE + "/products/" + id, { method: "DELETE" });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || "Product could not be deactivated");
    }
  },
  adjustStock: (id: number, delta: string, note: string) =>
    request("/inventory/products/" + id + "/adjustments", {
      method: "POST",
      body: JSON.stringify({ quantity_delta: delta, note }),
    }),
  createProduct: (product: Omit<Product, "id" | "is_active">) =>
    request<Product>("/products", {
      method: "POST",
      body: JSON.stringify(product),
    }),
  health: () =>
    fetch("http://127.0.0.1:8000/health").then((r) => r.json()) as Promise<{
      status: string;
      database: string;
    }>,
};
