import {
  changeOrderStatus,
  getOrderById,
  getOrderMessages,
  OrderStatus,
} from "@/client";
import { NotFound } from "@/components/common/notFound.tsx";
import { StatusTag } from "@/components/common/statusTag.tsx";
import { ConversationThread } from "@/components/order/conversationThread.tsx";
import { OrderCard } from "@/components/order/orderCard.tsx";
import { humanReadableStatus, orderStatusStateMachine } from "@/const.ts";
import { getAuthorizationHeader } from "@/utils.ts";
import {
  Box,
  Button,
  Flex,
  Heading,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Select,
  Stack,
  useDisclosure,
  useToast,
} from "@chakra-ui/react";
import {
  createFileRoute,
  Link as RouterLink,
  useRouter,
} from "@tanstack/react-router";
import { useState } from "react";
import { useAuth } from "react-oidc-context";

export const Route = createFileRoute("/_authenticated/orders/$orderId")({
  component: RouteComponent,
  loader: async ({ context, params }) => {
    const payload = {
      headers: { ...getAuthorizationHeader(context.auth) },
      path: { order_id: Number(params.orderId) },
    };

    // Parallel calls
    const [orderData, orderMessageData] = await Promise.all([
      getOrderById(payload),
      getOrderMessages(payload),
    ]);

    return {
      order: orderData.data!,
      messages: orderMessageData.data!,
    };
  },
});

function RouteComponent() {
  const auth = useAuth();
  const router = useRouter();
  const toast = useToast();

  const { order, messages } = Route.useLoaderData();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [newStatus, setNewStatus] = useState<OrderStatus | undefined>(
    undefined,
  );
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleOrderStatusChange = async () => {
    try {
      setIsSubmitting(true);
      await changeOrderStatus({
        headers: { ...getAuthorizationHeader(auth) },
        path: { order_id: order.id },
        query: { new_status: newStatus! },
      });
      toast({
        title: "Updated the order status!",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      handleClose();

      // Invalidate the current route to see new order status
      router.invalidate();
    } catch (error) {
      toast({
        title: "Failed to change order status!",
        description: String(error),
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setNewStatus(undefined);
      onClose();
    }
  };

  if (!order) {
    return <NotFound />;
  }

  return (
    <Box p={6}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading>{`Order > ${order.id}`}</Heading>
        <Flex gap={"2"}>
          <Button
            colorScheme={"red"}
            onClick={onOpen}
            disabled={orderStatusStateMachine[order.status!].length === 0}
          >
            Change order status
          </Button>
          <Button as={RouterLink} to={"/orders"} variant="outline">
            Back to orders
          </Button>
        </Flex>
      </Flex>

      <Flex gap={6} align="flex-start">
        <Box flex="1">
          <OrderCard order={order} />
        </Box>

        <Box flex="1">
          <ConversationThread messages={messages} orderId={order.id} />
        </Box>
      </Flex>

      <Modal isOpen={isOpen} onClose={handleClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>You're changing the order status...</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack gap={2}>
              <Box>
                Current status: <StatusTag status={order.status} />
              </Box>
              <Select
                placeholder={"choose new status..."}
                value={newStatus}
                isDisabled={isSubmitting}
                onChange={(e) => setNewStatus(e.target.value as OrderStatus)}
              >
                {orderStatusStateMachine[order.status!].map((status) => (
                  <option key={status} value={status}>
                    {humanReadableStatus[status]}
                  </option>
                ))}
              </Select>
            </Stack>
          </ModalBody>

          <ModalFooter>
            <Flex gap={2}>
              <Button
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                colorScheme="blue"
                mr={3}
                isLoading={isSubmitting}
                disabled={!newStatus}
                onClick={handleOrderStatusChange}
              >
                Confirm
              </Button>
            </Flex>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}
