// env.d.ts
/// <reference types="vite/client" />

// (Optionally) add your own vars here for stricter typing:
interface ImportMetaEnv {
    readonly VITE_API_URL: string
    readonly VITE_YJS_SERVER_URL: string
  }
  
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }