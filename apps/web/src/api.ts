export type Category={id:string;name:string;color:string};
export type Item={id:string;name:string;sku:string;category:string|null;price:string;cost:string;barcode:string;description:string;available_for_sale:boolean};
export type Session={authenticated:boolean;username:string|null;is_staff:boolean;organizations:{id:string;name:string;role:string}[];active_organization_id:string|null};
export type ItemPayload={name:string;sku:string;price:string;cost:string;category:string|null;barcode:string;description:string;available_for_sale:boolean};
const base='/api';
function csrf():string{return document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1]??''}
export async function request<T>(path:string,options:RequestInit={}):Promise<T>{
  let response:Response;
  try{
    response=await fetch(base+path,{...options,credentials:'include',headers:{'Content-Type':'application/json','X-CSRFToken':decodeURIComponent(csrf()),...options.headers}});
  }catch{throw new Error('No se pudo conectar con la API. Comprueba que Django esté ejecutándose en el puerto 8000.')}
  if(!response.ok){let detail='';try{const result=await response.json() as Record<string,unknown>;detail=typeof result.detail==='string'?result.detail:JSON.stringify(result)}catch{detail=response.statusText}throw new Error(detail||`Error HTTP ${response.status}`)}
  if(response.status===204)return undefined as T;
  return response.json() as Promise<T>;
}
export const api={
  session:()=>request<Session>('/session/'),
  login:(username:string,password:string)=>request<Session>('/login/',{method:'POST',body:JSON.stringify({username,password})}),
  logout:()=>request<Session>('/logout/',{method:'POST'}),
  chooseOrganization:(organization_id:string)=>request<{organization_id:string}>('/organization/select/',{method:'POST',body:JSON.stringify({organization_id})}),
  categories:()=>request<Category[]>('/categories/'),
  items:()=>request<Item[]>('/items/'),
  createCategory:(data:Pick<Category,'name'|'color'>)=>request<Category>('/categories/',{method:'POST',body:JSON.stringify(data)}),
  updateCategory:(id:string,data:Pick<Category,'name'|'color'>)=>request<Category>(`/categories/${id}/`,{method:'PATCH',body:JSON.stringify(data)}),
  createItem:(data:ItemPayload)=>request<Item>('/items/',{method:'POST',body:JSON.stringify(data)}),
  updateItem:(id:string,data:ItemPayload)=>request<Item>(`/items/${id}/`,{method:'PUT',body:JSON.stringify(data)}),
};
