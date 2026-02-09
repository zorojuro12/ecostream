package com.ecostream.order.service;

import com.ecostream.order.dto.LocationDTO;
import com.ecostream.order.dto.OrderRequestDTO;
import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.entity.Order;
import com.ecostream.order.entity.OrderStatus;
import com.ecostream.order.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Implementation of OrderService interface.
 * Provides business logic for order management operations.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderServiceImpl implements OrderService {

    private final OrderRepository orderRepository;

    /**
     * Creates a new order from the provided request DTO.
     * Sets the order status to PENDING regardless of the status in the request.
     *
     * @param request the order creation request containing status, destination, and priority
     * @return the created order as an OrderResponseDTO
     */
    @Override
    public OrderResponseDTO createOrder(OrderRequestDTO request) {
        log.debug("Creating new order with priority: {}", request.getPriority());

        // Map DTO to Entity, setting status to PENDING
        Order order = Order.builder()
                .status(OrderStatus.PENDING) // Always set to PENDING for new orders
                .destinationLatitude(request.getDestination().getLatitude())
                .destinationLongitude(request.getDestination().getLongitude())
                .priority(request.getPriority())
                .build();

        // Save order to database
        Order savedOrder = orderRepository.save(order);
        log.info("Order created successfully with ID: {}", savedOrder.getId());

        // Map Entity to Response DTO
        return mapToResponseDTO(savedOrder);
    }

    @Override
    public Optional<OrderResponseDTO> getOrderById(UUID id) {
        log.debug("Retrieving order with ID: {}", id);
        
        Optional<Order> orderOptional = orderRepository.findById(id);
        
        if (orderOptional.isEmpty()) {
            log.debug("Order not found with ID: {}", id);
            return Optional.empty();
        }
        
        Order order = orderOptional.get();
        log.info("Order retrieved successfully with ID: {}", id);
        return Optional.of(mapToResponseDTO(order));
    }

    @Override
    public List<OrderResponseDTO> getAllOrders() {
        log.debug("Retrieving all orders");
        
        List<Order> orders = orderRepository.findAll();
        log.info("Retrieved {} orders", orders.size());
        
        return orders.stream()
                .map(this::mapToResponseDTO)
                .toList();
    }

    @Override
    public Optional<OrderResponseDTO> updateOrder(UUID id, OrderRequestDTO request) {
        // TODO: Implement in next iteration
        throw new UnsupportedOperationException("Not yet implemented");
    }

    @Override
    public boolean deleteOrder(UUID id) {
        // TODO: Implement in next iteration
        throw new UnsupportedOperationException("Not yet implemented");
    }

    /**
     * Maps an Order entity to an OrderResponseDTO.
     *
     * @param order the Order entity to map
     * @return the mapped OrderResponseDTO
     */
    private OrderResponseDTO mapToResponseDTO(Order order) {
        LocationDTO locationDTO = LocationDTO.builder()
                .latitude(order.getDestinationLatitude())
                .longitude(order.getDestinationLongitude())
                .build();

        return OrderResponseDTO.builder()
                .id(order.getId())
                .status(order.getStatus())
                .destination(locationDTO)
                .priority(order.getPriority())
                .build();
    }
}
