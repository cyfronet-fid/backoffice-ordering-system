import { OrderPublic, OrderPublicWithDetails, UserPublic } from "@/client";
import { useEffect, useState } from "react";
import { AuthContextProps } from "react-oidc-context";

export const getAuthorizationHeader = (auth: AuthContextProps) => {
  return {
    Authorization: `Bearer ${auth.user?.access_token}`,
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
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  }).format(date);
};

export function isExtendedOrder(
  order: OrderPublic,
): order is OrderPublicWithDetails {
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

export function snakeToTitle(str: string): string {
  return str
    .split("_")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

export function getMpUser(
  all_users: UserPublic[] | undefined,
): UserPublic | undefined {
  return all_users?.find((user) => user.user_type.includes("mp_user"));
}
