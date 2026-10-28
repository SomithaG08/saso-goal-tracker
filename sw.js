const C="sgt-v3";
const SHELL=["./","./index.html","./manifest.webmanifest","./icon-192.png","./icon-512.png","./apple-touch-icon.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)));self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>!k.startsWith(C)).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;
  const url=new URL(r.url);
  if(url.origin===location.origin){
    // Always try the network first for the page and the Notion content, fall back to cache offline.
    if(r.mode==="navigate"||url.pathname.endsWith("/content.json")){
      const key=r.mode==="navigate"?"./index.html":"./content.json";
      e.respondWith(fetch(r).then(res=>{if(res.ok){const copy=res.clone();caches.open(C).then(c=>c.put(key,copy))}return res}).catch(()=>caches.match(key)));
      return;
    }
    e.respondWith(caches.match(r).then(m=>m||fetch(r)));
    return;
  }
  if(url.hostname==="fonts.googleapis.com"||url.hostname==="fonts.gstatic.com"){
    e.respondWith(caches.open(C+"-fonts").then(c=>c.match(r).then(m=>m||fetch(r).then(res=>{c.put(r,res.clone());return res}))));
  }
});
