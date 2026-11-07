import {useEffect,useMemo,useState} from 'react';
import {Search,Plus,Minus,Trash2,ShoppingBag,CheckCircle2} from 'lucide-react';
import {api,type Item,type Category,type StockRow,type Store,type Sale,type CheckoutInput} from '../api';

type CartLine={item:Item;quantity:number};
const money=(value:string|number)=>new Intl.NumberFormat('es-CL',{minimumFractionDigits:2,maximumFractionDigits:2}).format(Number(value));
export function PointOfSale({organizationId}:{organizationId:string|null}){
 const [items,setItems]=useState<Item[]>([]);
 const [categories,setCategories]=useState<Category[]>([]);
 const [stock,setStock]=useState<StockRow[]>([]);
 const [stores,setStores]=useState<Store[]>([]);
 const [storeId,setStoreId]=useState('');
 const [search,setSearch]=useState('');
 const [category,setCategory]=useState('');
 const [cart,setCart]=useState<CartLine[]>([]);
 const [cash,setCash]=useState('');
 const [paying,setPaying]=useState(false);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const [sale,setSale]=useState<Sale|null>(null);
 const [requestKey,setRequestKey]=useState('');
 useEffect(()=>{let active=true;Promise.all([api.items(),api.categories(),api.stock(),api.stores()]).then(([i,c,b,s])=>{
    if(!active)return;setItems(i);setCategories(c);setStock(b);setStores(s.filter(x=>x.is_active));
    setStoreId(prev=>s.some(x=>x.is_active&&x.id===prev)?prev:(s.find(x=>x.is_active)?.id??''));
    setCart([]);setSale(null);setPaying(false);setError('');
 }).catch(e=>{if(active)setError(String(e))});return()=>{active=false}},[organizationId]);
 const available=items.filter(x=>x.available_for_sale&&(category===''||x.category===category)&&
   (x.name.toLocaleLowerCase().includes(search.toLocaleLowerCase())||x.sku.toLocaleLowerCase().includes(search.toLocaleLowerCase())));
 const qtyAvailable=(id:string)=>Number(stock.find(x=>x.item_id===id&&x.store_id===storeId)?.quantity??0);
 const totalCents=useMemo(()=>cart.reduce((sum,x)=>sum+Math.round(Number(x.item.price)*100)*x.quantity,0),[cart]);
 const total=(totalCents/100).toFixed(2);
 function adjust(item:Item,delta:number){
   if(!storeId)return;
   setError('');
   setCart(prev=>{const existing=prev.find(x=>x.item.id===item.id);
     const next=(existing?.quantity??0)+delta;
     if(next<0||next>qtyAvailable(item.id))return prev;
     if(next===0)return prev.filter(x=>x.item.id!==item.id);
     return existing?prev.map(x=>x.item.id===item.id?{...x,quantity:next}:x):[...prev,{item,quantity:next}];
   });
 }
 function startPay(){setError('');setCash(total);setRequestKey(crypto.randomUUID());setPaying(true)}
 async function checkout(){
   if(!storeId||cart.length===0||busy)return;
   setBusy(true);setError('');
   const payload:CheckoutInput={store_id:storeId,idempotency_key:requestKey,payment_method:'cash',
     cash_received:cash,lines:cart.map(x=>({item_id:x.item.id,quantity:x.quantity.toFixed(3)}))};
   try{
     const receipt=await api.checkout(payload);
     setSale(receipt);setPaying(false);setCart([]);setStock(await api.stock());
   }catch(e){setError(e instanceof Error?e.message:String(e))}
   finally{setBusy(false)}
 }
 return <div className="pos-page">
  <div className="pos-workspace">
   <div className="pos-catalog">
    <div className="pos-topbar"><div><p className="eyebrow">PUNTO DE VENTA</p><h1>Ventas</h1></div>
      <label>Sucursal<select aria-label="Sucursal de venta" value={storeId} onChange={e=>{setStoreId(e.target.value);setCart([]);setError('')}}>
       {stores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label></div>
    <div className="pos-filters"><label className="search-field"><Search size={17}/><input placeholder="Buscar nombre o SKU" value={search} onChange={e=>setSearch(e.target.value)}/></label>
      <select aria-label="Categoría" value={category} onChange={e=>setCategory(e.target.value)}><option value="">Todos los artículos</option>{categories.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></div>
    {error&&!paying&&<div className="error" role="alert">{error}</div>}
    <div className="pos-grid">{available.map(item=><button className="pos-product" key={item.id} disabled={!storeId||qtyAvailable(item.id)<1} onClick={()=>adjust(item,1)}>
        <span className="pos-product-icon"><ShoppingBag size={24}/></span><strong>{item.name}</strong><small>{item.sku}</small>
        <span className="pos-product-bottom"><b>{money(item.price)}</b><small>Stock {qtyAvailable(item.id)}</small></span>
      </button>)}</div>
    {available.length===0&&<div className="empty">No se encontraron artículos disponibles.</div>}
   </div>
   <aside className="pos-ticket"><div className="pos-ticket-header"><h2>Ticket actual</h2><button title="Limpiar ticket" disabled={cart.length===0} onClick={()=>setCart([])}><Trash2 size={18}/></button></div>
    <div className="pos-lines">{cart.length===0?<div className="pos-empty">Selecciona artículos para comenzar una venta.</div>:
     cart.map(line=><div className="pos-line" key={line.item.id}><div><strong>{line.item.name}</strong><small>{money(line.item.price)} × {line.quantity}</small></div>
       <div className="pos-quantity"><button aria-label={`Restar ${line.item.name}`} onClick={()=>adjust(line.item,-1)}><Minus size={14}/></button><span>{line.quantity}</span>
         <button aria-label={`Sumar ${line.item.name}`} disabled={line.quantity>=qtyAvailable(line.item.id)} onClick={()=>adjust(line.item,1)}><Plus size={14}/></button></div>
       <b>{money(line.quantity*Number(line.item.price))}</b></div>)}</div>
    <div className="pos-footer"><div className="pos-total"><span>Total</span><strong>{money(total)}</strong></div>
     <button className="primary pos-charge" disabled={cart.length===0||!storeId} onClick={startPay}>Cobrar · {money(total)}</button></div>
   </aside>
  </div>
  {paying&&<div className="overlay"><div className="dialog"><h2>Cobrar en efectivo</h2><p className="muted">Total a cobrar: <strong>{money(total)}</strong></p>
   <label>Efectivo recibido<input type="number" min={total} step="0.01" value={cash} onChange={e=>{setCash(e.target.value);setError('')}}/></label>
   {error&&<div className="error" role="alert">{error}</div>}
   <div className="actions"><button disabled={busy} onClick={()=>setPaying(false)}>Cancelar</button>
     <button className="primary" disabled={busy||Number(cash)<Number(total)} onClick={()=>void checkout()}>{busy?'Procesando…':'Confirmar cobro'}</button></div>
  </div></div>}
  {sale&&<div className="overlay"><div className="dialog pos-success"><CheckCircle2 size={44} color="#17a572"/><h2>Venta registrada</h2>
    <p>Ticket {sale.id.slice(0,8).toUpperCase()}</p><div className="pos-success-values"><span>Total pagado <strong>{money(sale.total)}</strong></span>
    <span>Cambio <strong>{money(sale.change_due)}</strong></span></div>
    <button className="primary pos-charge" onClick={()=>setSale(null)}>Nueva venta</button></div></div>}
 </div>
}
