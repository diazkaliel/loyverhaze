import {useState, type FormEvent} from 'react';
import {api, type Category, type Item, type ItemPayload} from '../api';

type Props={kind:'item'|'category';categories:Category[];item?:Item;category?:Category;onDone:()=>Promise<void>;onCancel:()=>void};
export function CatalogForm({kind,categories,item,category:currentCategory,onDone,onCancel}:Props){
  const [name,setName]=useState(item?.name??currentCategory?.name??'');
  const [sku,setSku]=useState(item?.sku??'');
  const [price,setPrice]=useState(item?.price??'');
  const [cost,setCost]=useState(item?.cost??'0.00');
  const [barcode,setBarcode]=useState(item?.barcode??'');
  const [description,setDescription]=useState(item?.description??'');
  const [category,setCategory]=useState(item?.category??'');
  const [color,setColor]=useState(currentCategory?.color??'#64748b');
  const [available,setAvailable]=useState(item?.available_for_sale??true);
  const [saving,setSaving]=useState(false);
  const [error,setError]=useState('');
  async function submit(event:FormEvent){
    event.preventDefault();setSaving(true);setError('');
    try{
      if(kind==='category'){
        const data={name:name.trim(),color};
        if(currentCategory)await api.updateCategory(currentCategory.id,data);
        else await api.createCategory(data);
      }else{
        const data:ItemPayload={name:name.trim(),sku:sku.trim(),price,cost,barcode:barcode.trim(),description,category:category||null,available_for_sale:available};
        if(item)await api.updateItem(item.id,data);
        else await api.createItem(data);
      }
      await onDone();
    }catch(e){setError(e instanceof Error?e.message:String(e))}finally{setSaving(false)}
  }
  return <div className="overlay" role="presentation"><form className="dialog" onSubmit={e=>void submit(e)} aria-label={kind==='item'?'Formulario de artículo':'Formulario de categoría'}>
    <h2>{kind==='item'?(item?'Editar artículo':'Crear artículo'):(currentCategory?'Editar categoría':'Crear categoría')}</h2>
    {error&&<div className="error" role="alert">{error}</div>}
    <label>Nombre<input required maxLength={kind==='item'?200:120} value={name} onChange={e=>setName(e.target.value)}/></label>
    {kind==='item'?<>
      <label>Categoría<select value={category} onChange={e=>setCategory(e.target.value)}><option value="">Sin categoría</option>{categories.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
      <label>Descripción<textarea value={description} onChange={e=>setDescription(e.target.value)} rows={2}/></label>
      <label className="checkbox-line"><input type="checkbox" checked={available} onChange={e=>setAvailable(e.target.checked)}/> Disponible para la venta</label>
      <div className="form-grid"><label>Precio<input required type="number" min="0" step="0.01" value={price} onChange={e=>setPrice(e.target.value)}/></label><label>Coste<input required type="number" min="0" step="0.01" value={cost} onChange={e=>setCost(e.target.value)}/></label></div>
      <div className="form-grid"><label>REF (SKU)<input required maxLength={40} value={sku} onChange={e=>setSku(e.target.value)}/></label><label>Código de barras<input maxLength={100} value={barcode} onChange={e=>setBarcode(e.target.value)}/></label></div>
    </>:<label>Color de categoría<input type="color" value={color} onChange={e=>setColor(e.target.value)}/></label>}
    <div className="actions"><button type="button" onClick={onCancel} disabled={saving}>Cancelar</button><button className="primary" type="submit" disabled={saving}>{saving?'Guardando…':'Guardar'}</button></div>
  </form></div>
}
