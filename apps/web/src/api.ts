export type Category={id:string;name:string;color:string};
export type Item={id:string;name:string;sku:string;category:string|null;price:string;cost:string;barcode:string;description:string;available_for_sale:boolean};
export type Session={authenticated:boolean;username:string|null;is_staff:boolean;organizations:{id:string;name:string;role:string}[];active_organization_id:string|null};
export type Store={id:string;name:string;is_active:boolean};
export type Employee={id:string;username:string;role:'owner'|'manager'|'cashier';is_active:boolean};
export type StockRow={item_id:string;item_name:string;sku:string;store_id:string;store_name:string;store_active:boolean;quantity:string};
export type StockMovement={id:string;item:string;item_name:string;store:string;store_name:string;quantity_delta:string;resulting_quantity:string;reason:'receipt'|'adjustment'|'sale';note:string;username:string;created_at:string};
export type StockMovementInput={item_id:string;store_id:string;quantity_delta:string;reason:'receipt'|'adjustment';note:string;idempotency_key:string};
export type SaleLine={item_name:string;sku:string;quantity:string;unit_price:string;line_total:string};
export type Sale={id:string;store:string;store_name:string;cashier:number;total:string;cash_received:string;change_due:string;payment_method:'cash';created_at:string;lines:SaleLine[]};
export type CheckoutInput={store_id:string;idempotency_key:string;payment_method:'cash';cash_received:string;lines:{item_id:string;quantity:string}[]};
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
  checkout:(data:CheckoutInput)=>request<Sale>('/sales/checkout/',{method:'POST',body:JSON.stringify(data)}),
  sales:()=>request<Sale[]>('/sales/'),
  stock:()=>request<StockRow[]>('/inventory/stock/'),
  movements:()=>request<StockMovement[]>('/inventory/movements/'),
  createMovement:(data:StockMovementInput)=>request<StockMovement>('/inventory/movements/',{method:'POST',body:JSON.stringify(data)}),
  stores:()=>request<Store[]>('/stores/'),
  createStore:(data:{name:string;is_active:boolean})=>request<Store>('/stores/',{method:'POST',body:JSON.stringify(data)}),
  updateStore:(id:string,data:{name:string;is_active:boolean})=>request<Store>(`/stores/${id}/`,{method:'PATCH',body:JSON.stringify(data)}),
  employees:()=>request<Employee[]>('/employees/'),
  createEmployee:(data:{username:string;password:string;role:'manager'|'cashier'})=>request<Employee>('/employees/',{method:'POST',body:JSON.stringify(data)}),
  updateEmployee:(id:string,role:Employee['role'])=>request<Employee>(`/employees/${id}/`,{method:'PATCH',body:JSON.stringify({role})}),
  categories:()=>request<Category[]>('/categories/'),
  items:()=>request<Item[]>('/items/'),
  createCategory:(data:Pick<Category,'name'|'color'>)=>request<Category>('/categories/',{method:'POST',body:JSON.stringify(data)}),
  updateCategory:(id:string,data:Pick<Category,'name'|'color'>)=>request<Category>(`/categories/${id}/`,{method:'PATCH',body:JSON.stringify(data)}),
  createItem:(data:ItemPayload)=>request<Item>('/items/',{method:'POST',body:JSON.stringify(data)}),
  updateItem:(id:string,data:ItemPayload)=>request<Item>(`/items/${id}/`,{method:'PUT',body:JSON.stringify(data)}),
};
