import { useEffect, useMemo, useState, useRef } from "react";
import {
  Barcode,
  Boxes,
  ChartNoAxesCombined,
  CircleAlert,
  ClipboardList,
  CloudOff,
  Mic,
  PackagePlus,
  Plus,
  Search,
  ShoppingCart,
  Store,
  Trash2,
  X,
  Minus,
  ReceiptText,
  CircleHelp,
  Command,
} from "lucide-react";
import { api, type Product, type ImportPreview, type Sale, type StockSummary, type ReportSummary } from "./lib/api";

type CartLine = { product: Product; quantity: number };
const categories = [
  "All items",
  "Staples",
  "Dairy",
  "Snacks",
  "Beverages",
  "Personal care",
  "Household",
];
function categoryFor(product: Product) {
  const value = product.name.toLowerCase();
  if (/milk|curd|paneer|butter|cheese|ghee|yogurt/.test(value)) return "Dairy";
  if (/biscuit|chips|namkeen|chocolate|wafer|snack/.test(value))
    return "Snacks";
  if (/juice|water|cola|drink|tea|coffee/.test(value)) return "Beverages";
  if (/soap|shampoo|toothpaste|brush|cream/.test(value)) return "Personal care";
  if (/clean|detergent|phenyl|dishwash|floor/.test(value)) return "Household";
  return "Staples";
}
const money = (value: number) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState<"sale"|"stock"|"sales"|"reports">("sale");
  const [sales, setSales] = useState<Sale[]>([]);
  const [inventory, setInventory] = useState<StockSummary | null>(null);
  const [reports, setReports] = useState<ReportSummary | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<"cash"|"upi"|"card"|"other">("cash");
  const [lastSale, setLastSale] = useState<Sale | null>(null);
  const [checkoutBusy, setCheckoutBusy] = useState(false);
  const [recording, setRecording] = useState(false);
  const [voiceBusy, setVoiceBusy] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const [voiceResult, setVoiceResult] = useState<{transcript:string;items:{product_id:number;name:string;quantity:string;unit:string;selling_price:string;confidence:number}[]}|null>(null);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All items");
  const [health, setHealth] = useState("Checking");
  const [error, setError] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [stockMode, setStockMode] = useState<"replace" | "add">("replace");
  const [importBusy, setImportBusy] = useState(false);
  const [name, setName] = useState("");
  const [sku, setSku] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");

  async function refresh() {
    try {
      const result = await Promise.all([api.products(), api.health()]);
      setProducts(result[0]);
      setHealth(result[1].database === "connected" ? "Connected" : "Degraded");
      setError("");
    } catch (e) {
      setHealth("Offline");
      setError(
        e instanceof Error
          ? e.message
          : "Could not connect to the local service",
      );
    }
  }
  useEffect(() => { void refresh(); }, []);
  useEffect(() => {
    if (page === "stock") void api.inventory().then(setInventory).catch(e => setError(e.message));
    if (page === "sales") void api.sales().then(setSales).catch(e => setError(e.message));
    if (page === "reports") void api.reports().then(setReports).catch(e => setError(e.message));
  }, [page]);
  const filtered = useMemo(
    () =>
      products.filter((product) => {
        const matches = (
          product.name +
          " " +
          product.sku +
          " " +
          (product.brand || "")
        )
          .toLowerCase()
          .includes(search.toLowerCase());
        return (
          matches &&
          (category === "All items" || categoryFor(product) === category)
        );
      }),
    [products, search, category],
  );
  const subtotal = cart.reduce(
    (sum, line) => sum + Number(line.product.selling_price) * line.quantity,
    0,
  );
  const itemCount = cart.reduce((sum, line) => sum + line.quantity, 0);
  const taxTotal = cart.reduce((sum,line) => sum + Number(line.product.selling_price) * line.quantity * Number(line.product.tax_rate || 0) / 100, 0);
  const amountDue = subtotal + taxTotal;

  function add(product: Product) {
    setCart((current) => {
      const found = current.find((line) => line.product.id === product.id);
      return found
        ? current.map((line) =>
            line.product.id === product.id
              ? { ...line, quantity: line.quantity + 1 }
              : line,
          )
        : [...current, { product, quantity: 1 }];
    });
  }
  function changeQty(id: number, delta: number) {
    setCart((current) =>
      current
        .map((line) =>
          line.product.id === id
            ? { ...line, quantity: line.quantity + delta }
            : line,
        )
        .filter((line) => line.quantity > 0),
    );
  }
  async function saveProduct(event: React.FormEvent) {
    event.preventDefault();
    try {
      await api.createProduct({
        sku,
        name,
        selling_price: price,
        stock_quantity: stock,
        stock_unit: "piece",
        sale_unit: "piece",
      });
      setShowAdd(false);
      setName("");
      setSku("");
      setPrice("");
      setStock("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save product");
    }
  }

  return (
    <div className="pos-app">
      <aside className="rail">
        <div className="rail-brand">
          <span className="brand-symbol">
            <Store size={19} />
          </span>
          <span>SV</span>
        </div>
        <div className="rail-rule" />
        <button className={page === "sale" ? "rail-link selected" : "rail-link"} title="Point of sale" onClick={() => setPage("sale")}>
          <ShoppingCart size={19} />
          <small>Sale</small>
        </button>
        <button className={page === "stock" ? "rail-link selected" : "rail-link"} title="Inventory" onClick={() => setPage("stock")}>
          <Boxes size={19} />
          <small>Stock</small>
        </button>
        <button className={page === "sales" ? "rail-link selected" : "rail-link"} title="Sales history" onClick={() => setPage("sales")}>
          <ClipboardList size={19} />
          <small>Sales</small>
        </button>
        <button className={page === "reports" ? "rail-link selected" : "rail-link"} title="Reports" onClick={() => setPage("reports")}>
          <ChartNoAxesCombined size={19} />
          <small>Reports</small>
        </button>
        <div className="rail-spacer" />
        <button className="rail-link" title="Help">
          <CircleHelp size={18} />
          <small>Help</small>
        </button>
        <div className="rail-user">RG</div>
      </aside>
      <main className="pos-main">
        <header className="store-header">
          <div className="store-heading">
            <div className="store-overline">SMARTVOICE / RETAIL</div>
            <h1>
              Counter <span>01</span>
            </h1>
          </div>
          <div className="header-right">
            <div
              className={
                "service-state " +
                (health === "Connected" ? "is-online" : "is-warn")
              }
            >
              <i />{" "}
              {health === "Connected"
                ? "Local system ready"
                : health === "Checking"
                  ? "Connecting…"
                  : health}
            </div>
            <div className="date-stamp">REGISTER · MAIN STORE</div>
          </div>
        </header>
        {error && (
          <div className="error-strip">
            <CircleAlert size={15} />
            {error}
            <button onClick={() => void refresh()}>Try again</button>
          </div>
        )}
        <div className="pos-layout" style={{display:page === "sale" ? "grid" : "none"}}>
          <section className="browse-area">
            <div className="section-heading">
              <div>
                <div className="section-kicker">PRODUCTS</div>
                <h2>What are we selling?</h2>
              </div>
              <div className="heading-actions">
                <button
                  className="outline-action"
                  onClick={() => {
                    setPreview(null);
                    setShowImport(true);
                  }}
                >
                  <Boxes size={15} /> Import sheet
                </button>
                <button
                  className="outline-action"
                  onClick={() => setShowAdd(true)}
                >
                  <PackagePlus size={16} /> New item
                </button>
              </div>
            </div>
            <div className="search-row">
              <Search size={18} />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Scan barcode or search product name…"
              />
              <kbd>
                <Command size={11} /> K
              </kbd>
            </div>
            <div className="category-strip">
              {categories.map((item) => (
                <button
                  key={item}
                  className={
                    category === item ? "category-tab active" : "category-tab"
                  }
                  onClick={() => setCategory(item)}
                >
                  {item}
                </button>
              ))}
            </div>
            <div className="catalog-meta">
              <span>{filtered.length} ITEMS FOUND</span>
              <span>SELECT AN ITEM TO ADD TO BILL</span>
            </div>
            <div className="product-grid">
              {filtered.map((product, index) => (
                <button
                  className="product-tile"
                  key={product.id}
                  onClick={() => add(product)}
                >
                  <span className={"tile-mark mark-" + (index % 5)}>
                    <Barcode size={21} />
                  </span>
                  <span className="tile-copy">
                    <b>{product.name}</b>
                    <small>
                      {product.sku} · {product.stock_quantity}{" "}
                      {product.stock_unit}
                    </small>
                  </span>
                  <span className="tile-bottom">
                    <strong>{money(Number(product.selling_price))}</strong>
                    <i>
                      <Plus size={15} />
                    </i>
                  </span>
                </button>
              ))}
              {filtered.length === 0 && (
                <div className="catalog-empty">
                  <div className="empty-mark">
                    <Boxes size={23} />
                  </div>
                  <b>
                    {products.length === 0
                      ? "Your product shelf is empty"
                      : "No matching products"}
                  </b>
                  <span>
                    {products.length === 0
                      ? "Add your first item or import your stock list."
                      : "Try another search or category."}
                  </span>
                  {products.length === 0 && (
                    <button onClick={() => setShowAdd(true)}>
                      Add first product
                    </button>
                  )}
                </div>
              )}
            </div>
            <div className="catalog-footer">
              <span>
                <span className="key-dot" /> LOCAL CATALOGUE
              </span>
              <span>PRICES IN INR</span>
            </div>
          </section>
          <aside className="bill-panel">
            <div className="bill-topline">
              <div>
                <div className="section-kicker">CURRENT TRANSACTION</div>
                <h2>New sale</h2>
              </div>
              <span className="bill-status">DRAFT</span>
            </div>
            <div className="bill-reference">
              <span>RECEIPT NO.</span>
              <b>NEW · AUTO ASSIGNED</b>
              <span className="bill-clock">COUNTER 01</span>
            </div>
            <div className="bill-column-head">
              <span>ITEM / DESCRIPTION</span>
              <span>QTY</span>
              <span>AMOUNT</span>
            </div>
            <div className="bill-items">
              {cart.map((line) => (
                <div className="bill-line" key={line.product.id}>
                  <div className="bill-item-name">
                    <b>{line.product.name}</b>
                    <small>
                      {money(Number(line.product.selling_price))} /{" "}
                      {line.product.sale_unit}
                    </small>
                  </div>
                  <div className="bill-qty">
                    <button
                      onClick={() => changeQty(line.product.id, -1)}
                      aria-label="Decrease quantity"
                    >
                      <Minus size={12} />
                    </button>
                    <span>{line.quantity}</span>
                    <button
                      onClick={() => changeQty(line.product.id, 1)}
                      aria-label="Increase quantity"
                    >
                      <Plus size={12} />
                    </button>
                  </div>
                  <strong>
                    {money(Number(line.product.selling_price) * line.quantity)}
                  </strong>
                </div>
              ))}
              {cart.length === 0 && (
                <div className="bill-empty">
                  <ReceiptText size={25} />
                  <b>No items yet</b>
                  <span>Choose products from the list to build this bill.</span>
                </div>
              )}
            </div>
            <div className="bill-calculation">
              <div>
                <span>Items</span>
                <b>{itemCount}</b>
              </div>
              <div>
                <span>Subtotal</span>
                <b>{money(subtotal)}</b>
              </div>
              <div>
                <span>Tax</span>
                <b>{money(taxTotal)}</b>
              </div>
              <div className="bill-total">
                <span>Amount due</span>
                <strong>{money(amountDue)}</strong>
              </div>
            </div>
            <button className="charge-button" disabled={cart.length === 0 || checkoutBusy || health !== "Connected"} onClick={async () => { setCheckoutBusy(true); try { const sale = await api.checkout({idempotency_key:crypto.randomUUID(),payment_method:paymentMethod,discount:"0",items:cart.map(line=>({product_id:line.product.id,quantity:line.quantity}))}); setLastSale(sale); setCart([]); await refresh(); } catch(e) { setError(e instanceof Error ? e.message : "Checkout failed"); } finally { setCheckoutBusy(false); } }}>
              <span>{checkoutBusy ? "Processing…" : "Take payment"}</span>
              <b>{money(subtotal)}</b>
            </button>
            <div className="payment-method"><label>Payment<select value={paymentMethod} onChange={event=>setPaymentMethod(event.target.value as "cash"|"upi"|"card"|"other")}><option value="cash">Cash</option><option value="upi">UPI</option><option value="card">Card</option><option value="other">Other</option></select></label></div>
            <div className="bill-actions">
              <button onClick={() => setCart([])} disabled={cart.length === 0}>
                <Trash2 size={14} /> Clear bill
              </button>
              <button disabled>
                <ReceiptText size={14} /> Save draft
              </button>
            </div>
            <div className="bill-footnote">
              <CloudOff size={13} /> Your register works locally. Checkout is
              being connected.
            </div>
          </aside>
        </div>

        {page !== "sale" && <section className="module-page">
          <div className="section-kicker">{page === "stock" ? "INVENTORY CONTROL" : page === "sales" ? "TRANSACTION LEDGER" : "STORE PERFORMANCE"}</div>
          <h2>{page === "stock" ? "Stock on hand" : page === "sales" ? "Sales history" : "Reports overview"}</h2>
          {page === "stock" && inventory && <><div className="module-stats"><div><small>ACTIVE PRODUCTS</small><b>{inventory.product_count}</b></div><div><small>LOW STOCK ITEMS</small><b>{inventory.low_stock_count}</b></div></div><div className="data-table"><div className="data-head"><span>PRODUCT</span><span>SKU</span><span>ON HAND</span><span>PRICE</span><span>STATUS</span></div>{inventory.products.map(p=><div className="data-row" key={p.id}><b>{p.name}</b><span>{p.sku}</span><span>{p.stock_quantity} {p.stock_unit}</span><span>{money(Number(p.selling_price))}</span><span>{Number(p.stock_quantity)<=0?"Out of stock":Number(p.stock_quantity)<=Number(p.reorder_level)?"Reorder":"In stock"}</span><button className="table-action" onClick={async()=>{const newName=window.prompt("Product name:",p.name);if(newName===null||!newName.trim())return;const newPrice=window.prompt("Selling price (₹):",String(p.selling_price));if(newPrice===null||!newPrice.trim())return;try{await api.updateProduct(p.id,{name:newName.trim(),selling_price:newPrice});setInventory(await api.inventory());await refresh();}catch(e){setError(e instanceof Error?e.message:"Product update failed");}}}>Edit</button><button className="table-action" onClick={async()=>{const value=window.prompt("Enter stock change (use a negative number to remove stock):");if(value===null||!value.trim())return;try{await api.adjustStock(p.id,value,"Manual adjustment from Stock screen");setInventory(await api.inventory());await refresh();}catch(e){setError(e instanceof Error?e.message:"Stock adjustment failed");}}}>Adjust</button></div>)}</div></>}
          {page === "sales" && <div className="data-table"><div className="data-head"><span>RECEIPT</span><span>DATE</span><span>ITEMS</span><span>PAYMENT</span><span>TOTAL</span></div>{sales.map(sale=><div className="data-row clickable-row" key={sale.id} onClick={()=>setLastSale(sale)} title="Open receipt details"><b>{sale.receipt_number}</b><span>{new Date(sale.created_at).toLocaleString()}</span><span>{sale.items.length}</span><span>{sale.payment_method.toUpperCase()}</span><b>{money(Number(sale.grand_total))}</b><button className="table-action" onClick={async event=>{event.stopPropagation();if(!window.confirm("Refund this entire sale and restore its stock?"))return;const reason=window.prompt("Reason for refund:");if(!reason)return;try{await api.refund(sale.id,reason);setSales(await api.sales());setInventory(await api.inventory().catch(()=>null));}catch(e){setError(e instanceof Error?e.message:"Refund failed");}}} disabled={sale.status!=="completed"}>Refund</button></div>)}{sales.length===0&&<p className="module-empty">No completed sales yet.</p>}</div>}
          {page === "reports" && reports && <div className="module-stats"><div><small>TODAY'S REVENUE</small><b>{money(Number(reports.today_revenue))}</b><span>{reports.today_sales_count} transactions</span></div><div><small>ALL-TIME REVENUE</small><b>{money(Number(reports.all_time_revenue))}</b><span>{reports.all_time_sales_count} transactions</span></div><div><small>LOW STOCK</small><b>{reports.low_stock_count}</b></div><div><small>INVENTORY UNITS</small><b>{reports.inventory_units}</b></div></div>}
        </section>}
        <footer className="work-footer">
          <div>
            <span className="footer-live" /> LOCAL MODE{" "}
            <span className="footer-divider">/</span> INVENTORY SYNCED FROM THIS
            DEVICE
          </div>
          <div>
            SMARTVOICE POS <b>0.1.0</b>
          </div>
        </footer>
      </main>
      <button
        className="voice-button"
        disabled={voiceBusy || health !== "Connected"}
        onClick={async () => {
          if (recording) { recorderRef.current?.stop(); setRecording(false); return; }
          try {
            const stream = await navigator.mediaDevices.getUserMedia({audio:true});
            const recorder = new MediaRecorder(stream);
            recorderRef.current = recorder;
            audioChunks.current = [];
            recorder.ondataavailable = event => { if (event.data.size) audioChunks.current.push(event.data); };
            recorder.onstop = async () => {
              stream.getTracks().forEach(track => track.stop());
              setVoiceBusy(true);
              try { setVoiceResult(await api.transcribe(new Blob(audioChunks.current,{type:recorder.mimeType || "audio/webm"}))); }
              catch (error) { setError(error instanceof Error ? error.message : "Voice processing failed"); }
              finally { setVoiceBusy(false); }
            };
            recorder.start();
            setRecording(true);
          } catch (error) { setError(error instanceof Error ? error.message : "Microphone permission unavailable"); }
        }}
        title="Push to talk: click to start, click again to stop"
      >
        <Mic size={18} />
        <span>Voice entry</span>
        <small>SOON</small>
      </button>


      {lastSale && <div className="modal-backdrop"><section className="modal receipt-modal"><div className="modal-heading"><div><div className="section-kicker">PAYMENT COMPLETE</div><h3>{lastSale.receipt_number}</h3></div><button className="modal-close" onClick={()=>setLastSale(null)}><X size={18}/></button></div><p>{lastSale.status === "refunded" ? "This sale has been refunded." : "Sale saved. Stock was deducted and payment recorded."}</p><div className="receipt-lines">{lastSale.items.map((item,index)=><div key={index}><span>{item.name_snapshot} × {item.quantity}</span><b>{money(Number(item.line_total))}</b></div>)}</div><div className="receipt-total"><span>Total paid</span><b>{money(Number(lastSale.grand_total))}</b></div><button className="save-product" onClick={()=>window.print()}>Print receipt</button></section></div>}
      {voiceResult && <div className="modal-backdrop"><section className="modal receipt-modal"><div className="modal-heading"><div><div className="section-kicker">VOICE DRAFT · REVIEW REQUIRED</div><h3>Confirm spoken items</h3></div><button className="modal-close" onClick={()=>setVoiceResult(null)}><X size={18}/></button></div><p>{voiceResult.transcript || "No speech detected"}</p><div className="receipt-lines">{voiceResult.items.map((item,index)=><div key={index}><span>{item.name} · {item.quantity} {item.unit}</span><b>{money(Number(item.selling_price)*Number(item.quantity))}</b><button className="outline-action" onClick={()=>{const p=products.find(x=>x.id===item.product_id);if(p){setCart(current=>{const found=current.find(line=>line.product.id===p.id);return found?current.map(line=>line.product.id===p.id?{...line,quantity:line.quantity+Number(item.quantity)}:line):[...current,{product:p,quantity:Number(item.quantity)}]});}}}>Add</button></div>)}</div><button className="save-product" onClick={()=>setVoiceResult(null)}>Done reviewing</button></section></div>}
      {showImport && (
        <div
          className="modal-backdrop"
          onClick={() => {
            if (!importBusy) setShowImport(false);
          }}
        >
          <section
            className="modal import-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-heading">
              <div>
                <div className="section-kicker">STOCK MANAGEMENT</div>
                <h3>Import inventory</h3>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowImport(false)}
                disabled={importBusy}
              >
                <X size={18} />
              </button>
            </div>
            {!preview ? (
              <div className="upload-area">
                <Boxes size={25} />
                <b>Choose your stock spreadsheet</b>
                <span>CSV or Excel (.xlsx). Up to 10 MB.</span>
                <label className="file-pick">
                  Choose file
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xlsm"
                    onChange={async (event) => {
                      const file = event.target.files?.[0];
                      if (!file) return;
                      setImportBusy(true);
                      try {
                        setPreview(await api.previewImport(file));
                        setError("");
                      } catch (e) {
                        setError(
                          e instanceof Error
                            ? e.message
                            : "Import preview failed",
                        );
                      } finally {
                        setImportBusy(false);
                        event.target.value = "";
                      }
                    }}
                  />
                </label>
                <small>
                  Required columns: SKU, product name, selling price.
                </small>
              </div>
            ) : (
              <>
                <div className="import-summary">
                  <b>{preview.filename}</b>
                  <span>
                    {preview.row_count} rows · {preview.valid_count} valid ·{" "}
                    {preview.error_count} errors
                  </span>
                </div>
                <label className="mode-label">
                  How should stock quantities be applied?
                  <select
                    value={stockMode}
                    onChange={(event) =>
                      setStockMode(event.target.value as "replace" | "add")
                    }
                  >
                    <option value="replace">
                      Replace current stock with spreadsheet quantity
                    </option>
                    <option value="add">
                      Add spreadsheet quantity to current stock
                    </option>
                  </select>
                </label>
                <div className="preview-table">
                  <div className="preview-head">
                    <span>ROW / SKU</span>
                    <span>PRODUCT</span>
                    <span>ACTION</span>
                    <span>VALIDATION</span>
                  </div>
                  {preview.rows.slice(0, 80).map((row) => (
                    <div className="preview-row" key={row.row_number}>
                      <span>
                        #{row.row_number} · {row.sku || "—"}
                      </span>
                      <b>{row.name || "Unnamed"}</b>
                      <span>{row.action}</span>
                      <span
                        className={row.errors.length ? "row-error" : "row-ok"}
                      >
                        {row.errors.join(", ") || "Ready"}
                      </span>
                    </div>
                  ))}
                </div>
                {preview.rows.length > 80 && (
                  <small>Showing first 80 rows.</small>
                )}
                <div className="import-actions">
                  <button
                    className="outline-action"
                    disabled={importBusy}
                    onClick={() => setPreview(null)}
                  >
                    Choose another file
                  </button>
                  <button
                    className="save-product"
                    disabled={importBusy || preview.error_count > 0}
                    onClick={async () => {
                      setImportBusy(true);
                      try {
                        await api.commitImport(preview.import_id, stockMode);
                        setShowImport(false);
                        setPreview(null);
                        await refresh();
                      } catch (e) {
                        setError(
                          e instanceof Error
                            ? e.message
                            : "Import could not be committed",
                        );
                      } finally {
                        setImportBusy(false);
                      }
                    }}
                  >
                    {importBusy ? "Importing…" : "Commit import"}
                  </button>
                </div>
              </>
            )}
          </section>
        </div>
      )}
      {showAdd && (
        <div className="modal-backdrop" onClick={() => setShowAdd(false)}>
          <form
            className="modal"
            onSubmit={saveProduct}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-heading">
              <div>
                <div className="section-kicker">PRODUCT CATALOGUE</div>
                <h3>Add a product</h3>
              </div>
              <button
                type="button"
                className="modal-close"
                onClick={() => setShowAdd(false)}
              >
                <X size={18} />
              </button>
            </div>
            <label>
              Product name
              <input
                required
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. Aashirvaad Atta 5kg"
              />
            </label>
            <label>
              SKU / item code
              <input
                required
                value={sku}
                onChange={(event) => setSku(event.target.value)}
                placeholder="e.g. ATT-005"
              />
            </label>
            <div className="form-grid">
              <label>
                Selling price (₹)
                <input
                  required
                  min="0"
                  step="0.01"
                  type="number"
                  value={price}
                  onChange={(event) => setPrice(event.target.value)}
                />
              </label>
              <label>
                Opening stock
                <input
                  required
                  min="0"
                  step="0.001"
                  type="number"
                  value={stock}
                  onChange={(event) => setStock(event.target.value)}
                />
              </label>
            </div>
            <button className="save-product" type="submit">
              <Plus size={16} /> Save product
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
