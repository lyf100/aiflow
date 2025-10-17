/// <reference types="vite/client" />

// 🔧 扩展 ImportMeta 接口以支持 Vite 环境变量
interface ImportMetaEnv {
  readonly VITE_WS_URL?: string;
  // 可以在这里添加更多环境变量
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
