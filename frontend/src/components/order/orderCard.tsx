import { OrderPublicWithDetails } from "@/client";
import { StatusTag } from "@/components/common/statusTag.tsx";
import { getMpUser, snakeToTitle } from "@/utils.ts";
import {
  Box,
  Code,
  Flex,
  Link,
  Table,
  Tag,
  Tbody,
  Td,
  Tr,
} from "@chakra-ui/react";
import { Link as RouterLink } from "@tanstack/react-router";

interface Props {
  order: OrderPublicWithDetails;
}

export function OrderCard({ order }: Props) {
  const mpUser = getMpUser(order.users);
  const manager = order.users?.find((user) =>
    user.user_type?.includes("provider_manager"),
  );

  return (
    <Box p={6} boxShadow="md" borderRadius="md" bg="white">
      <Flex justify="space-between" align="center" mb={4}>
        <Box fontSize="lg" fontWeight="bold">
          Order
        </Box>
        <Box>
          Status <StatusTag status={order.status} />
        </Box>
      </Flex>

      <Table size="sm" variant="simple">
        <Tbody>
          <Tr>
            <Td fontWeight="bold">Providers</Td>
            <Td>
              {order.providers && order.providers.length > 0 ? (
                order.providers.map((provider) => (
                  <Tag
                    as={RouterLink}
                    colorScheme="gray"
                    to={`/providers/${provider.id}`}
                    key={provider.id}
                  >
                    {provider.name}
                  </Tag>
                ))
              ) : (
                <Tag colorScheme="gray">No Providers</Tag>
              )}
            </Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">User</Td>
            <Td>
              {mpUser ? (
                <Tag
                  as={RouterLink}
                  colorScheme="gray"
                  to={`/users/${mpUser.id}`}
                  key={mpUser.id}
                >
                  {mpUser.name}
                </Tag>
              ) : (
                "-"
              )}
            </Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Access Type</Td>
            <Td>{snakeToTitle(order.resource_type)}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Product</Td>
            <Td>{order.resource_name}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Source</Td>
            <Td>EOSC Marketplace</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Contact</Td>
            <Td>
              {manager?.email ? (
                <Link
                  href={`mailto:${manager.email}`}
                  color="blue.500"
                  isExternal
                >
                  {manager.email}
                </Link>
              ) : (
                "-"
              )}
            </Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Resource reference</Td>
            <Td>
              <Code>{order.resource_ref}</Code>
            </Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Config</Td>
            <Td>
              <Code
                p={2}
                maxW="100%"
                whiteSpace="pre-wrap"
                display="block"
                overflowX="auto"
              >
                {order.config
                  ? JSON.stringify(order.config, null, 2)
                  : "No Config Available"}
              </Code>
            </Td>
          </Tr>
        </Tbody>
      </Table>
    </Box>
  );
}
