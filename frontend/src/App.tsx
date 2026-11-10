import { useEffect, useMemo, useState } from 'react';
import { Activity, Barcode, Boxes, ChartNoAxesCombined, CircleAlert, ClipboardList, CloudOff, Mic, PackagePlus, Plus, Search, ShoppingCart, Sparkles, Store, Trash2, Wallet } from 'lucide-react';
import { api, type Product } from './lib/api';

type CartLine = { product: Product; quantity: number };

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [search, setSearch] = useState('');
  const [health, setHealth] = useState('Checking');
  const [error, setError] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState('');
  const [sku, setSku] = useState('');
  const [price, setPrice] = useState('');
  const [stock, setStock] = useState('');

  async function refresh() {
    try { const [items, status] = await Promise.all([api.products(), api.health()]); setProducts(items); setHealth(status.database === 'connected' ? 'Connected' : 'Degraded'); setError(''); }
    catch (e) { setHealth('Offline'); setError(e instanceof Error ? e.message : 'Could not connect to local backend'); }
  }
  useEffect(() => { void refresh(); }, []);
  const filtered = useMemo(() => products.filter(p => `${p.name} ${p.sku} ${p.brand ?? ''}`.toLowerCase().includes(search.toLowerCase())), [products, search]);
  const subtotal = cart.reduce((sum, line) => sum + Number(line.product.selling_price) * line.quantity, 0);
  function add(product: Product) { setCart(current => { const found = current.find(x => x.product.id === product.id); return found ? current.map(x => x.product.id === product.id ? {...x, quantity:x.quantity+1} : x) : [...current, {product, quantity:1}]; }); }
  function changeQty(id:number, delta:number) { setCart(current => current.map(x => x.product.id === id ? {...x, quantity:x.quantity+delta} : x).filter(x => x.quantity > 0)); }
  async function saveProduct(e: React.FormEvent) { e.preventDefault(); try { await api.createProduct({sku,name,selling_price:price,stock_quantity:stock,stock_unit:'piece',sale_unit:'piece'}); setShowAdd(false); setName('');setSku('');setPrice('');setStock(''); await refresh(); } catch(e) { setError(e instanceof Error ? e.message : 'Could not save product'); } }

  return <div className="app-shell">
    <aside className="sidebar"><div className="brand"><div className="brand-mark"><Store size={21}/></div><div><b>SmartVoice</b><small>GROCERY POS</small></div></div><div className="store-chip"><span className="live-dot"/> STORE COUNTER 01</div><nav><span className="nav-label">WORKSPACE</span><a className="active"><ShoppingCart size={17}/> Point of sale</a><a><Boxes size={17}/> Inventory</a><a><ClipboardList size={17}/> Sales history</a><a><ChartNoAxesCombined size={17}/> Reports</a></nav><div className="sidebar-bottom"><div className="offline-card"><CloudOff size={17}/><div><b>Offline-first mode</b><small>Data stays on this device</small></div></div><div className="version">SMARTVOICE POS <span>v0.1.0</span></div></div></aside>
    <main className="main"><header className="topbar"><div><div className="eyebrow">TUESDAY · LOCAL COUNTER</div><h1>Point of sale</h1></div><div className="top-actions"><div className="connection"><span className={health==='Connected'?'live-dot':'warn-dot'}/>{health}</div><div className="avatar">RG</div></div></header>
      <section className="welcome"><div><div className="welcome-kicker"><Sparkles size={14}/> YOUR COUNTER, SIMPLIFIED</div><h2>Good business starts with a <em>smooth checkout.</em></h2><p>Find products, build a cart, and keep your store moving.</p></div><div className="welcome-icon"><Activity size={38}/></div></section>
      {error && <div className="error-banner"><CircleAlert size={16}/>{error}<button onClick={()=>void refresh()}>Retry</button></div>}
      <section className="stats"><div className="stat-card"><div className="stat-icon blue"><Boxes size={18}/></div><div><small>ACTIVE PRODUCTS</small><strong>{products.length}</strong><span>In your catalogue</span></div></div><div className="stat-card"><div className="stat-icon green"><ShoppingCart size={18}/></div><div><small>CART ITEMS</small><strong>{cart.reduce((s,x)=>s+x.quantity,0)}</strong><span>Current bill</span></div></div><div className="stat-card"><div className="stat-icon amber"><Wallet size={18}/></div><div><small>CURRENT TOTAL</small><strong>₹{subtotal.toFixed(2)}</strong><span>Before checkout</span></div></div></section>
      <div className="workspace"><section className="catalog panel"><div className="panel-head"><div><div className="eyebrow">PRODUCT CATALOGUE</div><h3>Find products</h3></div><button className="primary-btn" onClick={()=>setShowAdd(true)}><PackagePlus size={16}/> Add product</button></div><div className="searchbox"><Search size={17}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by product name, SKU or brand..."/><kbd>⌘ K</kbd></div><div className="product-list">{filtered.map(p=><div className="product-row" key={p.id}><div className="product-thumb"><Barcode size={19}/></div><div className="product-info"><b>{p.name}</b><small>{p.sku} · Stock: {p.stock_quantity} {p.stock_unit}</small></div><div className="product-price">₹{Number(p.selling_price).toFixed(2)}</div><button className="add-btn" onClick={()=>add(p)} aria-label={`Add ${p.name}`}><Plus size={17}/></button></div>)}{filtered.length===0&&<div className="empty-state">{products.length===0?'Your catalogue is waiting for products. Add one to get started.':'No products match your search.'}</div>}</div></section>
      <section className="cart panel"><div className="panel-head"><div><div className="eyebrow">CURRENT ORDER</div><h3>Cart <span className="count-pill">{cart.length}</span></h3></div><button className="icon-btn" onClick={()=>setCart([])} title="Clear cart"><Trash2 size={16}/></button></div><div className="cart-lines">{cart.map(line=><div className="cart-line" key={line.product.id}><div className="line-main"><b>{line.product.name}</b><small>₹{Number(line.product.selling_price).toFixed(2)} / {line.product.sale_unit}</small></div><div className="qty-control"><button onClick={()=>changeQty(line.product.id,-1)}>−</button><span>{line.quantity}</span><button onClick={()=>changeQty(line.product.id,1)}>+</button></div><b className="line-total">₹{(Number(line.product.selling_price)*line.quantity).toFixed(2)}</b></div>)}{cart.length===0&&<div className="cart-empty"><div><ShoppingCart size={25}/></div><b>Your cart is empty</b><span>Add products from the catalogue to begin.</span></div>}</div><div className="bill-summary"><div><span>Subtotal</span><b>₹{subtotal.toFixed(2)}</b></div><div><span>Tax</span><b>₹0.00</b></div><div className="grand-total"><span>Total payable</span><strong>₹{subtotal.toFixed(2)}</strong></div><button className="checkout-btn" disabled>Checkout <span>Coming in billing module</span></button><p className="safe-note">Prices and stock will be revalidated at checkout.</p></div></section></div>
    </main>
    {showAdd&&<div className="modal-backdrop" onClick={()=>setShowAdd(false)}><form className="modal" onSubmit={saveProduct} onClick={e=>e.stopPropagation()}><div className="panel-head"><div><div className="eyebrow">CATALOGUE</div><h3>Add product</h3></div><button type="button" className="icon-btn" onClick={()=>setShowAdd(false)}>×</button></div><label>Product name<input required value={name} onChange={e=>setName(e.target.value)} placeholder="e.g. Aashirvaad Atta 5kg"/></label><label>SKU<input required value={sku} onChange={e=>setSku(e.target.value)} placeholder="e.g. ATT-005"/></label><div className="form-grid"><label>Selling price (₹)<input required min="0" step="0.01" type="number" value={price} onChange={e=>setPrice(e.target.value)}/></label><label>Opening stock<input required min="0" step="0.001" type="number" value={stock} onChange={e=>setStock(e.target.value)}/></label></div><button className="primary-btn full" type="submit"><Plus size={16}/> Save product</button></form></div>}
    <button className="voice-fab" title="Voice billing will be enabled with the offline speech module" disabled><Mic size={20}/><span>VOICE</span></button>
  </div>;
}
