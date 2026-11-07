import {useState,type FormEvent} from 'react';
import {LockKeyhole,ArrowRight} from 'lucide-react';
import {api,type Session} from '../api';

export function Login({onLogin}:{onLogin:(session:Session)=>void}){
 const [username,setUsername]=useState('');
 const [password,setPassword]=useState('');
 const [error,setError]=useState('');
 const [loading,setLoading]=useState(false);
 async function submit(event:FormEvent){
   event.preventDefault();setError('');setLoading(true);
   try{const session=await api.login(username,password);setPassword('');onLogin(session)}
   catch(e){setError(e instanceof Error?e.message:String(e))}
   finally{setLoading(false)}
 }
 return <div className="login-page">
   <section className="login-card">
     <div className="login-logo"><span className="brand-mark">L</span><strong>Loyverhaze</strong></div>
     <div className="login-icon"><LockKeyhole size={23}/></div>
     <h1>Bienvenido de nuevo</h1>
     <p className="muted">Ingresa con tu cuenta para acceder al Back Office.</p>
     <form onSubmit={e=>void submit(e)}>
       <label>Usuario<input autoComplete="username" required value={username} onChange={e=>setUsername(e.target.value)} placeholder="Tu nombre de usuario"/></label>
       <label>Contraseña<input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)} placeholder="Introduce tu contraseña"/></label>
       {error&&<div className="error" role="alert">{error}</div>}
       <button type="submit" disabled={loading} className="primary login-submit">{loading?'Accediendo…':'Iniciar sesión'}<ArrowRight size={17}/></button>
     </form>
     <p className="login-caption">Acceso de desarrollo. Los permisos de empresa y sucursal se implementarán posteriormente.</p>
   </section>
 </div>
}
