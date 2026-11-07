import React,{useEffect,useMemo,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Plus,RefreshCw,Search,ExternalLink} from 'lucide-react';
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
 const title=view==='summary'?'Resumen de ventas':view==='items'?'Lista de artículos':'Categorías';
 const visibleItems=useMemo(()=>items.filter(i=>[i.name,i.sku,i.barcode,categories.find(c=>c.id===i.category)?.name??''].some(v=>v.toLocaleLowerCase().includes(search.toLocaleLowerCase()))),[items,categories,search]);
 const visibleCategories=useMemo(()=>categories.filter(c=>c.name.toLocaleLowerCase().includes(search.toLocaleLowerCase())),[categories,search]);
 const nav=(next:View)=>{setView(next);setSearch('');setForm(null)};
 return <div className="shell"><Sidebar view={view} onNavigate={nav}/><main>
 <header><span>Back Office <span className="muted">/ {view==='summary'?'Informes':'Artículos'} / {title}</span></span><span className="user">{session?.username??'Invitado'}</span></header>
 <section className="content">
 <div className="heading"><div><p className="eyebrow">{view==='summary'?'INFORMES':'ARTÍCULOS'}</p><h1>{title}</h1><p className="muted">{view==='summary'?'Información de ventas del negocio':'Organiza y administra los artículos de tu negocio.'}</p></div>
 {view!=='summary'&&session?.authenticated&&<button className="primary" onClick={()=>setForm(view==='items'?{kind:'item'}:{kind:'category'})}><Plus size={18}/>{view==='items'?'Agregar artículo':'Agregar categoría'}</button>}</div>
 {error&&<div className="error" role="alert">{error}</div>}
 {session&&!session.authenticated&&<div className="notice">Para utilizar el catálogo inicia sesión en <a href="http://localhost:8000/admin/login/" target="_blank" rel="noreferrer">administración Django <ExternalLink size={14}/></a> y actualiza la página. La creación y edición requieren una cuenta de personal.</div>}
 {view==='summary'&&<div className="notice">Aún no hay un módulo de ventas. No mostramos indicadores inventados: el resumen de ventas se habilitará cuando existan registros de ventas y pagos reales.</div>}
 {session?.authenticated&&view!=='summary'&&<>
 <div className="toolbar"><label className="search-field"><Search size={16}/><input aria-label="Buscar registros" placeholder={view==='items'?'Buscar artículos, REF o categoría':'Buscar categorías'} value={search} onChange={e=>setSearch(e.target.value)}/></label><span>{view==='items'?visibleItems.length:visibleCategories.length} registros</span><button onClick={()=>void refresh()} disabled={loading}><RefreshCw size={16}/> {loading?'Cargando…':'Actualizar'}</button></div>
 <div className="table-wrap"><table><thead><tr>{view==='items'?<><th>Nombre del artículo</th><th>REF (SKU)</th><th>Categoría</th><th>Precio</th><th>Disponible</th></>:<><th>Categoría</th><th>Color</th></>}</tr></thead><tbody>{view==='items'?visibleItems.map(item=><tr key={item.id}><td><button className="table-link" onClick={()=>setForm({kind:'item',item})}>{item.name}</button></td><td>{item.sku}</td><td>{categories.find(c=>c.id===item.category)?.name??'Sin categoría'}</td><td>{item.price}</td><td>{item.available_for_sale?'Sí':'No'}</td></tr>):visibleCategories.map(category=><tr key={category.id}><td><button className="table-link" onClick={()=>setForm({kind:'category',category})}>{category.name}</button></td><td><span className="swatch" style={{background:category.color}}/>{category.color}</td></tr>)}</tbody></table>
 {(view==='items'?visibleItems.length:visibleCategories.length)===0&&<div className="empty">{search?'No hay coincidencias.':'Aún no hay registros. Utiliza «Agregar» para comenzar.'}</div>}</div></>}
 {form&&<CatalogForm kind={form.kind} categories={categories} item={form.kind==='item'?form.item:undefined} category={form.kind==='category'?form.category:undefined} onCancel={()=>setForm(null)} onDone={async()=>{await refresh();setForm(null)}}/>}
 </section></main></div>
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
