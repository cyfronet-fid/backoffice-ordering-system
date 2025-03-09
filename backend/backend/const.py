from backend.models.tables import OrderStatus

ORDER_STATUS_STATE_MACHINE: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.CANCELLED: [],
    OrderStatus.COMPLETED: [],
    OrderStatus.ON_HOLD: [OrderStatus.PROCESSING],
    OrderStatus.PROCESSING: [OrderStatus.COMPLETED, OrderStatus.REJECTED, OrderStatus.ON_HOLD],
    OrderStatus.REJECTED: [],
    OrderStatus.SUBMITTED: [OrderStatus.PROCESSING, OrderStatus.ON_HOLD, OrderStatus.CANCELLED],
}
