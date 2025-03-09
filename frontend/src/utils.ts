import { OrderPublic, OrderPublicWithProviders } from "@/client";
import { useEffect, useState } from "react";
import { AuthContextProps } from "react-oidc-context";

export const getAuthorizationHeader = (auth: AuthContextProps) => {
  return {
    Authorization: `Bearer: ${auth.user?.access_token}`,
  };
};

export const wait = (seconds: number) =>
  new Promise((resolve) => setTimeout(resolve, 1000 * seconds));

export const convertTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);

  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "long",
    year: "2-digit",
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  }).format(date);
};

export function isExtendedOrder(
  order: OrderPublic,
): order is OrderPublicWithProviders {
  return "providers" in order;
}

export function useDebouncedValue<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timeout = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timeout);
  }, [value, delay]);

  return debounced;
}
