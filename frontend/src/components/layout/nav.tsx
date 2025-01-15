import { VStack, Flex, Text, Box } from "@chakra-ui/react";
import { Link as RouterLink } from "@tanstack/react-router";

import { OrdersIcon } from "../common/icons/ordersIcon.tsx";
import { ProvidersIcon } from "../common/icons/providersIcon.tsx";
import { UsersIcon } from "../common/icons/usersIcon.tsx";

export const Nav = () => (
  <VStack spacing="2" align="stretch" p="4" height="100%">
    <Box
      as={RouterLink}
      to={"/orders"}
      borderRadius={"md"}
      p={1}
      activeProps={{
        style: {
          backgroundColor: "#EDF4FF",
          color: "#010E87",
        },
      }}
    >
      <Flex align="center" gap={2}>
        <OrdersIcon />
        <Text>Orders</Text>
      </Flex>
    </Box>
    <Box
      as={RouterLink}
      to={"/users"}
      borderRadius={"md"}
      p={1}
      activeProps={{
        style: {
          backgroundColor: "#EDF4FF",
          color: "#010E87",
        },
      }}
    >
      <Flex align="center" gap={2}>
        <UsersIcon />
        <Text>Users</Text>
      </Flex>
    </Box>
    <Box
      as={RouterLink}
      to={"/providers"}
      borderRadius={"md"}
      p={1}
      activeProps={{
        style: {
          backgroundColor: "#EDF4FF",
          color: "#010E87",
        },
      }}
    >
      <Flex align="center" gap={2}>
        <ProvidersIcon />
        <Text>Providers</Text>
      </Flex>
    </Box>
    <Box mt={"auto"}>
      <Flex align="center" gap={2}>
        <ProvidersIcon />
        <Text>Settings</Text>
      </Flex>
    </Box>
  </VStack>
);
