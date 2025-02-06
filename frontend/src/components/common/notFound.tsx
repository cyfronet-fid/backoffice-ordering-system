import { Box, Link, Text, VStack } from "@chakra-ui/react";
import { Link as RouterLink } from "@tanstack/react-router";

export const NotFound = () => {
  return (
    <Box
      position="fixed"
      top="0"
      left="0"
      width="100vw"
      height="100vh"
      display="flex"
      justifyContent="center"
      alignItems="center"
      bg="whiteAlpha.900"
      zIndex="9999"
    >
      <VStack spacing={6}>
        <Text fontSize="2xl" fontWeight="bold" color="gray.700">
          404 - Page Not Found
        </Text>
        <Text fontSize="md" color="gray.500">
          The page you’re looking for doesn’t exist.
        </Text>
        <Link as={RouterLink} to={"/"} colorScheme="blue" size="lg">
          Go Back to Home
        </Link>
      </VStack>
    </Box>
  );
};
