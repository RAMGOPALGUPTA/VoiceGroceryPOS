import { useEffect, useMemo, useState } from "react";
import { Barcode, Boxes, ChartNoAxesCombined, CircleAlert, ClipboardList, CloudOff, Mic, PackagePlus, Plus, Search, ShoppingCart, Store, Trash2, X, Minus, ReceiptText, CircleHelp, Command } from "lucide-react";
import { api, type Product } from "./lib/api";

type CartLine = { product: Product; quantity: number };
const categories = ["All items", "Staples", "Dairy", "Snacks", "Beverages", "Personal care", "Household"];
function categoryFor(product: Product) {
  const value = product.name.toLowerCase();
  if (/milk|curd|paneer|butter|cheese|ghee|yogurt/.test(value)) return "Dairy";
  if (/biscuit|chips|namkeen|chocolate|wafer|snack/.test(value)) return "Snacks";
  if (/juice|water|cola|drink|tea|coffee/.test(value)) return "Beverages";
  if (/soap|shampoo|toothpaste|brush|cream/.test(value)) return "Personal care";
  if (/clean|detergent|phenyl|dishwash|floor/.test(value)) return "Household";
  return "Staples";
}
const money = (value: number) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value);

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All items");
  const [health, setHealth] = useState("Checking");
  const [error, setError] = useState("");
  const [showAdd, setShowAdd] = useState(false);
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
      setError(e instanceof Error ? e.message : "Could not connect to the local service");
    }
  }
  useEffect(() => { void refresh(); }, []);
  const filtered = useMemo(() => products.filter((product) => {
    const matches = (product.name + " " + product.sku + " " + (product.brand || "")).toLowerCase().includes(search.toLowerCase());
    return matches && (category === "All items" || categoryFor(product) === category);
  }), [products, search, category]);
  const subtotal = cart.reduce((sum, line) => sum + Number(line.product.selling_price) * line.quantity, 0);
  const itemCount = cart.reduce((sum, line) => sum + line.quantity, 0);

  function add(product: Product) {
    setCart((current) => {
      const found = current.find((line) => line.product.id === product.id);
      return found
        ? current.map((line) => line.product.id === product.id ? { ...line, quantity: line.quantity + 1 } : line)
        : [...current, { product, quantity: 1 }];
    });
  }
  function changeQty(id: number, delta: number) {
    setCart((current) => current.map((line) => line.product.id === id ? { ...line, quantity: line.quantity + delta } : line).filter((line) => line.quantity > 0));
  }
  async function saveProduct(event: React.FormEvent) {
    event.preventDefault();
    try {
      await api.createProduct({ sku, name, selling_price: price, stock_quantity: stock, stock_unit: "piece", sale_unit: "piece" });
      setShowAdd(false); setName(""); setSku(""); setPrice(""); setStock("");
      await refresh();
    } catch (e) { setError(e instanceof Error ? e.message : "Could not save product"); }
  }

  return <div className="pos-app">
    <aside className="rail">
      <div className="rail-brand"><span className="brand-symbol"><Store size={19}/></span><span>SV</span></div>
      <div className="rail-rule"/>
      <button className="rail-link selected" title="Point of sale"><ShoppingCart size={19}/><small>Sale</small></button>
      <button className="rail-link" title="Inventory"><Boxes size={19}/><small>Stock</small></button>
      <button className="rail-link" title="Sales history"><ClipboardList size={19}/><small>Sales</small></button>
      <button className="rail-link" title="Reports"><ChartNoAxesCombined size={19}/><small>Reports</small></button>
      <div className="rail-spacer"/>
      <button className="rail-link" title="Help"><CircleHelp size={18}/><small>Help</small></button>
      <div className="rail-user">RG</div>
    </aside>
    <main className="pos-main">
      <header className="store-header">
        <div className="store-heading"><div className="store-overline">SMARTVOICE / RETAIL</div><h1>Counter <span>01</span></h1></div>
        <div className="header-right"><div className={"service-state " + (health === "Connected" ? "is-online" : "is-warn")}><i/> {health === "Connected" ? "Local system ready" : health === "Checking" ? "Connecting…" : health}</div><div className="date-stamp">REGISTER · MAIN STORE</div></div>
      </header>
      {error && <div className="error-strip"><CircleAlert size={15}/>{error}<button onClick={() => void refresh()}>Try again</button></div>}
      <div className="pos-layout">
        <section className="browse-area">
          <div className="section-heading"><div><div className="section-kicker">PRODUCTS</div><h2>What are we selling?</h2></div><button className="outline-action" onClick={() => setShowAdd(true)}><PackagePlus size={16}/> New item</button></div>
          <div className="search-row"><Search size={18}/><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Scan barcode or search product name…"/><kbd><Command size={11}/> K</kbd></div>
          <div className="category-strip">{categories.map((item) => <button key={item} className={category === item ? "category-tab active" : "category-tab"} onClick={() => setCategory(item)}>{item}</button>)}</div>
          <div className="catalog-meta"><span>{filtered.length} ITEMS FOUND</span><span>SELECT AN ITEM TO ADD TO BILL</span></div>
          <div className="product-grid">
            {filtered.map((product, index) => <button className="product-tile" key={product.id} onClick={() => add(product)}>
              <span className={"tile-mark mark-" + (index % 5)}><Barcode size={21}/></span>
              <span className="tile-copy"><b>{product.name}</b><small>{product.sku} · {product.stock_quantity} {product.stock_unit}</small></span>
              <span className="tile-bottom"><strong>{money(Number(product.selling_price))}</strong><i><Plus size={15}/></i></span>
            </button>)}
            {filtered.length === 0 && <div className="catalog-empty"><div className="empty-mark"><Boxes size={23}/></div><b>{products.length === 0 ? "Your product shelf is empty" : "No matching products"}</b><span>{products.length === 0 ? "Add your first item or import your stock list." : "Try another search or category."}</span>{products.length === 0 && <button onClick={() => setShowAdd(true)}>Add first product</button>}</div>}
          </div>
          <div className="catalog-footer"><span><span className="key-dot"/> LOCAL CATALOGUE</span><span>PRICES IN INR</span></div>
        </section>
        <aside className="bill-panel">
          <div className="bill-topline"><div><div className="section-kicker">CURRENT TRANSACTION</div><h2>New sale</h2></div><span className="bill-status">DRAFT</span></div>
          <div className="bill-reference"><span>RECEIPT NO.</span><b>NEW · AUTO ASSIGNED</b><span className="bill-clock">COUNTER 01</span></div>
          <div className="bill-column-head"><span>ITEM / DESCRIPTION</span><span>QTY</span><span>AMOUNT</span></div>
          <div className="bill-items">
            {cart.map((line) => <div className="bill-line" key={line.product.id}><div className="bill-item-name"><b>{line.product.name}</b><small>{money(Number(line.product.selling_price))} / {line.product.sale_unit}</small></div><div className="bill-qty"><button onClick={() => changeQty(line.product.id, -1)} aria-label="Decrease quantity"><Minus size={12}/></button><span>{line.quantity}</span><button onClick={() => changeQty(line.product.id, 1)} aria-label="Increase quantity"><Plus size={12}/></button></div><strong>{money(Number(line.product.selling_price) * line.quantity)}</strong></div>)}
            {cart.length === 0 && <div className="bill-empty"><ReceiptText size={25}/><b>No items yet</b><span>Choose products from the list to build this bill.</span></div>}
          </div>
          <div className="bill-calculation"><div><span>Items</span><b>{itemCount}</b></div><div><span>Subtotal</span><b>{money(subtotal)}</b></div><div><span>Tax</span><b>{money(0)}</b></div><div className="bill-total"><span>Amount due</span><strong>{money(subtotal)}</strong></div></div>
          <button className="charge-button" disabled><span>Take payment</span><b>{money(subtotal)}</b></button>
          <div className="bill-actions"><button onClick={() => setCart([])} disabled={cart.length === 0}><Trash2 size={14}/> Clear bill</button><button disabled><ReceiptText size={14}/> Save draft</button></div>
          <div className="bill-footnote"><CloudOff size={13}/> Your register works locally. Checkout is being connected.</div>
        </aside>
      </div>
      <footer className="work-footer"><div><span className="footer-live"/> LOCAL MODE <span className="footer-divider">/</span> INVENTORY SYNCED FROM THIS DEVICE</div><div>SMARTVOICE POS <b>0.1.0</b></div></footer>
    </main>
    <button className="voice-button" disabled title="Offline voice billing is under development"><Mic size={18}/><span>Voice entry</span><small>SOON</small></button>
    {showAdd && <div className="modal-backdrop" onClick={() => setShowAdd(false)}><form className="modal" onSubmit={saveProduct} onClick={(event) => event.stopPropagation()}>
      <div className="modal-heading"><div><div className="section-kicker">PRODUCT CATALOGUE</div><h3>Add a product</h3></div><button type="button" className="modal-close" onClick={() => setShowAdd(false)}><X size={18}/></button></div>
      <label>Product name<input required value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Aashirvaad Atta 5kg"/></label>
      <label>SKU / item code<input required value={sku} onChange={(event) => setSku(event.target.value)} placeholder="e.g. ATT-005"/></label>
      <div className="form-grid"><label>Selling price (₹)<input required min="0" step="0.01" type="number" value={price} onChange={(event) => setPrice(event.target.value)}/></label><label>Opening stock<input required min="0" step="0.001" type="number" value={stock} onChange={(event) => setStock(event.target.value)}/></label></div>
      <button className="save-product" type="submit"><Plus size={16}/> Save product</button>
    </form></div>}
  </div>;
}
