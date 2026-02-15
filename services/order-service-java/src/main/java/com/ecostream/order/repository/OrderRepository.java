package com.ecostream.order.repository;

import com.ecostream.order.entity.Order;
import com.ecostream.order.entity.OrderStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

/**
 * Repository interface for Order entity.
 * Provides CRUD operations and custom query methods for order management.
 */
@Repository
public interface OrderRepository extends JpaRepository<Order, UUID> {

    /**
     * Find all orders with a specific status.
     * @param status The order status to filter by
     * @return List of orders matching the status
     */
    List<Order> findByStatus(OrderStatus status);

    /**
     * Find all orders ordered by priority (descending).
     * @return List of orders sorted by priority
     */
    List<Order> findAllByOrderByPriorityDesc();
}
