import { UserIcon } from "@/components/common/icons/userIcon.tsx";
import { Logo } from "@/components/layout/logo.tsx";
import { Button, Flex, Link, Text } from "@chakra-ui/react";
import { useAuth } from "react-oidc-context";

type HeaderProps = {
  headerBackgroundColor?: string;
  userName?: string;
};

export const Header = ({
  headerBackgroundColor = "gray.200",
  userName,
}: HeaderProps) => {
  const auth = useAuth();

  return (
    <Flex
      align="center"
      justify="space-between"
      px="6"
      height="100%"
      bg={headerBackgroundColor}
    >
      <Logo />
      {auth.isAuthenticated ? (
        <Flex align={"center"} gap={2}>
          <UserIcon />
          <Text fontWeight="bold">{userName}</Text>
          <Button onClick={() => void auth.signoutRedirect()}>Logout</Button>
        </Flex>
      ) : (
        <Link onClick={() => void auth.signinRedirect()}>Log in</Link>
      )}
    </Flex>
  );
};
