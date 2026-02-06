package com.ecostream.order.controller;

import com.ecostream.order.dto.OrderRequestDTO;
import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.service.OrderService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

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
}
