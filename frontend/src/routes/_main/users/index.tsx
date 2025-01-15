import { Heading } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";

import { readUsers, User } from "../../../client";
import { UsersTable } from "../../../components/usersTable.tsx";

export const Route = createFileRoute("/_main/users/")({
  component: Users,
  loader: async () => {
    const { data } = await readUsers();
    return data;
  },
});

function Users() {
  const users: User[] = Route.useLoaderData();
  return (
    <>
      <Heading mb={2}>Users</Heading>
      <UsersTable users={users} />
    </>
  );
}
