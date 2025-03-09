import { ProviderPublicWithDetails } from "@/client";
import { Box, Flex, Link, Table, Tag, Tbody, Td, Tr } from "@chakra-ui/react";
import { Link as RouterLink } from "@tanstack/react-router";

interface Props {
  provider: ProviderPublicWithDetails;
}

export function ProviderCard({ provider }: Props) {
  return (
    <Box p={6} boxShadow="md" borderRadius="md" bg="white">
      <Flex justify="space-between" align="center" mb={4}>
        <Box fontSize="lg" fontWeight="bold">
          Provider
        </Box>
      </Flex>

      <Table size="sm" variant="simple">
        <Tbody>
          <Tr>
            <Td fontWeight="bold">Name</Td>
            <Td>{provider.name}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Contact</Td>
            <Td>
              {provider.website ? (
                <Link color="blue.500" href={provider.website} isExternal>
                  {provider.website}
                </Link>
              ) : (
                "No website available"
              )}
            </Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Created at</Td>
            <Td>{provider.created_at}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Managers</Td>
            <Td>
              <Flex gap={"2"}>
                {provider.managers && provider.managers.length > 0 ? (
                  provider.managers?.map((manager) => (
                    <Tag
                      as={RouterLink}
                      colorScheme="gray"
                      to={`/users/${manager.id}`}
                      key={manager.id}
                    >
                      {manager.name}
                    </Tag>
                  ))
                ) : (
                  <div>No managers!</div>
                )}
              </Flex>
            </Td>
          </Tr>
        </Tbody>
      </Table>
    </Box>
  );
}
