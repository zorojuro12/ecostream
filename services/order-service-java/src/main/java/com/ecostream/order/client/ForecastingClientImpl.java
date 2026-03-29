package com.ecostream.order.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.UUID;

/**
 * RestTemplate-based client for the AI Forecasting Service.
 * Protected by a Resilience4j circuit breaker: after repeated failures
 * the circuit opens and the fallback returns null (graceful degradation).
 */
@Component
@Slf4j
public class ForecastingClientImpl implements ForecastingClient {

    private final String baseUrl;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public ForecastingClientImpl(
            @Value("${ai.forecasting.base-url:http://localhost:5050}") String baseUrl,
            RestTemplate restTemplate,
            ObjectMapper objectMapper) {
        this.baseUrl = baseUrl;
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    @Override
    @CircuitBreaker(name = "forecastService", fallbackMethod = "forecastFallback")
    public ForecastResponseDTO getForecast(UUID orderId, Double destinationLatitude,
                                           Double destinationLongitude, String priority) {
        String url = baseUrl + "/api/forecast/" + orderId.toString();
        ForecastRequestDTO body = new ForecastRequestDTO(
                destinationLatitude,
                destinationLongitude,
                priority != null ? priority : "Standard"
        );
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        String jsonBody;
        try {
            jsonBody = objectMapper.writeValueAsString(body);
        } catch (Exception e) {
            throw new RuntimeException("Failed to serialize forecast request", e);
        }
        HttpEntity<String> entity = new HttpEntity<>(jsonBody, headers);
        ResponseEntity<ForecastResponseDTO> response =
                restTemplate.exchange(url, HttpMethod.POST, entity, ForecastResponseDTO.class);
        return response.getBody();
    }

    /** Fallback invoked when the circuit is open or the remote call fails. */
    @SuppressWarnings("unused")
    private ForecastResponseDTO forecastFallback(UUID orderId, Double destinationLatitude,
                                                 Double destinationLongitude, String priority,
                                                 Throwable t) {
        log.warn("Circuit breaker fallback for order {}: {}", orderId, t.getMessage());
        return null;
    }
}
