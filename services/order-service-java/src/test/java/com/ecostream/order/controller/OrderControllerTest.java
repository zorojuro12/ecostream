package com.ecostream.order.controller;

import com.ecostream.order.dto.LocationDTO;
import com.ecostream.order.dto.OrderRequestDTO;
import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.entity.OrderStatus;
import com.ecostream.order.service.OrderService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Unit tests for OrderController.
 * Tests follow TDD Red-Green-Refactor workflow.
 */
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void createOrder_ShouldReturn201Created() throws Exception {
        // Arrange: Create request DTO
        LocationDTO locationDTO = LocationDTO.builder()
                .latitude(37.7749)
                .longitude(-122.4194)
                .build();

        OrderRequestDTO requestDTO = OrderRequestDTO.builder()
                .status(OrderStatus.CONFIRMED)
                .destination(locationDTO)
                .priority(5)
                .build();

        // Arrange: Create response DTO
        UUID orderId = UUID.randomUUID();
        OrderResponseDTO responseDTO = OrderResponseDTO.builder()
                .id(orderId)
                .status(OrderStatus.PENDING)
                .destination(locationDTO)
                .priority(5)
                .build();

        // Arrange: Mock service to return response DTO
        when(orderService.createOrder(any(OrderRequestDTO.class))).thenReturn(responseDTO);

        // Act & Assert: POST request and verify 201 Created response
        mockMvc.perform(post("/api/orders")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(requestDTO)))
                .andExpect(status().isCreated())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.id").value(orderId.toString()))
                .andExpect(jsonPath("$.status").value("PENDING"))
                .andExpect(jsonPath("$.destination.latitude").value(37.7749))
                .andExpect(jsonPath("$.destination.longitude").value(-122.4194))
                .andExpect(jsonPath("$.priority").value(5));
    }
}
