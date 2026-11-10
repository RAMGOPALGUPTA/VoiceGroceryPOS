export const API_BASE = 'http://127.0.0.1:8000/api/v1';

export type Product = { id: number; sku: string; name: string; brand?: string | null; selling_price: string | number; stock_quantity: string | number; stock_unit: string; sale_unit: string; is_active: boolean };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export type ImportRow = { row_number:number; sku?:string|null; name?:string|null; selling_price?:string|null; stock_quantity?:string|null; action:string; errors:string[] };
export type ImportPreview = { import_id:string; filename:string; row_count:number; valid_count:number; error_count:number; rows:ImportRow[]; stock_modes:string[] };
export const api = {
  previewImport: async (file: File) => {
    const body = new FormData();
    body.append("file", file);
    const response = await fetch("http://127.0.0.1:8000/api/v1/inventory/import/preview", { method:"POST", body });
    if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(data.detail || "Import preview failed"); }
    return response.json() as Promise<ImportPreview>;
  },
  commitImport: (id:string, mode:"replace"|"add") => request<{status:string;processed_rows:number}>(`/inventory/import/${id}/commit?stock_mode=${mode}`, { method:"POST" }),
  products: () => request<Product[]>('/products'),
  createProduct: (product: Omit<Product, 'id' | 'is_active'>) => request<Product>('/products', { method: 'POST', body: JSON.stringify(product) }),
  health: () => fetch('http://127.0.0.1:8000/health').then(r => r.json()) as Promise<{status:string;database:string}>,
};
