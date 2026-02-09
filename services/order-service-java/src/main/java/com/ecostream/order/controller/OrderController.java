package com.ecostream.order.controller;

import com.ecostream.order.dto.OrderRequestDTO;
import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.dto.UpdateOrderRequestDTO;
import com.ecostream.order.service.OrderService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * REST controller for order management operations.
 * Provides CRUD endpoints for the Order Service.
 */
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Slf4j
public class OrderController {

    private final OrderService orderService;

    /**
     * Creates a new order.
     *
     * @param request the order creation request
     * @return the created order with 201 Created status
     */
    @PostMapping
    public ResponseEntity<OrderResponseDTO> createOrder(@Valid @RequestBody OrderRequestDTO request) {
        log.info("Received request to create new order with priority: {}", request.getPriority());
        
        OrderResponseDTO response = orderService.createOrder(request);
        
        log.debug("Order created successfully with ID: {}", response.getId());
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Retrieves an order by its unique identifier.
     *
     * @param id the UUID of the order to retrieve
     * @return the order with 200 OK status if found, 404 Not Found otherwise
     */
    @GetMapping("/{id}")
    public ResponseEntity<OrderResponseDTO> getOrderById(@PathVariable UUID id) {
        log.debug("Received request to retrieve order with ID: {}", id);
        
        Optional<OrderResponseDTO> orderOptional = orderService.getOrderById(id);
        
        if (orderOptional.isEmpty()) {
            log.debug("Order not found with ID: {}", id);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
        
        log.debug("Order retrieved successfully with ID: {}", id);
        return ResponseEntity.ok(orderOptional.get());
    }

    /**
     * Retrieves all orders in the system.
     *
     * @return list of all orders with 200 OK status
     */
    @GetMapping
    public ResponseEntity<List<OrderResponseDTO>> getAllOrders() {
        log.debug("Received request to retrieve all orders");
        
        List<OrderResponseDTO> orders = orderService.getAllOrders();
        
        log.debug("Retrieved {} orders", orders.size());
        return ResponseEntity.ok(orders);
    }

    /**
     * Updates an existing order.
     *
     * @param id the UUID of the order to update
     * @param request the order update request
     * @return the updated order with 200 OK status if found, 404 Not Found otherwise
     */
    @PutMapping("/{id}")
    public ResponseEntity<OrderResponseDTO> updateOrder(
            @PathVariable UUID id,
            @Valid @RequestBody UpdateOrderRequestDTO request) {
        log.debug("Received request to update order with ID: {}", id);
        
        Optional<OrderResponseDTO> orderOptional = orderService.updateOrder(id, request);
        
        if (orderOptional.isEmpty()) {
            log.debug("Order not found with ID: {}", id);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
        
        log.debug("Order updated successfully with ID: {}", id);
        return ResponseEntity.ok(orderOptional.get());
    }
}
