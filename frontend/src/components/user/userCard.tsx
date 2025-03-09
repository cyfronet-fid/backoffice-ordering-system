import { UserPublicWithEmployers } from "@/client";
import { RoleTag } from "@/components/common/roleTag.tsx";
import { Box, Flex, Table, Tag, Tbody, Td, Tr } from "@chakra-ui/react";
import { Link as RouterLink } from "@tanstack/react-router";

interface Props {
  user: UserPublicWithEmployers;
}

export function UserCard({ user }: Props) {
  const renderEmployers = () => {
    if (user.user_type.includes("provider_manager")) {
      return (
        <Tr>
          <Td fontWeight="bold">Employers</Td>
          <Td>
            <Flex gap={"2"}>
              {user.employers?.length ? (
                user.employers.map((provider) => (
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
                <div>No employers!</div>
              )}
            </Flex>
          </Td>
        </Tr>
      );
    }
    return undefined;
  };

  return (
    <Box p={6} boxShadow="md" borderRadius="md" bg="white">
      <Flex justify="space-between" align="center" mb={4}>
        <Box fontSize="lg" fontWeight="bold">
          User
        </Box>
        <Box>
          <Flex gap={"2"}>
            {user.user_type.map((role) => (
              <RoleTag key={`${user.id}-${role}`} role={role} />
            ))}
          </Flex>
        </Box>
      </Flex>

      <Table size="sm" variant="simple">
        <Tbody>
          <Tr>
            <Td fontWeight="bold">ID</Td>
            <Td>{user.id}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Name</Td>
            <Td>{user.name}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Email</Td>
            <Td>{user.email}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Created at</Td>
            <Td>{user.created_at}</Td>
          </Tr>
          <Tr>
            <Td fontWeight="bold">Updated at</Td>
            <Td>{user.updated_at}</Td>
          </Tr>
          {renderEmployers()}
        </Tbody>
      </Table>
    </Box>
  );
}
