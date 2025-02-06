import { Box, Spinner, Text, VStack } from "@chakra-ui/react";

export const FullScreenSpinner = () => {
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
      <VStack spacing={4}>
        <Spinner size="xl" />
        <Text fontSize="lg" color="gray.600" fontWeight="medium">
          Loading...
        </Text>
      </VStack>
    </Box>
  );
};
