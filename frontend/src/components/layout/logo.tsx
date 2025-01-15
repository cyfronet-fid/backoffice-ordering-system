import { Box, Text, Divider } from "@chakra-ui/react";
import { Link } from "@tanstack/react-router";

export function Logo() {
  return (
    <Link to={"/"}>
      <Box textAlign="center">
        <Text fontSize="2xl" fontWeight="bold" color="blue.900">
          BOS
        </Text>
        <Divider borderColor="gray.300" maxWidth="80px" mx="auto" mt="1" />
        <Text fontSize="sm" color="gray.600" mt="2">
          manage your orders
        </Text>
      </Box>
    </Link>
  );
}
