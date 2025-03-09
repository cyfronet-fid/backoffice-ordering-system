import { OrderStatus } from "@/client";
import { humanReadableStatus } from "@/const.ts";
import { Badge } from "@chakra-ui/react";
import { ReactElement } from "react";

interface Props {
  status?: OrderStatus;
}

export function StatusTag({ status }: Props) {
  const tagMap: Record<OrderStatus, ReactElement> = {
    cancelled: (
      <Badge colorScheme="red">{humanReadableStatus["cancelled"]}</Badge>
    ),
    completed: (
      <Badge colorScheme="green">{humanReadableStatus["completed"]}</Badge>
    ),
    on_hold: (
      <Badge colorScheme="yellow">{humanReadableStatus["on_hold"]}</Badge>
    ),
    processing: (
      <Badge colorScheme="blue">{humanReadableStatus["processing"]}</Badge>
    ),
    rejected: (
      <Badge colorScheme="purple">{humanReadableStatus["rejected"]}</Badge>
    ),
    submitted: (
      <Badge colorScheme={"gray"}>{humanReadableStatus["submitted"]}</Badge>
    ),
  };

  if (status) {
    return tagMap[status];
  }

  return <Badge>Unknown</Badge>;
}
