import { Button, Flex, Text } from "@chakra-ui/react";
import { useAuth } from "react-oidc-context";

import { UserIcon } from "../common/icons/userIcon.tsx";
import { Logo } from "./logo.tsx";

export const Header = () => {
  const auth = useAuth();

  return (
    <Flex
      align="center"
      justify="space-between"
      px="6"
      height="100%"
      bg="gray.200"
    >
      <Logo />
      <Flex align={"center"} gap={2}>
        <UserIcon />
        <Text>{auth.user?.profile?.name}</Text>
        <Button onClick={() => void auth.signoutRedirect()}>Logout</Button>
      </Flex>
    </Flex>
  );
};
