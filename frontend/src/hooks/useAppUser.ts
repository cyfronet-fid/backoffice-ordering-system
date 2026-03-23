import { getRouteApi } from "@tanstack/react-router";

const authenticatedRoute = getRouteApi("/_authenticated");

export function useAppUser() {
  const { appUser } = authenticatedRoute.useLoaderData();
  return appUser!;
}
