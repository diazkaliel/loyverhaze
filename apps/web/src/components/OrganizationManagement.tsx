import {useEffect,useState,type FormEvent} from 'react';
import {Plus,RefreshCw} from 'lucide-react';
import {api,type Employee,type Store} from '../api';

type Props={kind:'stores'|'employees';organizationId:string|null;role:string};
export function OrganizationManagement({kind,organizationId,role}:Props){
 const [stores,setStores]=useState<Store[]>([]);
 const [employees,setEmployees]=useState<Employee[]>([]);
 const [loading,setLoading]=useState(true);
 const [error,setError]=useState('');
 const [form,setForm]=useState(false);
 const [editingStore,setEditingStore]=useState<Store|null>(null);
 const [name,setName]=useState('');
 const [active,setActive]=useState(true);
 const [password,setPassword]=useState('');
 const [newRole,setNewRole]=useState<'manager'|'cashier'>('cashier');
 const [saving,setSaving]=useState(false);
 const isOwner=role==='owner';
 const canStoreEdit=isOwner||role==='manager';
 async function refresh(){
   setLoading(true);setError('');
   try{if(kind==='stores')setStores(await api.stores());else setEmployees(await api.employees())}
   catch(e){setError(e instanceof Error?e.message:String(e))}
   finally{setLoading(false)}
 }
 useEffect(()=>{void refresh()},[kind,organizationId]);
 function begin(){setEditingStore(null);setName('');setActive(true);setPassword('');setNewRole('cashier');setError('');setForm(true)}
 async function submit(e:FormEvent){e.preventDefault();setSaving(true);setError('');
   try{if(kind==='stores'){
     const data={name:name.trim(),is_active:active};
     if(editingStore)await api.updateStore(editingStore.id,data);
     else await api.createStore(data);
   }else await api.createEmployee({username:name.trim(),password,role:newRole});
   setForm(false);setPassword('');await refresh()
   }catch(e){setError(e instanceof Error?e.message:String(e))}
   finally{setSaving(false)}
 }
 async function changeRole(employee:Employee,changed:Employee['role']){
   setError('');
   try{await api.updateEmployee(employee.id,changed);await refresh()}
   catch(e){setError(e instanceof Error?e.message:String(e))}
 }
 return <div className="management">
   <div className="heading"><div><p className="eyebrow">{kind==='stores'?'CONFIGURACIÓN':'EMPLEADOS'}</p>
     <h1>{kind==='stores'?'Sucursales':'Empleados'}</h1>
     <p className="muted">{kind==='stores'?'Administra las sucursales de tu negocio.':'Gestiona los accesos y roles del equipo.'}</p></div>
     {((kind==='stores'&&canStoreEdit)||(kind==='employees'&&isOwner))&&
       <button className="primary" onClick={begin}><Plus size={18}/>{kind==='stores'?'Agregar sucursal':'Agregar empleado'}</button>}
   </div>
   {error&&<div className="error" role="alert">{error}</div>}
   <div className="toolbar"><span>{kind==='stores'?stores.length:employees.length} registros</span>
     <button onClick={()=>void refresh()} disabled={loading}><RefreshCw size={16}/> {loading?'Cargando…':'Actualizar'}</button></div>
   <div className="table-wrap"><table><thead><tr>{kind==='stores'?<><th>Sucursal</th><th>Estado</th></>:<><th>Usuario</th><th>Rol</th><th>Estado</th></>}</tr></thead>
     <tbody>{kind==='stores'?stores.map(store=><tr key={store.id}>
       <td>{canStoreEdit?<button className="table-link" onClick={()=>{setEditingStore(store);setName(store.name);setActive(store.is_active);setForm(true)}}>{store.name}</button>:store.name}</td>
       <td>{store.is_active?'Activa':'Inactiva'}</td></tr>):employees.map(emp=><tr key={emp.id}><td>{emp.username}</td>
       <td>{isOwner?<select aria-label={`Rol de ${emp.username}`} value={emp.role}
         onChange={e=>void changeRole(emp,e.target.value as Employee['role'])}>
           <option value="owner">Propietario</option><option value="manager">Administrador</option><option value="cashier">Cajero</option>
         </select>:({owner:'Propietario',manager:'Administrador',cashier:'Cajero'}[emp.role])}</td>
       <td>{emp.is_active?'Activo':'Inactivo'}</td></tr>)}</tbody></table>
     {!loading&&(kind==='stores'?stores.length:employees.length)===0&&<div className="empty">No hay registros disponibles.</div>}</div>
   {form&&<div className="overlay"><form className="dialog" onSubmit={e=>void submit(e)}>
     <h2>{kind==='stores'?(editingStore?'Editar sucursal':'Crear sucursal'):'Crear empleado'}</h2>
     {error&&<div className="error" role="alert">{error}</div>}
     <label>{kind==='stores'?'Nombre de sucursal':'Nombre de usuario'}<input required minLength={2} maxLength={kind==='stores'?160:150} autoComplete="off" value={name} onChange={e=>setName(e.target.value)}/></label>
     {kind==='stores'?<label className="checkbox-line"><input type="checkbox" checked={active} onChange={e=>setActive(e.target.checked)}/>Sucursal activa</label>:
       <><label>Contraseña inicial<input required type="password" autoComplete="new-password" minLength={8} value={password} onChange={e=>setPassword(e.target.value)}/></label>
       <label>Rol<select value={newRole} onChange={e=>setNewRole(e.target.value as 'manager'|'cashier')}>
         <option value="cashier">Cajero</option><option value="manager">Administrador</option></select></label></>}
     <div className="actions"><button type="button" onClick={()=>setForm(false)} disabled={saving}>Cancelar</button>
       <button className="primary" type="submit" disabled={saving}>{saving?'Guardando…':'Guardar'}</button></div>
   </form></div>}
 </div>
}
