import {useEffect,useState,type FormEvent} from 'react';
import {Plus,RefreshCw} from 'lucide-react';
import {api,type CashShift,type CashMovement,type Store} from '../api';

type Action={kind:'open'|'close'|'in'|'out';shift?:CashShift};
export function CashManagement({organizationId,role}:{organizationId:string|null;role:string}){
 const [shifts,setShifts]=useState<CashShift[]>([]);
 const [movements,setMovements]=useState<CashMovement[]>([]);
 const [stores,setStores]=useState<Store[]>([]);
 const [loading,setLoading]=useState(true);
 const [saving,setSaving]=useState(false);
 const [error,setError]=useState('');
 const [action,setAction]=useState<Action|null>(null);
 const [storeId,setStoreId]=useState('');
 const [amount,setAmount]=useState('');
 const [note,setNote]=useState('');
 const canClose=role==='owner'||role==='manager';
 async function refresh(){setLoading(true);setError('');try{
   const [s,m,st]=await Promise.all([api.cashShifts(),api.cashMovements(),api.stores()]);
   setShifts(s);setMovements(m);setStores(st.filter(x=>x.is_active));
 }catch(e){setError(e instanceof Error?e.message:String(e))}finally{setLoading(false)}}
 useEffect(()=>{void refresh()},[organizationId]);
 const open=shifts.filter(x=>x.status==='open');
 function begin(kind:Action['kind'],shift?:CashShift){setAction({kind,shift});setError('');setAmount(kind==='close'?shift?.expected_amount??'':'');setNote('');setStoreId(stores.find(s=>!open.some(x=>x.store===s.id))?.id??'')}
 async function submit(e:FormEvent){e.preventDefault();if(!action)return;setSaving(true);setError('');try{
   if(action.kind==='open')await api.openShift(storeId,amount);
   else if(action.kind==='close'&&action.shift)await api.closeShift(action.shift.id,amount);
   else if(action.shift)await api.cashMovement(action.shift.id,action.kind,amount,note);
   setAction(null);await refresh()
 }catch(e){setError(e instanceof Error?e.message:String(e))}finally{setSaving(false)}}
 return <div className="cash-page">
   <div className="heading"><div><p className="eyebrow">CAJA REGISTRADORA</p><h1>Turnos y efectivo</h1>
     <p className="muted">Abre un turno, registra movimientos y concilia el efectivo al cerrar.</p></div>
     {stores.some(s=>!open.some(x=>x.store===s.id))&&<button className="primary" onClick={()=>begin('open')}><Plus size={17}/> Abrir caja</button>}
   </div>
   {error&&!action&&<div className="error" role="alert">{error}</div>}
   <div className="toolbar"><span>{loading?'Cargando…':`${open.length} cajas abiertas`}</span><button onClick={()=>void refresh()} disabled={loading}><RefreshCw size={16}/> Actualizar</button></div>
   <div className="table-wrap"><table><thead><tr><th>Sucursal</th><th>Estado</th><th>Apertura</th><th>Esperado</th><th>Contado</th><th>Diferencia</th><th>Acciones</th></tr></thead><tbody>
     {shifts.map(s=><tr key={s.id}><td>{s.store_name}<small className="cash-subtitle">{new Date(s.opened_at).toLocaleString('es-CL')}</small></td><td>{s.status==='open'?'Abierta':'Cerrada'}</td><td>{s.opening_amount}</td><td>{s.expected_amount}</td><td>{s.counted_amount??'—'}</td><td>{s.difference??'—'}</td>
       <td>{s.status==='open'&&<div className="cash-actions"><button onClick={()=>begin('in',s)}>Entrada</button><button onClick={()=>begin('out',s)}>Salida</button>{canClose&&<button onClick={()=>begin('close',s)}>Cerrar</button>}</div>}</td></tr>)}
   </tbody></table>{!loading&&shifts.length===0&&<div className="empty">No hay turnos registrados. Abre una caja para comenzar.</div>}</div>
   <h2 className="cash-heading">Movimientos de efectivo</h2>
   <div className="table-wrap"><table><thead><tr><th>Fecha</th><th>Tipo</th><th>Importe</th><th>Motivo</th><th>Usuario</th></tr></thead><tbody>
     {movements.map(m=><tr key={m.id}><td>{new Date(m.created_at).toLocaleString('es-CL')}</td><td>{m.kind==='in'?'Entrada':'Salida'}</td><td>{m.amount}</td><td>{m.note}</td><td>{m.performed_by_username}</td></tr>)}
   </tbody></table>{!loading&&movements.length===0&&<div className="empty">No hay entradas ni salidas manuales.</div>}</div>
   {action&&<div className="overlay"><form className="dialog" onSubmit={e=>void submit(e)}>
     <h2>{action.kind==='open'?'Abrir caja':action.kind==='close'?'Cerrar caja':action.kind==='in'?'Entrada de efectivo':'Salida de efectivo'}</h2>
     {error&&<div className="error" role="alert">{error}</div>}
     {action.kind==='open'&&<label>Sucursal<select required value={storeId} onChange={e=>setStoreId(e.target.value)}>
       {stores.filter(s=>!open.some(x=>x.store===s.id)).map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></label>}
     {action.shift&&<p className="muted">Sucursal: {action.shift.store_name} · Efectivo esperado: {action.shift.expected_amount}</p>}
     <label>{action.kind==='open'?'Efectivo inicial':action.kind==='close'?'Efectivo contado':'Importe'}<input type="number" required min={action.kind==='in'||action.kind==='out'?'0.01':'0'} step="0.01" value={amount} onChange={e=>setAmount(e.target.value)}/></label>
     {(action.kind==='in'||action.kind==='out')&&<label>Motivo<input required maxLength={300} value={note} onChange={e=>setNote(e.target.value)}/></label>}
     {action.kind==='close'&&<p className="muted">El cierre fija la diferencia entre el efectivo contado y esperado. No se puede volver a modificar este turno.</p>}
     <div className="actions"><button type="button" disabled={saving} onClick={()=>setAction(null)}>Cancelar</button>
       <button type="submit" className="primary" disabled={saving}>{saving?'Guardando…':'Confirmar'}</button></div>
   </form></div>}
 </div>
}
