import { createMessage, MessagePublic } from "@/client";
import { RoleTag } from "@/components/common/roleTag.tsx";
import { getAuthorizationHeader } from "@/utils.ts";
import {
  Box,
  Button,
  Checkbox,
  Flex,
  Link,
  Textarea,
  useToast,
} from "@chakra-ui/react";
import { Link as RouterLink, useRouter } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { useAuth } from "react-oidc-context";

interface Props {
  messages: MessagePublic[];
  orderId: number;
}

export function ConversationThread({ messages, orderId }: Props) {
  const auth = useAuth();
  const router = useRouter();
  const toast = useToast();

  const [messageValue, setMessageValue] = useState<string>("");
  const [sendToUser, setSendToUser] = useState<boolean>(false);
  const [isMessageSubmitting, setMessageSubmitting] = useState<boolean>(false);

  const messageBoxRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messageBoxRef.current?.lastElementChild?.scrollIntoView({
      behavior: "smooth",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    try {
      setMessageSubmitting(true);
      await createMessage({
        headers: { ...getAuthorizationHeader(auth) },
        body: {
          content: messageValue,
          order_id: orderId,
          scope: sendToUser ? "public" : "private",
        },
      });
      toast({
        title: "Message sent!",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      setMessageValue("");
      setSendToUser(false);

      // Invalidate the current route to reload messages
      router.invalidate();
    } catch (error) {
      toast({
        title: "Failed to send the message!",
        description: String(error),
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    } finally {
      setMessageSubmitting(false);
    }
  };

  return (
    <>
      <Box pb="2" fontSize="lg" fontWeight="bold">
        Order timeline
      </Box>
      <Box p={6} boxShadow="md" borderRadius="md" bg="blue.50">
        <Flex
          direction="column"
          gap={4}
          maxH="400px"
          overflowY="auto"
          ref={messageBoxRef}
        >
          {messages && messages.length > 0 ? (
            messages.map((message) => (
              <Box
                key={message.id}
                p={4}
                borderRadius="2xl"
                boxShadow="sm"
                bg="white"
                maxW="80%"
              >
                <Box fontSize="sm" fontWeight="bold" mb={1}>
                  <Link as={RouterLink} to={`/users/${message.author.id}`}>
                    {message.author.email === auth.user?.profile.email ? (
                      "You"
                    ) : (
                      <>
                        {message.author.name} {/*TODO: Add roles list*/}
                        <RoleTag role={message.author?.user_type[0]} />
                      </>
                    )}
                  </Link>
                </Box>

                <Box fontSize="md">{message.content}</Box>
                <Box fontSize="xs" color="gray.500" mt={2}>
                  {new Date(message.created_at!).toLocaleString() +
                    (message.scope == "public" &&
                    !message.author?.user_type.includes("mp_user")
                      ? " (sent to the user)"
                      : "")}
                </Box>
              </Box>
            ))
          ) : (
            <div>No messages!</div>
          )}
        </Flex>
      </Box>
      <Flex my={4} gap={2}>
        <Textarea
          value={messageValue}
          onChange={(e) => setMessageValue(e.target.value)}
          placeholder="Type a message..."
          flex="1"
          resize="none"
        />
        <Button
          isLoading={isMessageSubmitting}
          isDisabled={messageValue.length === 0}
          onClick={handleSendMessage}
          bg="blue.900"
          textColor={"white"}
        >
          Send message
        </Button>
      </Flex>

      <Checkbox
        isDisabled={isMessageSubmitting}
        isChecked={sendToUser}
        onChange={() => setSendToUser(!sendToUser)}
      >
        Send message to the user
      </Checkbox>
    </>
  );
}
