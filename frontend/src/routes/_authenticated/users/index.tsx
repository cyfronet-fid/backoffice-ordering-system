import { readUsers, UserPublic } from "@/client";
import { UsersTable } from "@/components/user/usersTable.tsx";
import { getAuthorizationHeader } from "@/utils.ts";
import { Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/users/")({
  component: Users,
  loader: async ({ context }) => {
    const { data } = await readUsers({
      headers: { ...getAuthorizationHeader(context.auth) },
    });
    return data;
  },
});

function Users() {
  const users: UserPublic[] = Route.useLoaderData();
  return (
    <>
      <Heading mb={2}>Users</Heading>
      <UsersTable users={users} />
    </>
  );
}
