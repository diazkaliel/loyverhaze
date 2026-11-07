import React,{useEffect,useMemo,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Plus,RefreshCw,Search,LogOut} from 'lucide-react';
import {Login} from './components/Login';
import {OrganizationManagement} from './components/OrganizationManagement';
import {InventoryManagement} from './components/InventoryManagement';
import {PointOfSale} from './components/PointOfSale';
import {api,type Category,type Item,type Session} from './api';
import {CatalogForm} from './components/CatalogForm';
import {Sidebar,type View} from './components/Sidebar';
import './styles.css';

function App(){
 const [session,setSession]=useState<Session|null>(null);
 const [view,setView]=useState<View>('summary');
 const [items,setItems]=useState<Item[]>([]);
 const [categories,setCategories]=useState<Category[]>([]);
 const [loading,setLoading]=useState(false);
 const [error,setError]=useState('');
 const [search,setSearch]=useState('');
 const [form,setForm]=useState<{kind:'item';item?:Item}|{kind:'category';category?:Category}|null>(null);
 async function refresh(){setLoading(true);setError('');try{const [i,c]=await Promise.all([api.items(),api.categories()]);setItems(i);setCategories(c)}catch(e){setError(e instanceof Error?e.message:String(e))}finally{setLoading(false)}}
 useEffect(()=>{api.session().then(s=>{setSession(s);if(s.authenticated)void refresh()}).catch(e=>setError(String(e)))},[]);
 const title=view==='summary'?'Resumen de ventas':view==='items'?'Lista de artículos':view==='categories'?'Categorías':view==='stores'?'Sucursales':view==='employees'?'Empleados':view==='stock'?'Existencias':view==='movements'?'Movimientos':'Ventas (POS)';
 const visibleItems=useMemo(()=>items.filter(i=>[i.name,i.sku,i.barcode,categories.find(c=>c.id===i.category)?.name??''].some(v=>v.toLocaleLowerCase().includes(search.toLocaleLowerCase()))),[items,categories,search]);
 const visibleCategories=useMemo(()=>categories.filter(c=>c.name.toLocaleLowerCase().includes(search.toLocaleLowerCase())),[categories,search]);
 const activeRole=session?.organizations.find(o=>o.id===session.active_organization_id)?.role??'';
 const nav=(next:View)=>{setView(next);setSearch('');setForm(null)};
 async function switchOrganization(id:string){setError('');try{await api.chooseOrganization(id);const latest=await api.session();setSession(latest);setItems([]);setCategories([]);setForm(null);await refresh()}catch(e){setError(e instanceof Error?e.message:String(e))}}
 async function signOut(){setError('');try{const result=await api.logout();setSession(result);setItems([]);setCategories([]);setForm(null);setView('summary')}catch(e){setError(e instanceof Error?e.message:String(e))}}
 if(!session)return <div className="startup">Conectando con Loyverhaze…{error&&<div className="error" role="alert">{error}</div>}</div>;
 if(!session.authenticated)return <Login onLogin={s=>{setSession(s);void refresh()}}/>;
 return <div className="shell"><Sidebar view={view} onNavigate={nav}/><main>
 <header><span>Back Office <span className="muted">/ {view==='summary'?'Informes':view==='stores'?'Configuración':view==='employees'?'Personal':view==='stock'||view==='movements'?'Inventario':view==='pos'?'Punto de venta':'Artículos'} / {title}</span></span><div className="account">{session.organizations.length>0&&<label className="org-choice"><span className="sr-only">Negocio activo</span><select aria-label="Negocio activo" value={session.active_organization_id??''} onChange={e=>void switchOrganization(e.target.value)}>{session.organizations.map(o=><option key={o.id} value={o.id}>{o.name}</option>)}</select></label>}<span className="user">{session.username}</span><button className="signout" onClick={()=>void signOut()} title="Cerrar sesión"><LogOut size={17}/> Salir</button></div></header>
 <section className="content">
 {view==='pos'?<PointOfSale key={session.active_organization_id??'no-org'} organizationId={session.active_organization_id}/>:(view==='stores'||view==='employees')?<OrganizationManagement key={session.active_organization_id+'-'+view} kind={view} organizationId={session.active_organization_id} role={activeRole}/> :(view==='stock'||view==='movements')?<InventoryManagement key={session.active_organization_id+'-'+view} organizationId={session.active_organization_id} canWrite={session.is_staff} view={view}/> : <>
 <div className="heading"><div><p className="eyebrow">{view==='summary'?'INFORMES':'ARTÍCULOS'}</p><h1>{title}</h1><p className="muted">{view==='summary'?'Información de ventas del negocio':'Organiza y administra los artículos de tu negocio.'}</p></div>
 {(view==='items'||view==='categories')&&session.is_staff&&<button className="primary" onClick={()=>setForm(view==='items'?{kind:'item'}:{kind:'category'})}><Plus size={18}/>{view==='items'?'Agregar artículo':'Agregar categoría'}</button>}</div>
 {error&&<div className="error" role="alert">{error}</div>}
 {session.organizations.length===0&&<div className="notice">No tienes ningún negocio asignado. Pide al administrador que te agregue a una organización.</div>}
 {!session.is_staff&&(view==='items'||view==='categories')&&<div className="notice">Tu cuenta tiene acceso de lectura. Para modificar el catálogo necesitas permiso de personal.</div>}
 {view==='summary'&&<div className="notice">Aún no hay un módulo de ventas. No mostramos indicadores inventados: el resumen de ventas se habilitará cuando existan registros de ventas y pagos reales.</div>}
 {(view==='items'||view==='categories')&&<>
 <div className="toolbar"><label className="search-field"><Search size={16}/><input aria-label="Buscar registros" placeholder={view==='items'?'Buscar artículos, REF o categoría':'Buscar categorías'} value={search} onChange={e=>setSearch(e.target.value)}/></label><span>{view==='items'?visibleItems.length:visibleCategories.length} registros</span><button onClick={()=>void refresh()} disabled={loading}><RefreshCw size={16}/> {loading?'Cargando…':'Actualizar'}</button></div>
 <div className="table-wrap"><table><thead><tr>{view==='items'?<><th>Nombre del artículo</th><th>REF (SKU)</th><th>Categoría</th><th>Precio</th><th>Disponible</th></>:<><th>Categoría</th><th>Color</th></>}</tr></thead><tbody>{view==='items'?visibleItems.map(item=><tr key={item.id}><td><button className="table-link" onClick={()=>session.is_staff&&setForm({kind:'item',item})}>{item.name}</button></td><td>{item.sku}</td><td>{categories.find(c=>c.id===item.category)?.name??'Sin categoría'}</td><td>{item.price}</td><td>{item.available_for_sale?'Sí':'No'}</td></tr>):visibleCategories.map(category=><tr key={category.id}><td><button className="table-link" onClick={()=>session.is_staff&&setForm({kind:'category',category})}>{category.name}</button></td><td><span className="swatch" style={{background:category.color}}/>{category.color}</td></tr>)}</tbody></table>
 {(view==='items'?visibleItems.length:visibleCategories.length)===0&&<div className="empty">{search?'No hay coincidencias.':'Aún no hay registros. Utiliza «Agregar» para comenzar.'}</div>}</div></>}
 {form&&session.is_staff&&<CatalogForm kind={form.kind} categories={categories} item={form.kind==='item'?form.item:undefined} category={form.kind==='category'?form.category:undefined} onCancel={()=>setForm(null)} onDone={async()=>{await refresh();setForm(null)}}/>}
 </>}
 </section></main></div>
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
