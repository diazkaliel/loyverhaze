export type Category = {id:string;name:string;color:string};
export type Item = {id:string;name:string;sku:string;category:string|null;price:string;cost:string;available_for_sale:boolean};
export type Session = {authenticated:boolean;username:string|null};
const base = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
function csrf():string { return document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=')[1] ?? ''; }
export async function request<T>(path:string,options:RequestInit={}):Promise<T>{
  const response=await fetch(base+path,{...options,credentials:'include',headers:{'Content-Type':'application/json','X-CSRFToken':decodeURIComponent(csrf()),...options.headers}});
  if(!response.ok){const body=await response.text();throw new Error(body || `Error HTTP ${response.status}`);}
  return response.json() as Promise<T>;
}
export const api={session:()=>request<Session>('/session/'),categories:()=>request<Category[]>('/categories/'),items:()=>request<Item[]>('/items/'),createCategory:(name:string)=>request<Category>('/categories/',{method:'POST',body:JSON.stringify({name})}),createItem:(data:{name:string;sku:string;price:string;category:string|null})=>request<Item>('/items/',{method:'POST',body:JSON.stringify(data)})};
