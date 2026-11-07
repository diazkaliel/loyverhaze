import {ChartNoAxesCombined, ChevronDown, ChevronRight, Layers3, Package, Tags, Users, Store} from 'lucide-react';
export type View='summary'|'items'|'categories'|'stores'|'employees';
type Props={view:View;onNavigate:(next:View)=>void};
export function Sidebar({view,onNavigate}:Props){
  return <aside className="sidebar"><div className="brand"><span className="brand-mark">L</span><span>Loyverhaze<small>BACK OFFICE</small></span></div>
    <nav aria-label="Navegación del Back Office">
      <div className="menu-label">INFORMES</div>
      <button className={view==='summary'?'active':''} onClick={()=>onNavigate('summary')}><ChartNoAxesCombined size={18}/> Resumen de ventas</button>
      <div className="menu-label section-title"><Layers3 size={16}/> ARTÍCULOS <ChevronDown size={14}/></div>
      <button className={view==='items'?'active':''} onClick={()=>onNavigate('items')}><Package size={18}/> Lista de artículos</button>
      <button className={view==='categories'?'active':''} onClick={()=>onNavigate('categories')}><Tags size={18}/> Categorías</button>
      <div className="menu-label section-title"><Users size={16}/> PERSONAL <ChevronDown size={14}/></div>
      <button className={view==='employees'?'active':''} onClick={()=>onNavigate('employees')}><Users size={18}/> Empleados</button>
      <div className="menu-label section-title"><Store size={16}/> CONFIGURACIÓN <ChevronDown size={14}/></div>
      <button className={view==='stores'?'active':''} onClick={()=>onNavigate('stores')}><Store size={18}/> Sucursales</button>
    </nav>
    <div className="sidebar-footer"><ChevronRight size={14}/> Primera entrega · Catálogo</div>
  </aside>
}
