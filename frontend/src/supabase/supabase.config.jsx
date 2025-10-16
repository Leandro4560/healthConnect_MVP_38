import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  import.meta.env.VITE_APP_SUPABASE_URL,
  import.meta.env.VITE_APP_SUPABASE_ANON_KEY
);

const url = import.meta.env.VITE_APP_SUPABASE_URL || "fallback";
const key = import.meta.env.VITE_APP_SUPABASE_ANON_KEY || "fallback";
console.log({ url, key });

console.log("URL:", import.meta.env.VITE_APP_SUPABASE_URL);
console.log("KEY:", import.meta.env.VITE_APP_SUPABASE_ANON_KEY);
