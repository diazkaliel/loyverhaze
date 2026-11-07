import {useEffect,useMemo,useState,type FormEvent} from 'react';
import {Plus,RefreshCw} from 'lucide-react';
import {api,type StockMovement,type StockRow,type StockMovementInput} from '../api';

type Props={organizationId:string|null;canWrite:boolean;view:'stock'|'movements'};
export function InventoryManagement({organizationId,canWrite,view}:Props){
 const [stocks,setStocks]=useState<StockRow[]>([]);
 const [movements,setMovements]=useState<StockMovement[]>([]);
 const [error,setError]=useState('');
 const [loading,setLoading]=useState(true);
 const [showForm,setShowForm]=useState(false);
 const [saving,setSaving]=useState(false);
 const [storeId,setStoreId]=useState('');
 const [itemId,setItemId]=useState('');
 const [reason,setReason]=useState<'receipt'|'adjustment'>('receipt');
 const [quantity,setQuantity]=useState('');
 const [note,setNote]=useState('');
 const [requestKey,setRequestKey]=useState<string>('');
 const items=useMemo(()=>Array.from(new Map(stocks.map(s=>[s.item_id,{id:s.item_id,name:s.item_name}])).values()),[stocks]);
 const stores=useMemo(()=>Array.from(new Map(stocks.filter(s=>s.store_active).map(s=>[s.store_id,{id:s.store_id,name:s.store_name}])).values()),[stocks]);
 async function refresh(){
   setLoading(true);setError('');
   try{const [stockRows,movementRows]=await Promise.all([api.stock(),api.movements()]);setStocks(stockRows);setMovements(movementRows)}
   catch(e){setError(e instanceof Error?e.message:String(e))}
   finally{setLoading(false)}
 }
 useEffect(()=>{void refresh()},[organizationId]);
 function openForm(row?:StockRow){
   const key=crypto.randomUUID();
   setRequestKey(key);setItemId(row?.item_id??items[0]?.id??'');setStoreId(row?.store_id??stores[0]?.id??'');
   setReason('receipt');setQuantity('');setNote('');setError('');setShowForm(true);
 }
 async function submit(e:FormEvent){
   e.preventDefault();setSaving(true);setError('');
   const data:StockMovementInput={item_id:itemId,store_id:storeId,quantity_delta:quantity,reason,note,idempotency_key:requestKey};
   try{await api.createMovement(data);setShowForm(false);await refresh()}
   catch(e){setError(e instanceof Error?e.message:String(e))}
   finally{setSaving(false)}
 }
 return <div className="inventory-management">
   <div className="heading"><div><p className="eyebrow">INVENTARIO</p>
     <h1>{view==='stock'?'Existencias por sucursal':'Movimientos de inventario'}</h1>
     <p className="muted">{view==='stock'?'Disponibilidad actual de los artículos de cada sucursal.':'Historial auditable de entradas y ajustes, ordenado por fecha.'}</p></div>
     {canWrite&&items.length>0&&stores.length>0&&<button className="primary" onClick={()=>openForm()}><Plus size={18}/> Registrar movimiento</button>}
   </div>
   {error&&!showForm&&<div className="error" role="alert">{error}</div>}
   <div className="toolbar"><span>{loading?'Cargando…':view==='stock'?`${stocks.length} existencias`:`${movements.length} movimientos (últimos 200)`}</span>
      <button onClick={()=>void refresh()} disabled={loading}><RefreshCw size={16}/> Actualizar</button></div>
   <div className="table-wrap"><table><thead><tr>{view==='stock'?<><th>Artículo</th><th>REF (SKU)</th><th>Sucursal</th><th>Existencias</th></>:<><th>Fecha</th><th>Artículo</th><th>Sucursal</th><th>Tipo</th><th>Cambio</th><th>Resultado</th><th>Usuario</th></>}</tr></thead><tbody>
    {view==='stock'?stocks.map(r=><tr key={r.item_id+'-'+r.store_id}><td>{canWrite&&r.store_active?<button className="table-link" onClick={()=>openForm(r)}>{r.item_name}</button>:r.item_name}</td><td>{r.sku}</td><td>{r.store_name}{!r.store_active?' (Inactiva)':''}</td><td><strong>{r.quantity}</strong></td></tr>):
    movements.map(m=><tr key={m.id}><td>{new Date(m.created_at).toLocaleString('es-CL')}</td><td>{m.item_name}</td><td>{m.store_name}</td><td>{m.reason==='receipt'?'Entrada':m.reason==='sale'?'Venta':'Ajuste'}</td><td>{m.quantity_delta}</td><td>{m.resulting_quantity}</td><td>{m.username}</td></tr>)}
   </tbody></table>{!loading&&(view==='stock'?stocks.length:movements.length)===0&&<div className="empty">No hay registros. Para iniciar el inventario, crea artículos y sucursales.</div>}</div>
   {showForm&&<div className="overlay"><form className="dialog" onSubmit={e=>void submit(e)}><h2>Registrar movimiento de stock</h2>
     {error&&<div className="error" role="alert">{error}</div>}
     <label>Artículo<select required value={itemId} onChange={e=>setItemId(e.target.value)}>{items.map(i=><option key={i.id} value={i.id}>{i.name}</option>)}</select></label>
     <label>Sucursal<select required value={storeId} onChange={e=>setStoreId(e.target.value)}>{stores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>
     <label>Tipo<select value={reason} onChange={e=>setReason(e.target.value as 'receipt'|'adjustment')}><option value="receipt">Entrada</option><option value="adjustment">Ajuste (+/-)</option></select></label>
     <label>Cantidad {reason==='adjustment'?'(positiva o negativa)':'(positiva)'}<input type="number" required step="0.001" min={reason==='receipt'?'0.001':undefined} value={quantity} onChange={e=>setQuantity(e.target.value)}/></label>
     <label>Motivo / observaciones<input maxLength={300} value={note} onChange={e=>setNote(e.target.value)}/></label>
     <p className="muted">El registro no se puede modificar después de guardarlo. Una corrección debe realizarse con otro movimiento.</p>
     <div className="actions"><button type="button" onClick={()=>setShowForm(false)} disabled={saving}>Cancelar</button><button className="primary" type="submit" disabled={saving}>{saving?'Guardando…':'Registrar'}</button></div>
   </form></div>}
 </div>;
}
