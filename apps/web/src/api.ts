export type Category={id:string;name:string;color:string};
export type Item={id:string;name:string;sku:string;category:string|null;price:string;cost:string;barcode:string;description:string;available_for_sale:boolean};
export type Session={authenticated:boolean;username:string|null};
export type ItemPayload={name:string;sku:string;price:string;cost:string;category:string|null;barcode:string;description:string;available_for_sale:boolean};
const base=import.meta.env.VITE_API_URL??'http://localhost:8000/api';
function csrf():string{return document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1]??''}
export async function request<T>(path:string,options:RequestInit={}):Promise<T>{
  const response=await fetch(base+path,{...options,credentials:'include',headers:{'Content-Type':'application/json','X-CSRFToken':decodeURIComponent(csrf()),...options.headers}});
  if(!response.ok){let detail='';try{const result=await response.json() as Record<string,unknown>;detail=JSON.stringify(result)}catch{detail=response.statusText}throw new Error(detail||`Error HTTP ${response.status}`)}
  if(response.status===204)return undefined as T;
  return response.json() as Promise<T>;
}
export const api={
  session:()=>request<Session>('/session/'),
  categories:()=>request<Category[]>('/categories/'),
  items:()=>request<Item[]>('/items/'),
  createCategory:(data:Pick<Category,'name'|'color'>)=>request<Category>('/categories/',{method:'POST',body:JSON.stringify(data)}),
  updateCategory:(id:string,data:Pick<Category,'name'|'color'>)=>request<Category>(`/categories/${id}/`,{method:'PATCH',body:JSON.stringify(data)}),
  createItem:(data:ItemPayload)=>request<Item>('/items/',{method:'POST',body:JSON.stringify(data)}),
  updateItem:(id:string,data:ItemPayload)=>request<Item>(`/items/${id}/`,{method:'PUT',body:JSON.stringify(data)}),
};
