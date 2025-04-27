from backend.models.tables import OrderStatus

ORDER_STATUS_STATE_MACHINE: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.CANCELLED: [],
    OrderStatus.COMPLETED: [],
    OrderStatus.ON_HOLD: [OrderStatus.PROCESSING],
    OrderStatus.PROCESSING: [OrderStatus.COMPLETED, OrderStatus.REJECTED, OrderStatus.ON_HOLD],
    OrderStatus.REJECTED: [],
    OrderStatus.SUBMITTED: [OrderStatus.PROCESSING, OrderStatus.ON_HOLD, OrderStatus.CANCELLED],
}

WHITELABEL_ORDER_STATUS_MAPPING: dict[OrderStatus, str] = {
    OrderStatus.SUBMITTED: "registered",
    OrderStatus.ON_HOLD: "waiting_for_response",
    OrderStatus.PROCESSING: "in_progress",
    OrderStatus.COMPLETED: "ready",
    OrderStatus.REJECTED: "rejected",
    OrderStatus.CANCELLED: "rejected",
}
