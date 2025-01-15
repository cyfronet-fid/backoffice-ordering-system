import { Alert, AlertIcon } from "@chakra-ui/react";

interface Props {
  error: Error;
}
export function DefaultError({ error }: Props) {
  return (
    <Alert status="error">
      <AlertIcon />
      {error.message}
    </Alert>
  );
}
