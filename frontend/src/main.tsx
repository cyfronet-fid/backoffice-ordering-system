import { ChakraProvider } from "@chakra-ui/react";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { StrictMode } from "react";
import ReactDOM from "react-dom/client";

import { client } from "./client";
import { routeTree } from "./routeTree.gen";
import "./styles/main.scss";

// Set backend API URL
client.setConfig({
  baseUrl: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
});

// Create a new router instance
const router = createRouter({ routeTree });

// Register the router instance for type safety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

// Render the app
const rootElement = document.getElementById("root")!;
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <StrictMode>
      <ChakraProvider>
        <RouterProvider router={router} />
      </ChakraProvider>
    </StrictMode>,
  );
}
