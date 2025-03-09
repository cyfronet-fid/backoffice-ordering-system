import { OrderPublicWithProviders } from "@/client";
import { StatusTag } from "@/components/common/statusTag.tsx";
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
  order: OrderPublicWithProviders;
}
export function OrderCard({ order }: Props) {
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
            <Td fontWeight="bold">Product Type</Td>
            <Td>Unknown</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Access Type</Td>
            <Td>Unknown</Td>
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
              {order.providers &&
              order.providers.length > 0 &&
              order.providers[0].website ? (
                <Link
                  href={order.providers[0].website}
                  color="blue.500"
                  isExternal
                >
                  {order.providers[0].website}
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
            <Td fontWeight="bold">External reference</Td>
            <Td>
              <Code>{order.external_ref}</Code>
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
