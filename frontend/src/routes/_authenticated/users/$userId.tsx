import { getUserById } from "@/client";
import { NotFound } from "@/components/common/notFound.tsx";
import { UserCard } from "@/components/user/userCard.tsx";
import { useAppUser } from "@/hooks/useAppUser.ts";
import { getAuthorizationHeader } from "@/utils.ts";
import { Badge, Box, Button, Flex, Heading } from "@chakra-ui/react";
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/users/$userId")({
  component: RouteComponent,
  loader: async ({ context, params }) => {
    const { data } = await getUserById({
      headers: { ...getAuthorizationHeader(context.auth) },
      path: { user_id: Number(params.userId) },
    });
    return data;
  },
});

function RouteComponent() {
  const user = Route.useLoaderData()!;
  const appUser = useAppUser();

  if (!user) {
    return <NotFound />;
  }

  return (
    <Box p={6}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading>
          {`User > ${user.id}`}
          {appUser.id === user.id ? (
            <Badge colorScheme={"purple"}>You</Badge>
          ) : undefined}
        </Heading>
        <Button as={RouterLink} to={"/users"} variant="outline">
          Back to users
        </Button>
      </Flex>

      <Flex gap={6} align="flex-start">
        <Box flex="1">
          <UserCard user={user} />
        </Box>

        <Box flex="1">{/*  Left empty for now. */}</Box>
      </Flex>
    </Box>
  );
}
