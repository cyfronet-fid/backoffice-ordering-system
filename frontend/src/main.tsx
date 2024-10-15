import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Root from "./routes/Root.tsx";
import { client } from "./client";
import ErrorPage from "./routes/ErrorPage.tsx";
import { Tickets } from "./routes/Tickets.tsx";

client.setConfig({
  baseUrl: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
});

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/tickets",
    element: <Tickets />,
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
