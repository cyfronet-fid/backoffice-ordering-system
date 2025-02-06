import { client } from "@/client/client.gen.ts";
import { DefaultError } from "@/components/common/defaultError.tsx";
import { FullScreenSpinner } from "@/components/common/fullScreenSpinner.tsx";
import { NotFound } from "@/components/common/notFound.tsx";
import { appConfig, oidcConfig } from "@/config.ts";
import { routeTree } from "@/routeTree.gen.ts";
import { ChakraProvider } from "@chakra-ui/react";
import { createRouter, RouterProvider } from "@tanstack/react-router";
import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import { AuthProvider, useAuth } from "react-oidc-context";

const router = createRouter({
  routeTree,
  defaultPendingComponent: () => <FullScreenSpinner />,
  defaultErrorComponent: ({ error }) => <DefaultError error={error} />,
  defaultNotFoundComponent: () => <NotFound />,
  context: {
    auth: undefined!,
  },
});

// Register the router instance for type safety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

// Configure the @hey-api/openapi-ts client
client.setConfig({
  baseUrl: appConfig.backendUrl,
});

export function InnerApp() {
  const auth = useAuth();

  if (auth.isLoading) {
    return <FullScreenSpinner />;
  }

  return <RouterProvider router={router} context={{ auth }} />;
}

export function App() {
  return (
    <AuthProvider {...oidcConfig}>
      <ChakraProvider>
        <InnerApp />
      </ChakraProvider>
    </AuthProvider>
  );
}

// Render the app
const rootElement = document.getElementById("root")!;
if (!rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
