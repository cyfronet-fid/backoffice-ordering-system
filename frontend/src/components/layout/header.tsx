import { Flex, Text } from "@chakra-ui/react";

import { UserIcon } from "../common/icons/userIcon.tsx";
import { Logo } from "./logo.tsx";

export const Header = () => (
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
      <Text>Patryk Wójtowicz</Text>
    </Flex>
  </Flex>
);
