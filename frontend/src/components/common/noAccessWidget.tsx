import bg from "@/assets/no_access_bg.png";
import { Header } from "@/components/layout/header.tsx";
import {
  Box,
  Button,
  Flex,
  Heading,
  Text,
  VStack,
  HStack,
} from "@chakra-ui/react";

interface NoAccessWidgetProps {
  userName?: string;
}

export function NoAccessWidget({ userName }: NoAccessWidgetProps) {
  return (
    <Flex direction="column" h="100vh" w="100vw">
      <Box h="80px">
        <Header headerBackgroundColor="white" userName={userName} />
      </Box>

      <Flex
        flex="1"
        bgImage={`url(${bg})`}
        bgSize="cover"
        bgPosition="30% center"
        position="relative"
        justify="center"
      >
        <Flex
          position="relative"
          w="100%"
          justify="center"
          pt="120px"
          maxHeight="400px"
        >
          <Box
            bg="#F5F6F8"
            p="10"
            borderRadius="lg"
            boxShadow="xl"
            maxW="600px"
            textAlign="center"
          >
            <VStack spacing={7}>
              <Heading size="md" color="#010E87" lineHeight="1.4">
                Become a provider to continue
              </Heading>

              <Box maxW="400px">
                <Text fontSize="md" color="gray.600">
                  The Back Office Ordering System is available to Marketplace
                  Providers only.
                  <br />
                  Become a Provider to continue.
                </Text>
              </Box>

              <HStack spacing={10} pt={4}>
                <Button
                  variant="outline"
                  backgroundColor="#EDF4FF"
                  color="#010E87"
                  borderColor="#010E87"
                  borderWidth="2px"
                  w="210px"
                  onClick={() =>
                    (window.location.href =
                      import.meta.env.VITE_MARKETPLACE_URL ||
                      "https://marketplace.docker-fid.grid.cyf-kr.edu.pl/")
                  }
                >
                  Go back to Marketplace
                </Button>

                <Button
                  color={"white"}
                  bgColor="#010E87"
                  w="210px"
                  onClick={() =>
                    (window.location.href =
                      import.meta.env.VITE_BECOME_PROVIDER_URL ||
                      "https://marketplace.docker-fid.grid.cyf-kr.edu.pl/backoffice/providers/new/wizard")
                  }
                >
                  Become a Provider
                </Button>
              </HStack>
            </VStack>
          </Box>
        </Flex>
      </Flex>
    </Flex>
  );
}
