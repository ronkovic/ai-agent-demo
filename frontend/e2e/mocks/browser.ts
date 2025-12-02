import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

// This configures a Service Worker with the given request handlers.
export const worker = setupWorker(...handlers);

// Start the worker
export async function startMockServiceWorker() {
  if (typeof window !== "undefined") {
    return worker.start({
      onUnhandledRequest: "bypass",
    });
  }
}
