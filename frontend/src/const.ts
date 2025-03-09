import { OrderStatus } from "@/client";

export const orderStatusStateMachine: Record<OrderStatus, OrderStatus[]> = {
  cancelled: [],
  completed: [],
  on_hold: ["processing"],
  processing: ["completed", "rejected", "on_hold"],
  rejected: [],
  submitted: ["processing", "on_hold", "cancelled"],
};

export const humanReadableStatus: Record<OrderStatus, string> = {
  cancelled: "Cancelled",
  completed: "Completed",
  on_hold: "On hold",
  processing: "Processing",
  rejected: "Rejected",
  submitted: "Submitted",
};
